"""
Enhanced Evaluator Module
AI-powered candidate evaluation with detailed reasoning
"""

import re
import json
from modules.ai_client import generate_content, parse_json_response


def evaluate_candidate_with_reasoning(jd_data, resume_data, rubrics_config):
    """
    Evaluate candidate with AI-powered reasoning and tier classification
    """
    print("\n" + "=" * 60)
    print("STARTING CANDIDATE EVALUATION")
    print("=" * 60)

    # Calculate individual scores
    scores = {}
    weights = rubrics_config.get('weights', {})

    print("\nCalculating individual scores...")
    scores['skills'] = evaluate_skills(jd_data, resume_data, rubrics_config)
    print(f"  Skills: {scores['skills']:.1f}%")

    scores['tools'] = evaluate_tools(jd_data, resume_data, rubrics_config)
    print(f"  Tools: {scores['tools']:.1f}%")

    scores['experience'] = evaluate_experience(jd_data, resume_data, rubrics_config)
    print(f"  Experience: {scores['experience']:.1f}%")

    scores['education'] = evaluate_education(jd_data, resume_data, rubrics_config)
    print(f"  Education: {scores['education']:.1f}%")

    scores['projects'] = evaluate_projects(jd_data, resume_data, rubrics_config)
    print(f"  Projects: {scores['projects']:.1f}%")

    scores['certifications'] = evaluate_certifications(jd_data, resume_data, rubrics_config)
    print(f"  Certifications: {scores['certifications']:.1f}%")

    scores['profile_quality'] = evaluate_profile_quality(jd_data, resume_data, rubrics_config)
    print(f"  Profile Quality: {scores['profile_quality']:.1f}%")

    # Calculate weighted overall score
    overall_score = sum(scores[key] * (weights.get(key, 0) / 100) for key in scores.keys())
    print(f"\nOverall Score: {overall_score:.2f}%")

    # Generate AI reasoning
    print("\nGenerating AI reasoning...")
    ai_reasoning = generate_ai_reasoning(jd_data, resume_data, scores, weights, overall_score)

    if ai_reasoning:
        print(f"AI Reasoning Generated: {len(ai_reasoning)} characters")
        print(f"Preview: {ai_reasoning[:100]}...")
    else:
        print("WARNING: AI reasoning is empty!")

    # Determine candidate tier
    candidate_tier = determine_candidate_tier(overall_score, scores, ai_reasoning)
    print(f"Candidate Tier: {candidate_tier}")

    # Extract strengths and weaknesses
    strengths, weaknesses = extract_strengths_weaknesses(scores, weights, jd_data, resume_data)
    print(f"Strengths: {len(strengths)}, Weaknesses: {len(weaknesses)}")

    print("=" * 60)
    print("EVALUATION COMPLETED")
    print("=" * 60 + "\n")

    return {
        'individual_scores': scores,
        'overall_score': round(overall_score, 2),
        'weights_applied': weights,
        'breakdown': generate_score_breakdown(scores, weights),
        'ai_reasoning': ai_reasoning,
        'candidate_tier': candidate_tier,
        'strengths': strengths,
        'weaknesses': weaknesses
    }


def generate_ai_reasoning(jd_data, resume_data, scores, weights, overall_score):
    """
    Generate comprehensive AI reasoning for the candidate evaluation
    """
    try:
        # Extract data safely
        jd_title = jd_data.get('job_title', 'N/A')
        jd_exp = jd_data.get('experience', {}).get('required_years', 'N/A')
        jd_skills = jd_data.get('required_skills', {}).get('technical_skills', [])
        jd_tools = jd_data.get('required_skills', {}).get('tools', [])

        candidate_name = resume_data.get('name', 'Unknown')
        candidate_exp = resume_data.get('experience', {}).get('total_experience', 'N/A')
        candidate_edu = 'N/A'
        if resume_data.get('education') and len(resume_data.get('education', [])) > 0:
            candidate_edu = resume_data.get('education', [{}])[0].get('degree', 'N/A')
        candidate_skills = resume_data.get('skills', {}).get('technical_skills', [])

        prompt = f"""You are an expert HR analyst with 15+ years of experience in recruitment. Analyze this candidate evaluation and provide detailed professional reasoning.

JOB REQUIREMENTS:
- Position: {jd_title}
- Required Experience: {jd_exp}
- Key Skills: {', '.join(jd_skills[:5]) if jd_skills else 'Not specified'}
- Tools: {', '.join(jd_tools[:5]) if jd_tools else 'Not specified'}

CANDIDATE PROFILE:
- Name: {candidate_name}
- Total Experience: {candidate_exp}
- Education: {candidate_edu}
- Key Skills: {', '.join(candidate_skills[:10]) if candidate_skills else 'Not specified'}

EVALUATION SCORES:
- Skills Match: {scores['skills']:.1f}% (Weight: {weights.get('skills', 0)}%)
- Tools Match: {scores['tools']:.1f}% (Weight: {weights.get('tools', 0)}%)
- Experience: {scores['experience']:.1f}% (Weight: {weights.get('experience', 0)}%)
- Education: {scores['education']:.1f}% (Weight: {weights.get('education', 0)}%)
- Projects: {scores['projects']:.1f}% (Weight: {weights.get('projects', 0)}%)
- Certifications: {scores['certifications']:.1f}% (Weight: {weights.get('certifications', 0)}%)
- Profile Quality: {scores['profile_quality']:.1f}% (Weight: {weights.get('profile_quality', 0)}%)

OVERALL SCORE: {overall_score:.1f}%

Write a comprehensive 4-5 sentence professional analysis that:
1. Evaluates overall fit for the role
2. Highlights key matching strengths
3. Identifies critical gaps or areas of concern
4. Provides actionable recommendation (Strong Hire/Moderate Fit/Not Recommended)
5. Uses professional HR language and industry insights

Be honest, direct, and professional. Focus on job-relevant factors. Do NOT use any markdown formatting or code blocks."""

        print("\nSending prompt to AI for reasoning...")
        response = generate_content(prompt)

        if response:
            print(f"AI Response received: {len(response)} characters")
            # Clean and return reasoning
            reasoning = response.strip()

            # Remove any JSON formatting if present
            if reasoning.startswith('{'):
                try:
                    parsed = parse_json_response(reasoning)
                    reasoning = parsed.get('reasoning', reasoning)
                except:
                    pass

            # Remove markdown code blocks if present
            if '```' in reasoning:
                reasoning = reasoning.replace('```', '').strip()

            return reasoning
        else:
            print("WARNING: No response from AI, using fallback")
            return generate_fallback_reasoning(overall_score, scores)

    except Exception as e:
        print(f"ERROR in AI Reasoning: {str(e)}")
        return generate_fallback_reasoning(overall_score, scores)


def generate_fallback_reasoning(overall_score, scores):
    """Generate fallback reasoning if AI fails"""
    print("Using fallback reasoning generation")

    if overall_score >= 75:
        reasoning = f"This candidate demonstrates strong alignment with the role requirements, achieving an overall match score of {overall_score:.1f}%. The candidate shows particularly strong performance in key evaluation areas, with solid technical skills ({scores['skills']:.1f}%) and relevant experience ({scores['experience']:.1f}%). The profile suggests a well-rounded professional with the necessary competencies to excel in this position. Recommendation: Strong candidate for further consideration and interview."

    elif overall_score >= 55:
        best_category = max(scores, key=scores.get)
        reasoning = f"This candidate shows moderate alignment with the role requirements, achieving an overall match score of {overall_score:.1f}%. While there are some areas of strength, particularly in {best_category.replace('_', ' ')} ({scores[best_category]:.1f}%), there are also notable gaps in other critical areas. The candidate may require additional assessment to determine if they can bridge these gaps through training or on-the-job learning. Recommendation: Consider for interview with focus on addressing identified gaps."

    else:
        weak_areas = sorted(scores.items(), key=lambda x: x[1])[:3]
        weak_names = ', '.join([k.replace('_', ' ') for k, v in weak_areas])
        reasoning = f"This candidate shows limited alignment with the role requirements, achieving an overall match score of {overall_score:.1f}%. Significant gaps exist in multiple critical areas including {weak_names}. These gaps suggest the candidate may not currently possess the necessary foundation for success in this role. Recommendation: Not recommended for this position at this time; consider for alternative roles or future opportunities after skill development."

    return reasoning


def determine_candidate_tier(overall_score, scores, ai_reasoning):
    """
    Determine candidate tier with consistent labeling.
    Returns one of: TOP, BEST, MODERATE, LOW, VERY_LOW
    """
    # === Primary logic based on overall score ===
    if overall_score >= 80:
        candidate_tier = "TOP"
    elif overall_score >= 60:
        candidate_tier = "BEST"
    elif overall_score >= 40:
        candidate_tier = "MODERATE"
    elif overall_score >= 20:
        candidate_tier = "LOW"
    else:
        candidate_tier = "VERY_LOW"

    # === Critical category safeguard ===
    critical_scores = ['skills', 'tools', 'experience']
    critical_avg = sum(scores.get(key, 0) for key in critical_scores) / len(critical_scores)

    # Downgrade if key categories are weak
    if critical_avg < 50 and candidate_tier in ("TOP", "BEST"):
        candidate_tier = "MODERATE"
    elif critical_avg < 30 and candidate_tier == "MODERATE":
        candidate_tier = "LOW"

    # === AI Reasoning adjustment (only if strong indicator) ===
    if ai_reasoning:
        reasoning_lower = ai_reasoning.lower()

        # Promote only if *clearly* mentioned “strong hire” or “excellent fit”
        if "strong hire" in reasoning_lower or "excellent fit" in reasoning_lower:
            if overall_score >= 70:
                candidate_tier = "TOP"
            elif overall_score >= 60:
                candidate_tier = "BEST"

        # Downgrade if explicitly says not recommended
        elif "not recommended" in reasoning_lower or "poor fit" in reasoning_lower or "limited alignment" in reasoning_lower:
            if overall_score < 50:
                candidate_tier = "LOW"
            else:
                candidate_tier = "MODERATE"

    return candidate_tier


def extract_strengths_weaknesses(scores, weights, jd_data, resume_data):
    """Extract strengths and weaknesses based on scores"""
    strengths = []
    weaknesses = []

    for category, score in scores.items():
        weight = weights.get(category, 0)
        category_name = category.replace('_', ' ').title()

        # High performing areas (>75% and weight >10%)
        if score >= 75 and weight >= 10:
            strengths.append(f"Strong {category_name} match ({score:.0f}%)")

        # Low performing critical areas (<50% and weight >10%)
        if score < 50 and weight >= 10:
            weaknesses.append(f"Gap in {category_name} ({score:.0f}%)")

    # Add specific strengths
    if scores.get('skills', 0) >= 70:
        jd_skills_set = set([s.lower() for s in jd_data.get('required_skills', {}).get('technical_skills', [])])
        resume_skills_set = set([s.lower() for s in resume_data.get('skills', {}).get('technical_skills', [])])
        matched_skills = len(jd_skills_set.intersection(resume_skills_set))

        if matched_skills > 0:
            strengths.append(f"Matches {matched_skills} required technical skills")

    # Add specific weaknesses
    if scores.get('experience', 0) < 60:
        jd_exp = extract_years(jd_data.get('experience', {}).get('required_years', '0'))
        resume_exp = extract_years(resume_data.get('experience', {}).get('total_experience', '0'))
        if resume_exp < jd_exp:
            weaknesses.append(f"Experience gap: {resume_exp:.1f} years vs {jd_exp:.1f} required")

    if not strengths:
        strengths = ["Meets basic requirements"]

    if not weaknesses:
        weaknesses = ["No significant gaps identified"]

    return strengths[:5], weaknesses[:5]


def evaluate_skills(jd_data, resume_data, rubrics_config):
    """Evaluate technical skills match"""
    try:
        jd_skills = jd_data.get('required_skills', {}).get('technical_skills', [])
        resume_skills = resume_data.get('skills', {}).get('technical_skills', [])

        all_jd_skills = set([s.lower().strip() for s in jd_skills])
        all_resume_skills = set([s.lower().strip() for s in resume_skills])

        if not all_jd_skills:
            return 50.0

        matched_skills = all_jd_skills.intersection(all_resume_skills)
        match_percentage = (len(matched_skills) / len(all_jd_skills)) * 100

        return round(min(match_percentage, 100), 2)

    except Exception as e:
        print(f"Skills evaluation error: {e}")
        return 50.0


def evaluate_tools(jd_data, resume_data, rubrics_config):
    """Evaluate tools and technologies match"""
    try:
        jd_tools = jd_data.get('required_skills', {}).get('tools', [])
        resume_tools = resume_data.get('skills', {}).get('tools', [])

        all_jd_tools = set([t.lower().strip() for t in jd_tools])
        all_resume_tools = set([t.lower().strip() for t in resume_tools])

        if not all_jd_tools:
            return 50.0

        matched_tools = all_jd_tools.intersection(all_resume_tools)
        match_percentage = (len(matched_tools) / len(all_jd_tools)) * 100

        return round(min(match_percentage, 100), 2)

    except Exception as e:
        print(f"Tools evaluation error: {e}")
        return 50.0


def evaluate_experience(jd_data, resume_data, rubrics_config):
    """Evaluate experience match"""
    try:
        jd_exp = jd_data.get('experience', {}).get('required_years', '0')
        resume_exp = resume_data.get('experience', {}).get('total_experience', '0')

        jd_years = extract_years(jd_exp)
        resume_years = extract_years(resume_exp)

        if jd_years == 0:
            return 100.0 if resume_years <= 1 else 80.0

        if resume_years >= jd_years:
            return 100.0
        elif resume_years >= jd_years * 0.8:
            return 85.0
        elif resume_years >= jd_years * 0.6:
            return 70.0
        elif resume_years >= jd_years * 0.4:
            return 50.0
        else:
            return 30.0

    except Exception as e:
        print(f"Experience evaluation error: {e}")
        return 50.0


def evaluate_education(jd_data, resume_data, rubrics_config):
    """Evaluate education match"""
    try:
        criteria = rubrics_config.get('education_criteria', {})
        scoring = criteria.get('scoring', {})
        is_mandatory = criteria.get('is_mandatory', False)

        if not resume_data.get('education'):
            return 0.0 if is_mandatory else 30.0

        highest_degree = resume_data.get('education', [{}])[0].get('degree', '').lower()

        if 'phd' in highest_degree or 'doctorate' in highest_degree:
            return scoring.get('phd', 100)
        elif 'master' in highest_degree or 'mtech' in highest_degree or 'm.tech' in highest_degree:
            return scoring.get('masters', 90)
        elif 'bachelor' in highest_degree or 'btech' in highest_degree or 'b.tech' in highest_degree or 'b.e' in highest_degree:
            return scoring.get('bachelors', 80)
        elif 'diploma' in highest_degree:
            return scoring.get('diploma', 60)
        else:
            return scoring.get('other', 40)

    except Exception as e:
        print(f"Education evaluation error: {e}")
        return 50.0


def evaluate_projects(jd_data, resume_data, rubrics_config):
    """Evaluate projects"""
    try:
        criteria = rubrics_config.get('projects_criteria', {})
        projects = resume_data.get('projects', [])
        project_count = len(projects)

        min_projects = criteria.get('minimum_projects', 2)

        if project_count == 0:
            return 0.0
        elif project_count >= min_projects + 3:
            return 100.0
        elif project_count >= min_projects:
            return 80.0
        else:
            return (project_count / min_projects) * 60

    except Exception as e:
        print(f"Projects evaluation error: {e}")
        return 50.0


def evaluate_certifications(jd_data, resume_data, rubrics_config):
    """Evaluate certifications"""
    try:
        criteria = rubrics_config.get('certifications_criteria', {})
        is_required = criteria.get('required', False)

        certifications = resume_data.get('certifications', [])
        cert_count = len(certifications)

        if cert_count == 0:
            return 0.0 if is_required else 30.0
        elif cert_count >= 4:
            return 100.0
        elif cert_count >= 2:
            return 75.0
        else:
            return 50.0

    except Exception as e:
        print(f"Certifications evaluation error: {e}")
        return 50.0


def evaluate_profile_quality(jd_data, resume_data, rubrics_config):
    """Evaluate LinkedIn/GitHub/Portfolio presence and role fit"""
    try:
        profile_quality = resume_data.get('profile_quality', {})

        # Profile presence score (50%)
        profile_score = 0
        if profile_quality.get('has_linkedin'):
            profile_score += 20
        if profile_quality.get('has_github'):
            profile_score += 20
        if profile_quality.get('has_portfolio'):
            profile_score += 10

        # Role fit score (50%)
        jd_roles = set([r.lower() for r in jd_data.get('experience', {}).get('required_roles', [])])
        resume_roles = set([c.get('role', '').lower() for c in resume_data.get('experience', {}).get('companies', [])])

        role_score = 0
        if jd_roles:
            matched_roles = len(jd_roles.intersection(resume_roles))
            role_score = (matched_roles / len(jd_roles)) * 50
        else:
            role_score = 25

        total_score = profile_score + role_score
        return round(min(total_score, 100.0), 2)

    except Exception as e:
        print(f"Profile quality evaluation error: {e}")
        return 50.0


def extract_years(exp_string):
    """Extract years from experience string"""
    try:
        years_match = re.findall(r'(\d+)\s*(?:year|yr)', str(exp_string).lower())
        months_match = re.findall(r'(\d+)\s*(?:month|mon)', str(exp_string).lower())

        years = int(years_match[0]) if years_match else 0
        months = int(months_match[0]) if months_match else 0

        total_years = years + (months / 12)
        return total_years

    except:
        numbers = re.findall(r'\d+', str(exp_string))
        return int(numbers[0]) if numbers else 0


def generate_score_breakdown(scores, weights):
    """Generate detailed score breakdown"""
    breakdown = []

    for category, score in scores.items():
        weight = weights.get(category, 0)
        weighted_contribution = (score * weight) / 100

        breakdown.append({
            'category': category.replace('_', ' ').title(),
            'score': round(score, 2),
            'weight': weight,
            'contribution': round(weighted_contribution, 2)
        })

    return breakdown


def rank_candidates(evaluation_results):
    """Rank candidates based on overall scores"""
    sorted_results = sorted(
        evaluation_results,
        key=lambda x: x['overall_score'],
        reverse=True
    )

    for rank, result in enumerate(sorted_results, 1):
        result['rank'] = rank

    return sorted_results