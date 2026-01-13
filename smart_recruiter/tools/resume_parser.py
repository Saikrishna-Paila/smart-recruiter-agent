"""Resume Parser Tool - Extract structured data from resumes."""
import os
import re
from typing import Optional
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import Field
import fitz  # PyMuPDF
from docx import Document

class ResumeParserTool(BaseTool):
    """Tool to parse resumes and extract structured information."""

    name: str = "resume_parser"
    description: str = """
    Parses a resume file (PDF, DOC, DOCX) and extracts structured information.
    Input: path to the resume file
    Output: Extracted text content and structured data from the resume
    """

    def _run(self, resume_path: str) -> str:
        """Parse resume and extract text content."""
        if not os.path.exists(resume_path):
            return f"Error: File not found at {resume_path}"

        file_ext = Path(resume_path).suffix.lower()

        try:
            if file_ext == '.pdf':
                text = self._parse_pdf(resume_path)
            elif file_ext in ['.doc', '.docx']:
                text = self._parse_docx(resume_path)
            else:
                return f"Error: Unsupported file format {file_ext}. Supported: PDF, DOC, DOCX"

            if not text.strip():
                return "Error: Could not extract text from resume. File may be empty or corrupted."

            return f"RESUME CONTENT:\n{text}"

        except Exception as e:
            return f"Error parsing resume: {str(e)}"

    def _parse_pdf(self, path: str) -> str:
        """Extract text from PDF file."""
        text_parts = []
        doc = fitz.open(path)
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)

    def _parse_docx(self, path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(path)
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        return "\n".join(text_parts)


class ResumeAnalyzerTool(BaseTool):
    """Tool to analyze parsed resume and extract structured data."""

    name: str = "resume_analyzer"
    description: str = """
    Analyzes resume text and extracts structured data including:
    - Contact information (name, email, phone)
    - Skills
    - Work experience
    - Education
    - Certifications
    Input: Raw text content from a resume
    Output: Structured analysis of the resume
    """

    def _run(self, resume_text: str) -> str:
        """Analyze resume text and extract structured data."""
        result = []

        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            result.append(f"EMAIL: {emails[0]}")

        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            result.append(f"PHONE: {phones[0]}")

        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, resume_text.lower())
        if linkedin:
            result.append(f"LINKEDIN: {linkedin[0]}")

        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, resume_text.lower())
        if github:
            result.append(f"GITHUB: {github[0]}")

        # Common technical skills to look for (expanded for AI/ML roles)
        common_skills = [
            # Programming Languages
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'scala', 'kotlin',
            # Web Frameworks
            'react', 'angular', 'vue', 'next.js', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'github actions',
            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'cassandra',
            # AI/ML Frameworks
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'xgboost',
            'hugging face', 'transformers', 'nltk', 'spacy', 'opencv',
            # LLM & GenAI
            'langchain', 'langgraph', 'llamaindex', 'openai', 'gpt', 'llm', 'rag', 'fine-tuning', 'prompt engineering',
            'vector database', 'pinecone', 'qdrant', 'faiss', 'pgvector', 'chromadb', 'weaviate',
            'embedding', 'retrieval', 'agentic', 'function calling', 'chatgpt', 'claude', 'anthropic',
            # Data Engineering
            'spark', 'hadoop', 'airflow', 'kafka', 'etl', 'data pipeline', 'databricks', 'snowflake',
            'pandas', 'numpy', 'dask', 'polars',
            # MLOps
            'mlflow', 'kubeflow', 'sagemaker', 'vertex ai', 'mlops', 'model deployment', 'model monitoring',
            # Other
            'git', 'linux', 'agile', 'scrum', 'jira',
            'html', 'css', 'tailwind',
            'rest api', 'graphql', 'microservices', 'api design',
            'nlp', 'computer vision', 'reinforcement learning', 'neural network'
        ]

        found_skills = []
        text_lower = resume_text.lower()
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)

        if found_skills:
            result.append(f"DETECTED SKILLS: {', '.join(found_skills)}")

        # Estimate years of experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|of|working)',
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result.append(f"EXPERIENCE: {match.group(1)}+ years")
                break

        # Extract education - look for degree + field patterns
        education_found = []

        # Look for specific degree mentions
        degree_keywords = [
            r"(b\.?s\.?|bachelor'?s?)\s+(?:in\s+)?(computer science|data science|engineering|information technology)",
            r"(m\.?s\.?|master'?s?)\s+(?:in\s+)?(computer science|data science|engineering|information technology|business)",
            r"(ph\.?d\.?|doctorate)\s+(?:in\s+)?(computer science|data science|engineering)",
            r"(mba|m\.?b\.?a\.?)",
        ]

        for pattern in degree_keywords:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                if isinstance(m, tuple):
                    edu = " ".join([p for p in m if p]).strip()
                    if len(edu) > 3:
                        education_found.append(edu.title())
                elif m:
                    education_found.append(m.upper())

        # Also look for university names
        university_pattern = r'([\w\s]+university|[\w\s]+institute of technology|[\w\s]+college)'
        uni_matches = re.findall(university_pattern, text_lower)
        universities = [u.strip().title() for u in uni_matches if len(u.strip()) > 5][:2]

        if education_found:
            result.append(f"EDUCATION: {', '.join(list(set(education_found))[:3])}")
        if universities:
            result.append(f"UNIVERSITIES: {', '.join(universities)}")

        # Extract companies
        company_indicators = ['at ', 'for ', ' - ', ', ']
        job_titles = ['engineer', 'developer', 'scientist', 'analyst', 'manager', 'lead', 'architect', 'consultant']

        result.append(f"\nFULL TEXT:\n{resume_text[:2000]}...")

        return "\n".join(result)
