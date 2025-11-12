# ============================================================
# FILE: modules/jd_parser.py
# ============================================================
"""
Job Description Parser Module
Parses JD using Groq AI
"""

import json
from modules.ai_client import generate_content, parse_json_response


def parse_jd(text):
    """
    Parse Job Description using Groq AI

    Args:
        text: Raw text extracted from JD

    Returns:
        dict: Parsed JD data with structured information
    """
    try:
        prompt = f"""You are an expert job description analyzer. Analyze this JD carefully and extract ALL relevant information.

Return ONLY valid JSON (no markdown, no code blocks, no explanations):

{{
    "job_title": "Exact job title/position",
    "company": "Company name if mentioned",
    "department": "Department if mentioned",
    "job_type": "Full-time/Part-time/Contract/Internship",
    "location": "Job location",
    "work_mode": "Remote/Hybrid/On-site",
    "salary_range": "Salary range if mentioned",
    
    "required_skills": {{
        "technical_skills": ["List ALL technical skills, programming languages, frameworks mentioned"],
        "tools": ["List ALL tools, software, platforms mentioned"],
        "soft_skills": ["List soft skills like communication, leadership, etc."]
    }},
    
    "experience": {{
        "required_years": "Extract required years (e.g., '3-5 years', '2+ years', 'Fresher')",
        "required_roles": ["Previous role titles that are preferred/required"],
        "domain_experience": ["Specific domain/industry experience if mentioned"]
    }},
    
    "education": {{
        "required_degree": "Required degree (e.g., 'Bachelor's in CS', 'Master's', 'Any degree')",
        "preferred_degree": "Preferred degree if different from required",
        "specialization": "Specific specialization if mentioned",
        "is_mandatory": true or false based on whether education is strictly required
    }},
    
    "projects": {{
        "required": true or false,
        "description": "Type of projects experience needed",
        "domains": ["Specific project domains if mentioned"]
    }},
    
    "certifications": {{
        "required": true or false,
        "list": ["Specific certifications mentioned"],
        "is_mandatory": true or false
    }},
    
    "profile_requirements": {{
        "linkedin_required": true or false,
        "github_required": true or false,
        "portfolio_required": true or false
    }},
    
    "responsibilities": ["Key job responsibilities"],
    "benefits": ["Benefits mentioned if any"],
    "notice_period": "Required notice period if mentioned"
}}

Job Description Text:
{text}"""

        print("🤖 Sending JD to Groq AI...")
        response_text = generate_content(prompt)
        parsed_data = parse_json_response(response_text)

        if parsed_data:
            print(f"✅ JD parsed successfully")
            return parsed_data
        else:
            print(f"❌ Failed to parse JD JSON")
            return None

    except Exception as e:
        print(f"❌ JD Parsing Error: {e}")
        return None


def get_jd_summary(jd_data):
    """
    Generate a human-readable summary of parsed JD
    Safely handles missing or malformed fields from AI output.
    """

    def safe_join(value):
        """Safely join a list or return string/default"""
        if isinstance(value, list):
            return ', '.join(value) if value else 'N/A'
        elif isinstance(value, str):
            return value
        elif value is None:
            return 'N/A'
        return str(value)

    # Extract sub-sections safely
    experience = jd_data.get('experience', {}) or {}
    education = jd_data.get('education', {}) or {}
    skills = jd_data.get('required_skills', {}) or {}
    projects = jd_data.get('projects', {}) or {}
    certs = jd_data.get('certifications', {}) or {}

    summary = f"""
📋 JOB DESCRIPTION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Position: {jd_data.get('job_title', 'N/A')}
Company: {jd_data.get('company', 'N/A')}
Location: {jd_data.get('location', 'N/A')} | {jd_data.get('work_mode', 'N/A')}

EXPERIENCE REQUIRED:
  Years: {experience.get('required_years', 'N/A')}
  Roles: {safe_join(experience.get('required_roles'))}
  Domains: {safe_join(experience.get('domain_experience'))}

EDUCATION:
  Required: {education.get('required_degree', 'N/A')}
  Preferred: {education.get('preferred_degree', 'N/A')}
  Specialization: {education.get('specialization', 'N/A')}
  Mandatory: {education.get('is_mandatory', 'N/A')}

SKILLS:
  Technical: {safe_join(skills.get('technical_skills'))}
  Tools: {safe_join(skills.get('tools'))}
  Soft Skills: {safe_join(skills.get('soft_skills'))}

PROJECTS:
  Required: {'Yes' if projects.get('required') else 'No'}
  Domains: {safe_join(projects.get('domains'))}

CERTIFICATIONS:
  Required: {'Yes' if certs.get('required') else 'No'}
  List: {safe_join(certs.get('list'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return summary.strip()
