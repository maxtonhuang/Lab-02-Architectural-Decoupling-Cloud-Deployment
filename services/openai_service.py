import re

from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

# Initialize the OpenAI client using the key loaded from config.py
client = OpenAI(api_key=OPENAI_API_KEY)

# System instruction defining the strict output contract
SYSTEM_PROMPT = (
    "You are a database-integrated text processing utility. Analyze the user text data. "
    "You MUST output your response in a strict formatted style containing two sections:\n"
    "1. A bulleted summary synthesized from the reviews.\n"
    "2. A standalone single line stating exactly: 'FINAL_RATING: X' (where X is an integer score from 0 to 10).\n\n"
    "Keep your response analytical and professional."
)


def analyze_review_sentiment(review_content):
    """Queries the OpenAI model, parses the rating and category, and returns the result.

    Returns a dictionary with keys: summary, rating, category.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": review_content},
        ],
        temperature=0.1,
    )

    raw_output = response.choices[0].message.content

    # PARSING LOGIC: Extract score metrics from the structural marker
    rating = 5  # Safe default fallback score if parsing fails
    clean_summary = raw_output

    if "FINAL_RATING:" in raw_output:
        # Everything before the first marker is the summary body.
        marker_index = raw_output.find("FINAL_RATING:")
        clean_summary = raw_output[:marker_index].strip()
        tail = raw_output[marker_index + len("FINAL_RATING:"):]

        # Take the first integer that appears after the marker, then clamp to 0-10.
        # Safely handles "8", "8/10", "9 out of 10", surrounding markdown such as
        # **9**, a stray newline before the number, decimals (keeps the whole part),
        # and any trailing commentary the model adds.
        match = re.search(r"\d+", tail)
        if match:
            rating = max(0, min(10, int(match.group())))
        else:
            rating = 5  # No parseable number found; keep the safe default.

    # Determine the category routing bracket
    if 8 <= rating <= 10:
        category = "Good"
    elif 4 <= rating <= 7:
        category = "Average"
    else:
        category = "Bad"

    return {
        "summary": clean_summary,
        "rating": rating,
        "category": category,
    }
