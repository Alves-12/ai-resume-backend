# backend/parser.py
from docx import Document
import requests
from bs4 import BeautifulSoup

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def extract_resume_sections(text):
    sections = {}
    lines = text.split('\n')
    current_section = 'HEADER'
    sections[current_section] = []

    headings = [
        'SUMMARY', 'SKILLS', 'EDUCATION', 'WORK HISTORY',
        'EXPERIENCE', 'CERTIFICATES', 'PROJECTS', 'LANGUAGES'
    ]

    for line in lines:
        line = line.strip()
        if any(h in line.upper() for h in headings):
            current_section = line.upper()
            sections[current_section] = []
        elif line:
            sections.setdefault(current_section, []).append(line)

    return {k: '\n'.join(v) for k, v in sections.items()}

def fetch_job_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract visible text (simplified)
        paragraphs = soup.find_all(['p', 'li'])
        text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return text
    except Exception as e:
        return f"Error fetching job from URL: {str(e)}"