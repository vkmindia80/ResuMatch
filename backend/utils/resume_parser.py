"""
Resume Parser Utility
Extracts structured data from resumes (PDF, DOCX, TXT) using AI
"""
import os
import io
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import PyPDF2
import docx
import pdfplumber
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

class ResumeParser:
    """Parse resumes and extract structured data using AI"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfplumber first (better for formatted PDFs)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text.strip()
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2")
        
        try:
            # Fallback to PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1').strip()
            except Exception as e:
                raise ValueError(f"Failed to extract text from TXT: {str(e)}")
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from file based on extension"""
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file_content)
        elif file_extension in ['docx', 'doc']:
            return self.extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def parse_resume_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text and extract structured data using AI"""
        
        # Create system message for AI
        system_message = """You are an expert resume parser. Extract structured information from resumes and return it in JSON format.
        
Your task is to extract the following information:
1. Personal Information: name, email, phone, location, title, linkedin, portfolio
2. Education: institution, degree, field, start_date, end_date, gpa, achievements
3. Work Experience: company, title, employment_type, start_date, end_date, location, responsibilities, achievements, technologies
4. Skills: technical skills, soft skills, languages, tools
5. Projects: name, description, technologies, role, url, start_date, end_date
6. Certifications: name, issuer, issue_date, expiry_date, credential_id

Return the data in this exact JSON structure:
{
  "personal_info": {
    "full_name": "",
    "email": "",
    "phone": "",
    "location": "",
    "title": "",
    "linkedin": "",
    "portfolio": ""
  },
  "education": [
    {
      "institution": "",
      "degree": "",
      "field": "",
      "start_date": "",
      "end_date": "",
      "gpa": null,
      "achievements": []
    }
  ],
  "experience": [
    {
      "company": "",
      "title": "",
      "employment_type": "",
      "start_date": "",
      "end_date": "",
      "is_current": false,
      "location": "",
      "responsibilities": [],
      "achievements": [],
      "technologies": []
    }
  ],
  "skills": {
    "technical": [],
    "soft": [],
    "languages": [],
    "tools": []
  },
  "projects": [
    {
      "name": "",
      "description": "",
      "technologies": [],
      "role": "",
      "url": "",
      "start_date": "",
      "end_date": ""
    }
  ],
  "certifications": [
    {
      "name": "",
      "issuer": "",
      "issue_date": "",
      "expiry_date": "",
      "credential_id": ""
    }
  ]
}

Important:
- Extract only information that is present in the resume
- Use null or empty arrays for missing information
- For dates, use format: "YYYY-MM" or "YYYY" if only year is available
- Be thorough and accurate
- Return ONLY valid JSON, no extra text or explanations"""

        try:
            # Initialize LLM chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"resume_parser_{hash(resume_text[:100])}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")
            
            # Create user message with resume text
            user_message = UserMessage(
                text=f"Parse this resume and extract all information:\n\n{resume_text}"
            )
            
            # Get AI response
            response = await chat.send_message(user_message)
            
            # Parse JSON response
            import json
            # Extract JSON from response (in case there's extra text)
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            parsed_data = json.loads(response_text)
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"Failed to parse resume with AI: {str(e)}")
    
    async def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Main method to parse resume from file"""
        try:
            # Extract text from file
            resume_text = self.extract_text(file_content, filename)
            
            if not resume_text or len(resume_text) < 50:
                raise ValueError("Resume text is too short or empty")
            
            # Parse with AI
            parsed_data = await self.parse_resume_with_ai(resume_text)
            
            return {
                "success": True,
                "data": parsed_data,
                "raw_text": resume_text[:500]  # First 500 chars for reference
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
