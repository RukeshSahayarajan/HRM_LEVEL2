# ============================================================
# FILE: modules/rubrics_generator.py
# ============================================================
"""
AI-Powered Rubrics Generator Module
Uses Groq AI to automatically generate rubrics based on JD
"""

import json
from modules.ai_client import generate_content, parse_json_response
from config import DEFAULT_RUBRICS_WEIGHTS


def generate_rubrics_from_jd(jd_data):
    """
    AI-powered rubrics generation based on JD requirements

    Args:
        jd_data: Parsed JD dictionary

    Returns:
        dict: Rubrics configuration with weights and scoring criteria
    """
    try:
        # Remove MongoDB ObjectId if present
        jd_data_clean = {k: v for k, v in jd_data.items() if k != '_id'}

        # Create detailed prompt for AI
        prompt = f"""You are an expert HR analyst. Based on this job description, create a custom evaluation rubrics configuration.

BASE WEIGHTS (adjust intelligently based on JD):
- Skills: 25% (Technical skills)
- Tools: 25% (Tools and technologies)
- Experience: 20% (Work experience)
- Education: 5% (Educational background)
- Projects: 15% (Project experience)
- Certifications: 5% (Certifications and courses)
- Profile Quality: 5% (LinkedIn/GitHub/Role fit)

RULES FOR ADJUSTMENT:
1. If education is NOT mandatory or not mentioned → reduce education weight to 0-3% and redistribute
2. If certifications are required → increase certification weight
3. If JD is for freshers → increase education & projects weight, decrease experience weight
4. If JD requires senior role → increase experience weight significantly
5. If projects are explicitly required → increase projects weight
6. If specific tools are critical → increase tools weight
7. ALL weights MUST sum to 100%

JOB DESCRIPTION DATA:
{json.dumps(jd_data_clean, indent=2, default=str)}

Return ONLY valid JSON (no markdown, no explanations):
{{
    "rubrics_name": "Auto-generated rubrics for [Job Title]",
    "job_title": "{jd_data.get('job_title', 'N/A')}",
    "jd_analysis": {{
        "education_importance": "high/medium/low/none",
        "experience_level": "fresher/junior/mid/senior",
        "skills_criticality": "high/medium/low",
        "certifications_required": true,
        "projects_importance": "high/medium/low"
    }},
    
    "weights": {{
        "skills": 25,
        "tools": 25,
        "experience": 20,
        "education": 5,
        "projects": 15,
        "certifications": 5,
        "profile_quality": 5
    }},
    
    "skills_criteria": {{
        "required_skills": {json.dumps(jd_data.get('required_skills', {}).get('technical_skills', []))},
        "required_tools": {json.dumps(jd_data.get('required_skills', {}).get('tools', []))},
        "minimum_match_percentage": 60,
        "scoring_notes": "Explanation of how skills will be scored"
    }},
    
    "experience_criteria": {{
        "required_years": "{jd_data.get('experience', {}).get('required_years', 'N/A')}",
        "required_roles": {json.dumps(jd_data.get('experience', {}).get('required_roles', []))},
        "scoring_method": "Description of experience scoring",
        "years_scoring": {{
            "perfect_match": ">=X years gets 100%",
            "partial_match": "How to score less experience",
            "no_experience": "0% if fresher allowed, else 0-20%"
        }}
    }},
    
    "education_criteria": {{
        "is_mandatory": {json.dumps(jd_data.get('education', {}).get('is_mandatory', False))},
        "required_degree": "{jd_data.get('education', {}).get('required_degree', 'N/A')}",
        "scoring": {{
            "phd": 100,
            "masters": 90,
            "bachelors": 80,
            "diploma": 60,
            "other": 40
        }},
        "scoring_notes": "Explanation"
    }},
    
    "projects_criteria": {{
        "required": {json.dumps(jd_data.get('projects', {}).get('required', False))},
        "expected_domains": {json.dumps(jd_data.get('projects', {}).get('domains', []))},
        "scoring_method": "How projects will be evaluated",
        "minimum_projects": 2,
        "scoring_notes": "1-2 projects: 60%, 3-4: 80%, 5+: 100%"
    }},
    
    "certifications_criteria": {{
        "required": {json.dumps(jd_data.get('certifications', {}).get('required', False))},
        "preferred_certifications": {json.dumps(jd_data.get('certifications', {}).get('list', []))},
        "scoring_method": "Each relevant cert: 25 points, max 100%"
    }},
    
    "profile_criteria": {{
        "linkedin_required": {json.dumps(jd_data.get('profile_requirements', {}).get('linkedin_required', False))},
        "github_required": {json.dumps(jd_data.get('profile_requirements', {}).get('github_required', False))},
        "portfolio_required": {json.dumps(jd_data.get('profile_requirements', {}).get('portfolio_required', False))},
        "role_fit_scoring": "50% role match + 50% profile presence"
    }},
    
    "reasoning": "Brief explanation of why weights were adjusted this way"
}}

IMPORTANT: 
- Weights MUST sum to exactly 100
- Be intelligent: if education not important in JD, give it 0-3%
- Adjust based on job level (fresher vs senior)
"""

        print("🤖 Generating rubrics with Groq AI...")
        response_text = generate_content(prompt)
        rubrics = parse_json_response(response_text)

        if not rubrics:
            print("⚠️ Rubrics generation failed, using fallback")
            return create_fallback_rubrics(jd_data)

        # Validate weights sum to 100
        total_weight = sum(rubrics.get('weights', {}).values())
        if abs(total_weight - 100) > 0.1:
            print(f"⚠️ Warning: Weights sum to {total_weight}%, normalizing to 100%")
            rubrics['weights'] = normalize_weights(rubrics['weights'])

        print("✅ Rubrics generated successfully")
        return rubrics

    except Exception as e:
        print(f"❌ Rubrics Generation Error: {e}")
        return create_fallback_rubrics(jd_data)


def normalize_weights(weights):
    """Normalize weights to sum to 100"""
    total = sum(weights.values())
    if total == 0:
        return DEFAULT_RUBRICS_WEIGHTS.copy()

    normalized = {}
    for key, value in weights.items():
        normalized[key] = round((value / total) * 100, 2)

    # Adjust for rounding errors
    diff = 100 - sum(normalized.values())
    if diff != 0:
        max_key = max(normalized, key=normalized.get)
        normalized[max_key] += diff

    return normalized


def create_fallback_rubrics(jd_data):
    """Create fallback rubrics if AI generation fails"""
    return {
        "rubrics_name": f"Fallback rubrics for {jd_data.get('job_title', 'Unknown')}",
        "job_title": jd_data.get('job_title', 'Unknown'),
        "jd_analysis": {
            "education_importance": "medium",
            "experience_level": "mid",
            "skills_criticality": "high",
            "certifications_required": False,
            "projects_importance": "medium"
        },
        "weights": DEFAULT_RUBRICS_WEIGHTS.copy(),
        "skills_criteria": {
            "required_skills": jd_data.get('required_skills', {}).get('technical_skills', []),
            "required_tools": jd_data.get('required_skills', {}).get('tools', []),
            "minimum_match_percentage": 60,
            "scoring_notes": "Match percentage based scoring"
        },
        "experience_criteria": {
            "required_years": jd_data.get('experience', {}).get('required_years', 'N/A'),
            "required_roles": jd_data.get('experience', {}).get('required_roles', []),
            "scoring_method": "Linear scoring based on years",
            "years_scoring": {
                "perfect_match": "Meets or exceeds required years",
                "partial_match": "Proportional scoring",
                "no_experience": "20% minimum"
            }
        },
        "education_criteria": {
            "is_mandatory": jd_data.get('education', {}).get('is_mandatory', False),
            "required_degree": jd_data.get('education', {}).get('required_degree', 'Bachelor'),
            "scoring": {
                "phd": 100,
                "masters": 90,
                "bachelors": 80,
                "diploma": 60,
                "other": 40
            },
            "scoring_notes": "Standard education scoring"
        },
        "projects_criteria": {
            "required": jd_data.get('projects', {}).get('required', False),
            "expected_domains": jd_data.get('projects', {}).get('domains', []),
            "scoring_method": "Count based",
            "minimum_projects": 2,
            "scoring_notes": "20% per project, max 100%"
        },
        "certifications_criteria": {
            "required": jd_data.get('certifications', {}).get('required', False),
            "preferred_certifications": jd_data.get('certifications', {}).get('list', []),
            "scoring_method": "25% per relevant certification"
        },
        "profile_criteria": {
            "linkedin_required": jd_data.get('profile_requirements', {}).get('linkedin_required', False),
            "github_required": jd_data.get('profile_requirements', {}).get('github_required', False),
            "portfolio_required": jd_data.get('profile_requirements', {}).get('portfolio_required', False),
            "scoring_method": "LinkedIn: 40%, GitHub: 40%, Portfolio: 20%"
        },
        "reasoning": "Fallback rubrics with balanced default weights"
    }


def validate_rubrics(rubrics):
    """Validate rubrics configuration"""
    try:
        if 'weights' not in rubrics:
            return False, "Missing 'weights' key"

        required_keys = ['skills', 'tools', 'experience', 'education',
                        'projects', 'certifications', 'profile_quality']

        for key in required_keys:
            if key not in rubrics['weights']:
                return False, f"Missing weight key: {key}"

        total = sum(rubrics['weights'].values())
        if abs(total - 100) > 0.1:
            return False, f"Weights sum to {total}%, must be 100%"

        for key, value in rubrics['weights'].items():
            if value < 0:
                return False, f"Negative weight for {key}: {value}"

        return True, "Valid"

    except Exception as e:
        return False, str(e)


def format_rubrics_for_display(rubrics):
    """Format rubrics for human-readable display"""
    weights = rubrics.get('weights', {})
    analysis = rubrics.get('jd_analysis', {})

    output = f"""
🎯 AI-GENERATED RUBRICS CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Job Title: {rubrics.get('job_title', 'N/A')}
Rubrics Name: {rubrics.get('rubrics_name', 'N/A')}

📊 JD ANALYSIS:
  Education Importance: {analysis.get('education_importance', 'N/A').upper()}
  Experience Level: {analysis.get('experience_level', 'N/A').upper()}
  Skills Criticality: {analysis.get('skills_criticality', 'N/A').upper()}
  Certifications Required: {'YES' if analysis.get('certifications_required') else 'NO'}
  Projects Importance: {analysis.get('projects_importance', 'N/A').upper()}

⚖️ EVALUATION WEIGHTS:
  Skills:              {weights.get('skills', 0)}%
  Tools:               {weights.get('tools', 0)}%
  Experience:          {weights.get('experience', 0)}%
  Education:           {weights.get('education', 0)}%
  Projects:            {weights.get('projects', 0)}%
  Certifications:      {weights.get('certifications', 0)}%
  Profile Quality:     {weights.get('profile_quality', 0)}%
  ─────────────────────────────
  TOTAL:               {sum(weights.values())}%

💡 AI REASONING:
{rubrics.get('reasoning', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return output