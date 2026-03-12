from pydantic import BaseModel, Field
from typing import List, Optional

class CandidateExtraction(BaseModel):
    """Dados extraídos do texto bruto do CV usando o SLM."""
    candidate_id: Optional[str] = Field(default=None, description="Unique identifier or generated id if none exists")
    full_name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    city: Optional[str] = Field(default=None, description="City of residence")
    state: Optional[str] = Field(default=None, description="State of residence")
    country: Optional[str] = Field(default=None, description="Country of residence")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, description="Personal portfolio URL")

    # Cargo e Experiência
    current_title: Optional[str] = Field(default=None, description="Current job title")
    target_role: Optional[str] = Field(default=None, description="Inferred target role based on profile")
    seniority_level: Optional[str] = Field(default=None, description="E.g., Junior, Mid, Senior, Lead")
    years_of_experience: Optional[float] = Field(default=None, description="Total years of professional experience")
    current_company: Optional[str] = Field(default=None, description="Current employer")
    current_company_tenure_months: Optional[int] = Field(default=None, description="Tenure at current company in months")

    # Educação
    education_level: Optional[str] = Field(default=None, description="Highest degree level (e.g., Bachelor, Master)")
    degree_name: Optional[str] = Field(default=None, description="Name of the degree")
    institution_name: Optional[str] = Field(default=None, description="Name of the educational institution")
    graduation_year: Optional[int] = Field(default=None, description="Year of graduation")

    # Stack de Habilidades
    primary_stack: List[str] = Field(default_factory=list, description="Primary technologies/stack used")
    secondary_stack: List[str] = Field(default_factory=list, description="Secondary technologies/stack used")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages known")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks known")
    databases: List[str] = Field(default_factory=list, description="Databases known")
    cloud_platforms: List[str] = Field(default_factory=list, description="Cloud platforms experienced with (e.g., AWS, Azure)")
    devops_tools: List[str] = Field(default_factory=list, description="DevOps and CI/CD tools used")
    methodologies: List[str] = Field(default_factory=list, description="Methodologies familiar with (e.g., Agile, Scrum)")
    spoken_languages: List[str] = Field(default_factory=list, description="Languages spoken")

    # Detalhes do Último Emprego
    latest_job_title: Optional[str] = Field(default=None, description="Title at most recent job")
    latest_company: Optional[str] = Field(default=None, description="Company of most recent job")
    latest_job_start_date: Optional[str] = Field(default=None, description="Start date of latest job (YYYY-MM-DD or YYYY-MM)")
    latest_job_end_date: Optional[str] = Field(default=None, description="End date of latest job or 'Present'")
    previous_companies_count: Optional[int] = Field(default=None, description="Number of previous companies worked for")
    job_hopping_flag: Optional[bool] = Field(default=False, description="True if the candidate has a history of short tenures")

    # Detalhes de Experiência
    key_skills: List[str] = Field(default_factory=list, description="Overall key skills or tags representing the candidate")
    domain_experience: List[str] = Field(default_factory=list, description="Specific business domains worked in")
    industry_experience: List[str] = Field(default_factory=list, description="Industries worked in (e.g., FinTech, Healthcare)")
    management_experience: Optional[bool] = Field(default=False, description="Has experience managing people")
    team_lead_experience: Optional[bool] = Field(default=False, description="Has experience as a team lead")

    # Extras
    certifications: List[str] = Field(default_factory=list, description="Professional certifications obtained")
    relevant_projects: List[str] = Field(default_factory=list, description="Notable projects mentioned")
    achievements_summary: Optional[str] = Field(default=None, description="Summary of key achievements")

    # Preferências
    employment_type_preference: Optional[str] = Field(default=None, description="Contract, Full-time, etc.")
    work_model_preference: Optional[str] = Field(default=None, description="Remote, Hybrid, On-site")
    availability_status: Optional[str] = Field(default=None, description="Immediately available, passive, etc.")
    notice_period_days: Optional[int] = Field(default=None, description="Days required before starting")
    salary_expectation: Optional[float] = Field(default=None, description="Expected salary figure")
    currency: Optional[str] = Field(default=None, description="Currency of salary expectation")
    relocation_available: Optional[bool] = Field(default=None, description="Willingness to relocate")


class CandidateEvaluation(BaseModel):
    """Dados avaliados pelo LLM (GPT-4o mini) com base nos dados extraídos."""
    must_have_skills_match: float = Field(description="Percentage match for typical must-have skills for the role (0-100)")
    nice_to_have_skills_match: float = Field(description="Percentage match for typical nice-to-have skills (0-100)")
    recruiter_notes: str = Field(description="Notes for the recruiter generated by the LLM")
    candidate_score: float = Field(description="Overall rating score of the candidate (0-100)")
    candidate_status: str = Field(description="Determined status/stage (e.g., Shortlisted, Rejected, Hold)")
    fit_summary: str = Field(description="A brief paragraph summarizing the candidate's fit for the target role")
    red_flags: List[str] = Field(default_factory=list, description="List of potential red flags identified")
    next_action: str = Field(description="Suggested next action (e.g., Schedule screening call)")

class CRMRecord(BaseModel):
    """Representa a estrutura final plana destinada à linha do Excel."""
    # Campos extraídos
    candidate_id: str
    full_name: str
    email: str
    phone: str
    city: str
    state: str
    country: str
    linkedin_url: str
    github_url: str
    portfolio_url: str

    current_title: str
    target_role: str
    seniority_level: str
    years_of_experience: float
    current_company: str
    current_company_tenure_months: int

    education_level: str
    degree_name: str
    institution_name: str
    graduation_year: int

    primary_stack: str
    secondary_stack: str
    programming_languages: str
    frameworks: str
    databases: str
    cloud_platforms: str
    devops_tools: str
    methodologies: str
    spoken_languages: str

    latest_job_title: str
    latest_company: str
    latest_job_start_date: str
    latest_job_end_date: str
    previous_companies_count: int
    job_hopping_flag: bool

    key_skills: str
    must_have_skills_match: float
    nice_to_have_skills_match: float
    domain_experience: str
    industry_experience: str
    management_experience: bool
    team_lead_experience: bool

    certifications: str
    relevant_projects: str
    achievements_summary: str

    employment_type_preference: str
    work_model_preference: str
    availability_status: str
    notice_period_days: int
    salary_expectation: float
    currency: str
    relocation_available: bool

    cv_source: str
    cv_file_name: str
    cv_language: str
    cv_parse_date: str
    cv_last_update_date: str

    # Campos avaliados
    recruiter_notes: str
    candidate_score: float
    candidate_status: str
    fit_summary: str
    red_flags: str
    next_action: str
