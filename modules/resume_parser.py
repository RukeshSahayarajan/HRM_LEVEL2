# ============================================================
# FILE: modules/resume_parser.py
# ============================================================
"""
Resume Parser Module
Parses resumes using Groq AI
"""

import json
from modules.ai_client import generate_content, parse_json_response


def parse_resume(text):
    """
    Parse Resume using Groq AI

    Args:
        text: Raw text extracted from resume

    Returns:
        dict: Parsed resume data with structured information
    """
    try:
        prompt = f"""You are an expert resume parser. Extract ALL information comprehensively and return ONLY valid JSON (no markdown, no code blocks):

{{
    "name": "Full name of candidate",
    
    "contact_details": {{
        "email": "Email address",
        "phone": "Phone number with country code if present",
        "linkedin": "LinkedIn profile URL if found",
        "github": "GitHub profile URL if found",
        "portfolio": "Portfolio/website URL if found",
        "location": "City, State/Country"
    }},
    
    "skills": {{
        "technical_skills": ["ALL programming languages, frameworks, technologies found ANYWHERE"],
        "tools": ["ALL tools, software, platforms mentioned"],
        "soft_skills": ["Communication, leadership, teamwork, etc."],
        "all_skills_combined": ["Flat list of ALL skills for easy matching"]
    }},
    
    "experience": {{
        "total_experience": "Calculate total years and months from ALL jobs (e.g., '3 years 6 months', '6 months', 'Fresher')",
        "companies": [
            {{
                "company": "Company name",
                "location": "Company location",
                "role": "Job title/position",
                "duration": "Start date - End date (e.g., 'Jan 2022 - Present')",
                "duration_months": 0,
                "responsibilities": ["Key responsibilities and achievements"],
                "skills_used": ["Technologies/tools used in this role"]
            }}
        ]
    }},
    
    "education": [
        {{
            "college": "Institution/University name",
            "degree": "Degree name (PhD/Masters/Bachelors/Diploma)",
            "specialization": "Field of study (e.g., 'Computer Science')",
            "score": "CGPA/GPA/Percentage with scale (e.g., '8.5/10' or '85%')",
            "year_of_passing": "Graduation year",
            "location": "College location if mentioned"
        }}
    ],
    
    "projects": [
        {{
            "name": "Project title",
            "duration": "Project timeline (e.g., '01/2023 - 03/2023')",
            "description": "Clear 2-3 line summary",
            "technologies": ["Technologies, frameworks, tools used"],
            "highlights": ["Key achievements or features"],
            "domain": "Project domain (e.g., 'E-commerce', 'Healthcare', 'Finance')"
        }}
    ],
    
    "certifications": [
        {{
            "name": "Certification name",
            "issuer": "Issuing organization",
            "date": "Completion date if mentioned",
            "credential_id": "Credential ID if mentioned"
        }}
    ],
    
    "achievements": ["Awards, recognitions, publications, etc."],
    
    "profile_quality": {{
        "has_linkedin": true,
        "has_github": true,
        "has_portfolio": false,
        "profile_completeness": 85
    }}
}}

Resume Text:
{text}"""

        print("🤖 Sending resume to Groq AI...")
        response_text = generate_content(prompt)
        parsed_data = parse_json_response(response_text)

        if parsed_data:
            print(f"✅ Resume parsed successfully")
            return parsed_data
        else:
            print(f"❌ Failed to parse resume JSON")
            return None

    except Exception as e:
        print(f"❌ Resume Parsing Error: {e}")
        return None


def get_resume_summary(resume_data):
    """
    Generate a human-readable summary of parsed resume

    Args:
        resume_data: Parsed resume dictionary

    Returns:
        str: Summary text
    """
    summary = f"""
👤 RESUME SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {resume_data.get('name', 'N/A')}
Email: {resume_data.get('contact_details', {}).get('email', 'N/A')}
Phone: {resume_data.get('contact_details', {}).get('phone', 'N/A')}
Location: {resume_data.get('contact_details', {}).get('location', 'N/A')}

EXPERIENCE:
  Total: {resume_data.get('experience', {}).get('total_experience', 'N/A')}
  Companies: {len(resume_data.get('experience', {}).get('companies', []))}

EDUCATION:
  Degrees: {len(resume_data.get('education', []))}
  Highest: {resume_data.get('education', [{}])[0].get('degree', 'N/A') if resume_data.get('education') else 'N/A'}

SKILLS:
  Technical: {len(resume_data.get('skills', {}).get('technical_skills', []))}
  Tools: {len(resume_data.get('skills', {}).get('tools', []))}

PROJECTS: {len(resume_data.get('projects', []))}
CERTIFICATIONS: {len(resume_data.get('certifications', []))}

PROFILES:
  LinkedIn: {'✓' if resume_data.get('contact_details', {}).get('linkedin') else '✗'}
  GitHub: {'✓' if resume_data.get('contact_details', {}).get('github') else '✗'}
  Portfolio: {'✓' if resume_data.get('contact_details', {}).get('portfolio') else '✗'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return summary
