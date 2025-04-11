# backend
from sentence_transformers import SentenceTransformer, util

# Load sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def calculate_match_score(resume_sections, job_sections):
    """
    Compares resume sections and job sections using semantic similarity.
    Returns overall match %, per-section breakdown, and improvement suggestions.
    """

    compare_keys = ["SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION"]
    total_score = 0
    total_possible = 0
    breakdown = {}
    suggestions = []

    for key in compare_keys:
        resume_text = resume_sections.get(key, "").strip()
        job_text = job_sections.get(key, "").strip()

        if resume_text and job_text:
            # Calculate cosine similarity between section pairs
            embeddings = model.encode([resume_text, job_text], convert_to_tensor=True)
            similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

            section_score = round(similarity * 100)
            breakdown[key] = f"{section_score}% match"

            total_score += section_score
            total_possible += 100

            if section_score < 50:
                suggestions.append(
                    f"Improve your {key.lower()} section to better reflect the job description."
                )
        else:
            breakdown[key] = "No data provided"
            suggestions.append(
                f"Missing or empty content in {key.lower()} section — consider adding this to your resume."
            )
            total_possible += 100

    match_percentage = round((total_score / total_possible) * 100) if total_possible else 0

    return {
        "match_score": f"{match_percentage}%",
        "breakdown": breakdown,
        "suggestions": suggestions
    }