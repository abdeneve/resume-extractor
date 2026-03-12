from fpdf import FPDF
import os

def create_dummy_cv():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    cv_content = [
        "JANE DOE",
        "jane.doe@example.com | +1 555-0198",
        "San Francisco, CA, USA",
        "LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe",
        "",
        "SUMMARY",
        "Senior Data Engineer with over 8 years of experience building scalable data pipelines",
        "and working with cloud data platforms.",
        "",
        "EXPERIENCE",
        "Senior Data Engineer | Tech Innovations Inc. | Jan 2021 - Present",
        "- Designed and implemented robust data pipelines using Apache Spark and Airflow.",
        "- Managed AWS infrastructure (S3, Redshift) for big data processing.",
        "- Lead a team of 3 junior engineers.",
        "",
        "Data Engineer | DataCorp | Jun 2016 - Dec 2020",
        "- Developed ETL processes using Python and SQL.",
        "- Migrated legacy databases to PostgreSQL.",
        "",
        "EDUCATION",
        "Master of Science in Computer Science | Stanford University | 2016",
        "Bachelor of Science in Information Technology | MIT | 2014",
        "",
        "SKILLS",
        "Programming: Python, Scala, SQL, Bash",
        "Frameworks: Apache Spark, Pandas, FastAPI",
        "Databases: PostgreSQL, Redshift, MongoDB",
        "Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins",
        "Certifications: AWS Certified Data Analytics - Specialty"
    ]
    
    for line in cv_content:
        pdf.cell(200, 10, txt=line, ln=1, align="L")
        
    os.makedirs("input", exist_ok=True)
    pdf.output("input/dummy_cv.pdf")
    print("Criado input/dummy_cv.pdf")

if __name__ == "__main__":
    create_dummy_cv()
