import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file")


# Create Gemini client
client = genai.Client(api_key=api_key)


# Gemini model
MODEL_NAME = "gemini-3.8-flash"


def analyze_meal(image_bytes: bytes, mime_type: str):
    """
    Send a meal image to Gemini and return structured food analysis.
    """

    prompt = """
You are a food analysis system for an AI Dietplan Assistant.

Analyze the meal image carefully.

Identify every clearly visible food item.

For EACH food item provide:

1. food_name
2. approximate_portion
3. approximate_percentage_of_visible_meal
4. calories
5. protein_g
6. carbohydrates_g
7. fat_g
8. fiber_g
9. confidence_score
10. bounding_box

Bounding box format:

[x_min, y_min, x_max, y_max]

Use normalized coordinates from 0 to 1000.

Important instructions:

- Do not identify plates, spoons, glasses, tables, or other non-food objects.
- Estimate the edible portion visible in the image.
- Nutrition values should correspond to the estimated portion.
- Calories should be in kcal.
- Protein, carbohydrates, fat and fiber should be in grams.
- Keep nutrition estimates realistic.
- If a food item cannot be identified confidently, use a general food name.
- Do not invent foods that are not visible.
- The percentages should approximately represent how much of the visible meal each food occupies.

Return ONLY valid JSON.

Use exactly this structure:

{
    "foods": [
        {
            "food_name": "...",
            "approximate_portion": "...",
            "approximate_percentage_of_visible_meal": 0,
            "calories": 0,
            "protein_g": 0,
            "carbohydrates_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "confidence_score": 0.0,
            "bounding_box": [0, 0, 0, 0]
        }
    ],
    "meal_total": {
        "calories": 0,
        "protein_g": 0,
        "carbohydrates_g": 0,
        "fat_g": 0,
        "fiber_g": 0
    }
}
"""

    # Convert image bytes into a Gemini image part
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    # Send image + prompt to Gemini
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            image_part,
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    # Get Gemini's response
    raw_text = response.text.strip()

    # Remove markdown code fences if Gemini returns them
    if raw_text.startswith("```"):
        raw_text = raw_text.replace("```json", "", 1)
        raw_text = raw_text.replace("```", "", 1)
        raw_text = raw_text.strip()

    # Convert JSON string into Python dictionary
    result = json.loads(raw_text)

    return result