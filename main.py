import os
import glob
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from dotenv import load_dotenv

load_dotenv()

from graph import build_cv_extractor_graph, GraphState

def main():
    # Verificar diretório de entrada
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"Diretório {input_dir} não encontrado. Criando...")
        os.makedirs(input_dir)
        return
        
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado em {input_dir}")
        return

    print(f"Encontrados {len(pdf_files)} CVs para processar.")
    
    # Inicializar checkpointer silenciando os avisos de deserialização do Msgpack
    memory = MemorySaver(
        serde=JsonPlusSerializer(
            allowed_msgpack_modules=[
                ("schema", "CandidateExtraction"),
                ("schema", "CandidateEvaluation")
            ]
        )
    )
    
    # Construir e compilar o grafo
    builder = build_cv_extractor_graph()
    
    # Interrompemos antes do human_review_node para que a execução pause se a validação falhar
    graph = builder.compile(checkpointer=memory, interrupt_before=["human_review_node"])
    
    # Gerar e salvar a imagem do grafo
    try:
        img_bytes = graph.get_graph().draw_mermaid_png()
        with open("graph_image.png", "wb") as f:
            f.write(img_bytes)
        print("Imagem do grafo salva como 'graph_image.png'")
    except Exception as e:
        print(f"Aviso: Não foi possível gerar a imagem do grafo: {e}")
        
    # Processar cada CV
    for idx, pdf_path in enumerate(pdf_files):
        print(f"\n--- Processando CV {idx+1}/{len(pdf_files)}: {pdf_path} ---")
        file_name = os.path.basename(pdf_path)
        
        # Usamos o caminho do arquivo como thread_id para rastreamento de estado único por CV
        thread_config = {"configurable": {"thread_id": file_name}}
        
        initial_state = GraphState(
            cv_path=pdf_path,
            cv_file_name=file_name,
            raw_text="",
            extracted_data=None,
            is_valid=False,
            evaluated_data=None,
            error_message=None
        )
        
        # Executar o grafo
        for event in graph.stream(initial_state, config=thread_config, stream_mode="values"):
            pass # Esgotar o stream
            
        # Verificar se está pausado (interrompido)
        current_state = graph.get_state(thread_config)
        if current_state.next:
            print(f"⚠️ Execução de {file_name} pausada nos nós: {current_state.next}")
            print("Você pode investigar o estado ou retomar manualmente depois.")
            error_msg = current_state.values.get("error_message")
            if error_msg:
                print(f"🛑 Motivo de la pausa: {error_msg}")
        else:
            final_data = current_state.values.get('evaluated_data')
            err = current_state.values.get('error_message')
            if err:
                print(f"Concluído com erros: {err}")
            elif final_data:
                print(f"Processado e exportado com sucesso {file_name}.")

if __name__ == "__main__":
    main()
