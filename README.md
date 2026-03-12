# Resume Extractor

**Resume Extractor** é uma ferramenta de automação robusta baseada em **LangGraph** que extrai dados estruturados de currículos (CVs) em PDF, avalia o perfil dos candidatos usando Inteligência Artificial (SLMs locais e LLMs em nuvem) e os consolida em uma base de dados no Excel projetada para sistemas de CRM ou ATS.

## 🎯 Principais Funcionalidades

- **Extração Automática:** Processa PDFs para extrair texto bruto de forma eficiente utilizando `pypdf`.
- **Estruturação de Dados com IA Local:** Utiliza modelos rodando localmente (via **Ollama**, como `phi3:mini` ou `qwen3.5:4b`) para mapear as informações não-estruturadas e transformá-las em um esquema estruturado validado (`pydantic`), capturando: dados de contato, formação acadêmica, histórico profissional, e *stack* de habilidades.
- **Avaliação de Candidatos:** Utiliza o `gpt-4o-mini` da **OpenAI** para atuar como um *Tech Recruiter Sênior* virtual. Ele lê os dados extraídos para avaliar o match das habilidades primárias/desejáveis e produz notas gerais de adequação à vaga.
- **Fluxo com Human-in-the-Loop (Revisão Humana):** Implementa um nó condicional. Caso a IA falhe em encontrar o nome completo (ou em outras validações), a execução daquele documento é pausada de forma inteligente.
- **Exportação Direta para Excel:** Gera (ou anexa a) um arquivo `crm_database.xlsx` contendo todos os registros extraídos em uma planilha consolidada e de fácil consumo para Recrutadores.

## 🏗 Arquitetura do Grafo (LangGraph Workflow)

O fluxo de processamento funciona na seguinte ordem:
1. `ingest_pdf` - Lê o arquivo na pasta `input/`, extrai o texto e o salva em cache na pasta `output/raw/`.
2. `extractor_node` - Processa o texto com o LLM estruturado via Ollama para popular o objeto `CandidateExtraction`.
3. `condição` - Verifica se a extração é válida. Se for inválida (ex: nome do candidato em branco), é direcionado ao `human_review_node`.
4. `evaluator_node` - Recebe os dados validados e produz o objeto formatado de avaliação qualitativa (`CandidateEvaluation`) no OpenAI.
5. `export_to_crm` - Combina extração + avaliação em uma estrutura plana (`CRMRecord`) e insere na planilha `output/crm_database.xlsx`.

> **Nota:** A imagem completa da arquitetura pode ser vista gerada no arquivo `graph_image.png` após a execução do código.

## 🚀 Como Começar

### Pré-requisitos

- Python >= 3.12
- [Ollama](https://ollama.com/) rodando no seu computador (com o modelo base instalado, ex: `ollama run phi3:mini`).
- Chave de API da OpenAI (para a avaliação final dos candidatos).

### Instalação

1. Clone o repositório ou navegue até o diretório do projeto.
2. Instale as dependências usando seu gerenciador de pacotes favorito (recomenda-se o uso de `uv`, `pip` ou ambiente virtual padrão):

```bash
# Exemplo com pip
pip install -r pyproject.toml
```

3. Crie e configure o arquivo de ambiente:
Copie o `.env.example` para `.env` e defina sua API Key da OpenAI:
```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Execução

1. Crie uma pasta chamada `input` (caso não exista) na raiz do projeto:
```bash
mkdir input
```

2. Coloque um ou mais arquivos de currículos (em formato `.pdf`) dentro do diretório `input`.

3. Execute o programa principal:
```bash
python main.py
```

4. **Resultados**: 
    - Os textos brutos estarão armazenados em `output/raw`.
    - Os dados consolidados e de avaliação dos candidatos resultantes estarão em `output/crm_database.xlsx`.

## 🛠️ Tecnologias Utilizadas

- [LangGraph](https://python.langchain.com/docs/langgraph) / [LangChain](https://python.langchain.com/) - Orquestração do fluxo de agentes.
- [Ollama](https://ollama.com/) / [Langchain-Ollama](https://python.langchain.com/docs/integrations/llms/ollama/) - SLMs Locais para extração estruturada de menor custo e maior privacidade de dados sensíveis.
- [OpenAI](https://openai.com/) / GPT-4o-mini - LLM Inteligente para a análise inferencial de recrutamento.
- [Pydantic](https://docs.pydantic.dev/) - Tipagem forte e validação dos esquemas (Schemas) de JSON.
- [pandas](https://pandas.pydata.org/) / [openpyxl](https://openpyxl.readthedocs.io/) - Manipulação e exportação dos dados tabulares.
- [pypdf](https://pypi.org/project/pypdf/) - Leitura dos PDFs de entrada.

## 🇧🇷 Audiência Alvo
Esta ferramenta busca facilitar a vida de *Tech Recruiters* do Brasil, estruturando extrações localizadas, em pt-BR padrão, permitindo buscas e ranqueamento rápidos via planilhas de ATS/CRM convencionais.
