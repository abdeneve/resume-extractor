import os
import datetime
import uuid
from typing import TypedDict, Optional, Annotated

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import pypdf
import pandas as pd
from langgraph.graph import StateGraph, START, END

from schema import CandidateExtraction, CandidateEvaluation, CRMRecord

# --- Definição do Estado ---
class GraphState(TypedDict):
    """O estado do LangGraph."""
    cv_path: str
    cv_file_name: str
    raw_text: str
    extracted_data: Optional[CandidateExtraction]
    is_valid: bool
    evaluated_data: Optional[CandidateEvaluation]
    error_message: Optional[str]

# --- Nós ---

def ingest_pdf(state: GraphState) -> GraphState:
    """Lê o arquivo PDF e extrai o texto."""
    path = state["cv_path"]
    text = ""
    try:
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Salvar texto bruto em output/raw
        os.makedirs("output/raw", exist_ok=True)
        base_name = os.path.splitext(state["cv_file_name"])[0]
        raw_filepath = os.path.join("output/raw", f"{base_name}_raw.txt")
        with open(raw_filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        return {"raw_text": text}
    except Exception as e:
        return {"error_message": f"Erro ao ler o PDF: {e}", "is_valid": False}

def extractor_node(state: GraphState) -> GraphState:
    """Usa o Qwen3.5:4b local via Ollama para extrair dados estruturados."""
    text = state["raw_text"]
    if not text:
        return {"error_message": "Nenhum texto extraído", "is_valid": False}
    
    model_name = "phi3:mini"
    print(f"--- Iniciando extração de currículo. Modelo em uso: {model_name} ---")
    llm = ChatOllama(
        model=model_name, #"qwen3.5:4b", 
        temperature=0.0,
        #num_predict=4000,  # Aumentado para acomodar o tamanho grande do JSON de saída
    )
    
    # Usar with_structured_output
    structured_llm = llm.with_structured_output(CandidateExtraction)
    
    try:
        result = structured_llm.invoke([
            SystemMessage(content=(
                "You are an expert technical recruiter. "
                "Extract the requested fields from the following CV and return ONLY a valid JSON object. "
                "Do not include markdown tags like ```json. Do not include any conversational text. "
                "Ensure all required fields are filled to the best of your ability based on the text. "
                "If a field is not present, use null or an empty list as appropriate. "
                "The CVs will always be in Portuguese. Your extracted text values MUST be in Brazilian Portuguese (pt-BR)."
            )),
            HumanMessage(content=f"CV Text:\n{text}")
        ])
        
        # Validação simples: se obtivermos pelo menos um nome completo, consideramos válido.
        if isinstance(result, dict):
            # Às vezes, a saída estruturada via Ollama retorna dict diretamente se usar tipos de chain mais antigos
           full_name = result.get("full_name")
        else:
           full_name = result.full_name
           
        if full_name and len(full_name.strip()) > 0:
            return {"extracted_data": result, "is_valid": True, "error_message": None}
        else:
            return {"extracted_data": result, "is_valid": False, "error_message": "Falha na validação: Não foi possível extrair o nome completo."}
            
    except Exception as e:
        return {"error_message": f"Falha na extração: {e}", "is_valid": False}

def conditional_validation(state: GraphState) -> str:
    """Lógica de roteamento para extração válida."""
    if state.get("is_valid", False):
        return "evaluator_node"
    return "human_review_node"

def human_review_node(state: GraphState) -> GraphState:
    """Um nó reservado que interrompe a execução quando há um erro. 
    O checkpointer do LangGraph permite pausar antes deste nó ou retomar a partir dele."""
    # Este nó não fará muito, ele depende do mecanismo interrupt_before/interrupt_after
    print(f"--- REVISÃO HUMANA NECESSÁRIA ---")
    print(f"Erro: {state.get('error_message')}")
    return state
    
def evaluator_node(state: GraphState) -> GraphState:
    """Usa GPT-4o mini para avaliar o candidato."""
    # Serializamos a extração estruturada para o LLM
    extracted = state["extracted_data"]
    
    if isinstance(extracted, CandidateExtraction):
        extracted_dict = extracted.model_dump()
    else:
        extracted_dict = extracted
        
    model_name = "gpt-4o-mini"
    print(f"--- Iniciando avaliação do candidato. Modelo em uso: {model_name} ---")
    llm = ChatOpenAI(model=model_name, temperature=0.0)
    structured_llm = llm.with_structured_output(CandidateEvaluation)
    
    try:
         result = structured_llm.invoke([
            SystemMessage(content="You are a Senior Tech Recruiter assessing a candidate's profile against general industry standards for their target role. Evaluate them fairly based on the provided extracted data. The candidate's CV is in Portuguese, and your evaluation responses MUST be written in Brazilian Portuguese (pt-BR)."),
            HumanMessage(content=f"Extracted Candidate Data:\n{extracted_dict}")
         ])
         return {"evaluated_data": result}
    except Exception as e:
        print(f"Erro na avaliação: {e}")
        return {"error_message": f"Falha na avaliação: {e}"}

def export_to_crm(state: GraphState) -> GraphState:
    """Combina dados de extração e avaliação em um registro de CRM e salva no Excel."""
    extracted = state.get("extracted_data")
    evaluated = state.get("evaluated_data")
    
    if not extracted or not evaluated:
        return state
        
    if isinstance(extracted, CandidateExtraction):
        extr_dict = extracted.model_dump()
    else:
        extr_dict = extracted
        
    if isinstance(evaluated, CandidateEvaluation):
        eval_dict = evaluated.model_dump()
    else:
        eval_dict = evaluated
        
    # Construir registro completo (lidar com listas unindo-as)
    def clean_val(v):
        if isinstance(v, list):
            return ", ".join([str(x) for x in v])
        if v is None:
            return ""
        return v
        
    combined = {**extr_dict, **eval_dict}
    
    record = CRMRecord(
        candidate_id=str(combined.get("candidate_id") or uuid.uuid4()),
        full_name=clean_val(combined.get("full_name")),
        email=clean_val(combined.get("email")),
        phone=clean_val(combined.get("phone")),
        city=clean_val(combined.get("city")),
        state=clean_val(combined.get("state")),
        country=clean_val(combined.get("country")),
        linkedin_url=clean_val(combined.get("linkedin_url")),
        github_url=clean_val(combined.get("github_url")),
        portfolio_url=clean_val(combined.get("portfolio_url")),
        current_title=clean_val(combined.get("current_title")),
        target_role=clean_val(combined.get("target_role")),
        seniority_level=clean_val(combined.get("seniority_level")),
        years_of_experience=float(combined.get("years_of_experience") or 0.0),
        current_company=clean_val(combined.get("current_company")),
        current_company_tenure_months=int(combined.get("current_company_tenure_months") or 0),
        education_level=clean_val(combined.get("education_level")),
        degree_name=clean_val(combined.get("degree_name")),
        institution_name=clean_val(combined.get("institution_name")),
        graduation_year=int(combined.get("graduation_year") or 0),
        primary_stack=clean_val(combined.get("primary_stack")),
        secondary_stack=clean_val(combined.get("secondary_stack")),
        programming_languages=clean_val(combined.get("programming_languages")),
        frameworks=clean_val(combined.get("frameworks")),
        databases=clean_val(combined.get("databases")),
        cloud_platforms=clean_val(combined.get("cloud_platforms")),
        devops_tools=clean_val(combined.get("devops_tools")),
        methodologies=clean_val(combined.get("methodologies")),
        spoken_languages=clean_val(combined.get("spoken_languages")),
        latest_job_title=clean_val(combined.get("latest_job_title")),
        latest_company=clean_val(combined.get("latest_company")),
        latest_job_start_date=clean_val(combined.get("latest_job_start_date")),
        latest_job_end_date=clean_val(combined.get("latest_job_end_date")),
        previous_companies_count=int(combined.get("previous_companies_count") or 0),
        job_hopping_flag=bool(combined.get("job_hopping_flag") or False),
        key_skills=clean_val(combined.get("key_skills")),
        must_have_skills_match=float(combined.get("must_have_skills_match") or 0.0),
        nice_to_have_skills_match=float(combined.get("nice_to_have_skills_match") or 0.0),
        domain_experience=clean_val(combined.get("domain_experience")),
        industry_experience=clean_val(combined.get("industry_experience")),
        management_experience=bool(combined.get("management_experience") or False),
        team_lead_experience=bool(combined.get("team_lead_experience") or False),
        certifications=clean_val(combined.get("certifications")),
        relevant_projects=clean_val(combined.get("relevant_projects")),
        achievements_summary=clean_val(combined.get("achievements_summary")),
        employment_type_preference=clean_val(combined.get("employment_type_preference")),
        work_model_preference=clean_val(combined.get("work_model_preference")),
        availability_status=clean_val(combined.get("availability_status")),
        notice_period_days=int(combined.get("notice_period_days") or 0),
        salary_expectation=float(combined.get("salary_expectation") or 0.0),
        currency=clean_val(combined.get("currency")),
        relocation_available=bool(combined.get("relocation_available") or False),
        
        cv_source="File System",
        cv_file_name=state["cv_file_name"],
        cv_language="Unknown",
        cv_parse_date=datetime.datetime.now().isoformat(),
        cv_last_update_date=datetime.datetime.now().isoformat(),
        
        recruiter_notes=clean_val(combined.get("recruiter_notes")),
        candidate_score=float(combined.get("candidate_score") or 0.0),
        candidate_status=clean_val(combined.get("candidate_status")),
        fit_summary=clean_val(combined.get("fit_summary")),
        red_flags=clean_val(combined.get("red_flags")),
        next_action=clean_val(combined.get("next_action"))
    )
    
    # Salvar no Excel
    output_path = "output/crm_database.xlsx"
    df_new = pd.DataFrame([record.model_dump()])
    
    if os.path.exists(output_path):
        df_existing = pd.read_excel(output_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(output_path, index=False)
    else:
        df_new.to_excel(output_path, index=False)
        
    return state


# --- Construir Grafo ---
def build_cv_extractor_graph():
    builder = StateGraph(GraphState)
    
    builder.add_node("ingest_pdf", ingest_pdf)
    builder.add_node("extractor_node", extractor_node)
    builder.add_node("evaluator_node", evaluator_node)
    builder.add_node("export_to_crm", export_to_crm)
    builder.add_node("human_review_node", human_review_node)
    
    builder.add_edge(START, "ingest_pdf")
    builder.add_edge("ingest_pdf", "extractor_node")
    
    builder.add_conditional_edges("extractor_node", conditional_validation, {
        "evaluator_node": "evaluator_node",
        "human_review_node": "human_review_node"
    })
    
    # Após a revisão humana, você pode rotear de volta ou finalizar. Por enquanto, rotearemos para o fim se houver erro.
    builder.add_edge("human_review_node", END)
    
    builder.add_edge("evaluator_node", "export_to_crm")
    builder.add_edge("export_to_crm", END)
    
    return builder
