import os
import json
import base64
import io

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError(
        "DEEPSEEK_API_KEY is not set in the .env file"
    )


# ============================================================
# CREATE DEEPSEEK CLIENT
# ============================================================

client = OpenAI(
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com"
)

MODEL_NAME = "deepseek-flash"


# ============================================================
# MEAL ANALYSIS FUNCTION
# ============================================================

def analyze_meal(
    image_bytes: bytes,
    mime_type: str,
    user,
    health_profile,
    user_comment: str | None = None,
    daily_nutrition_context: dict | None = None
):

    # --------------------------------------------------------
    # CONVERT UPLOADED IMAGE TO JPEG
    # --------------------------------------------------------

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=90
    )

    jpeg_bytes = buffer.getvalue()


    # --------------------------------------------------------
    # CONVERT IMAGE INTO BASE64
    # --------------------------------------------------------

    base64_image = base64.b64encode(
        jpeg_bytes
    ).decode("utf-8")


    # --------------------------------------------------------
    # CLEAN OPTIONAL USER COMMENT
    # --------------------------------------------------------

    cleaned_user_comment = (
        user_comment.strip()
        if user_comment and user_comment.strip()
        else None
    )


    if cleaned_user_comment:

        meal_context = f"""
USER-PROVIDED MEAL CONTEXT:

{cleaned_user_comment}

The user provided this information about the meal.

Use it as additional context for understanding ingredients,
preparation methods, quantities, or circumstances that may
not be visible in the image.

Examples include oil, ghee, butter, sugar, cream, coconut,
nuts, sauces, spices, blended ingredients, cooking methods,
or information about where/why the meal is being eaten.

IMPORTANT:

- The image and user comment must be considered together.
- Do not ignore relevant ingredients explicitly mentioned
  by the user merely because they are not visually visible.
- If the user gives a useful quantity such as "2 tsp oil",
  use it when estimating nutrition.
- Do not invent quantities that the user did not provide.
- If the comment only describes the situation, such as a
  party or buffet, do not invent additional foods from it.
- Do not treat the user's comment as a medical diagnosis.
"""

    else:

        meal_context = """
USER-PROVIDED MEAL CONTEXT:

No additional meal information was provided.

Analyze the meal using the image and available user profile.
"""


    # --------------------------------------------------------
    # FOOD REGION CONTEXT
    # --------------------------------------------------------

    food_region = (
        getattr(
            health_profile,
            "food_region",
            None
        )
        or "Not specified"
    )

    food_region = str(
        food_region
    ).strip()

    if not food_region:
        food_region = "Not specified"


    # --------------------------------------------------------
    # WOMEN'S HEALTH CONTEXT
    # --------------------------------------------------------

    women_health_condition = (
        health_profile.women_health_condition
        if getattr(
            health_profile,
            "women_health_condition",
            None
        )
        else "none"
    )

    women_health_condition = (
        str(women_health_condition)
        .lower()
        .strip()
    )

    women_health_labels = {
        "none": "None",
        "pcos": "PCOS",
        "menstrual_wellness": "Menstrual Wellness",
        "pregnancy": "Pregnancy",
        "breastfeeding": "Breastfeeding",
    }

    women_health_text = (
        women_health_labels.get(
            women_health_condition,
            "None"
        )
    )


    # --------------------------------------------------------
    # WOMEN'S HEALTH FEEDBACK INSTRUCTIONS
    # --------------------------------------------------------

    if women_health_condition == "pcos":

        women_health_instructions = """
The user selected PCOS as health context.

When relevant to the visible meal, consider:

- protein balance
- fiber
- vegetables
- whole fruits
- minimally processed carbohydrate sources
- overall carbohydrate quality
- balanced portions

Do not automatically label carbohydrates as bad.

Do not claim that reducing carbohydrates treats PCOS.

Do not claim that any food treats, reverses,
prevents or cures PCOS.

Do not diagnose PCOS.

Keep the feedback focused on general nutrition
and meal balance.
"""

    elif women_health_condition == "menstrual_wellness":

        women_health_instructions = """
The user selected Menstrual Wellness as health context.

When relevant to the visible meal, consider general
nutritional balance including appropriate sources of:

- iron
- protein
- fiber
- magnesium-containing foods
- fruits
- vegetables

Where appropriate, vitamin-C-containing foods can be
suggested alongside plant-based iron sources.

Do not assume the user has anemia.

Do not assume a vitamin or mineral deficiency.

Do not diagnose menstrual disorders.

Do not claim that a food treats menstrual symptoms
or hormonal conditions.
"""

    elif women_health_condition == "pregnancy":

        women_health_instructions = """
IMPORTANT: The user selected Pregnancy.

Meal feedback must be conservative.

Do NOT encourage:

- aggressive calorie restriction
- intentional rapid weight loss
- extreme carbohydrate restriction
- fasting
- highly restrictive diets

When relevant, consider balanced intake and appropriate
food sources of:

- protein
- iron
- folate
- calcium
- fiber
- fruits
- vegetables

Also consider basic pregnancy food safety.

Do not recommend raw or undercooked meat, seafood,
or eggs.

Do not recommend unpasteurized dairy products.

Do not recommend alcohol.

Do not recommend supplements or supplement doses.

Do not diagnose pregnancy complications.

Do not claim that food can treat, prevent or cure
pregnancy-related medical conditions.

Keep recommendations suitable for general wellness only.
"""

    elif women_health_condition == "breastfeeding":

        women_health_instructions = """
IMPORTANT: The user selected Breastfeeding.

Meal feedback must be conservative.

Do NOT encourage:

- aggressive calorie restriction
- rapid weight loss
- fasting
- highly restrictive diets

When relevant, consider:

- balanced energy intake
- adequate protein
- fruits
- vegetables
- whole grains where appropriate
- healthy fat sources
- hydration
- calcium-containing foods where appropriate
- iron-containing foods where appropriate

Do not recommend supplements or supplement doses.

Do not claim that a specific food will increase,
guarantee or medically alter breast-milk supply.

Do not claim that foods treat postpartum or
breastfeeding-related conditions.

Keep recommendations suitable for general wellness only.
"""

    else:

        women_health_instructions = """
No specific women's health condition has been selected.

Do not introduce special women's-health assumptions
or restrictions into the feedback.
"""


    # --------------------------------------------------------
    # BUILD USER CONTEXT
    # --------------------------------------------------------

    user_context = f"""
USER INFORMATION:

Age: {user.age}
Gender: {user.gender}
Height: {user.height_cm} cm
Weight: {user.weight_kg} kg


HEALTH PROFILE:

BMI: {health_profile.bmi}

Blood Pressure:
Systolic: {health_profile.systolic_bp}
Diastolic: {health_profile.diastolic_bp}

Blood Sugar:
{health_profile.blood_sugar_mg_dl} mg/dL

Thyroid Status:
{health_profile.thyroid_status}

Activity Level:
{health_profile.activity_level}

Diet Preference:
{health_profile.diet_preference}

State / Food Region:
{food_region}

Goal:
{health_profile.goal}

Women's Health Context:
{women_health_text}
"""


    # --------------------------------------------------------
    # DAILY NUTRITION / ADAPTIVE CONTEXT
    # --------------------------------------------------------

    if (
        daily_nutrition_context
        and daily_nutrition_context.get("available")
    ):
        targets = (
            daily_nutrition_context.get("targets")
            or {}
        )

        consumed_before = (
            daily_nutrition_context.get(
                "consumed_before_meal"
            )
            or {}
        )

        planned_meals = (
            daily_nutrition_context.get(
                "planned_meals"
            )
            or []
        )

        daily_context_text = f"""
============================================================
TODAY'S NUTRITION CONTEXT
============================================================

MealMind has already tracked the user's nutrition from meals
analyzed earlier today.

IMPORTANT:
The consumed values below DO NOT include the current uploaded
meal. You are analyzing the current meal now.

DAILY TARGETS:

Calories: {targets.get("calories", 0)} kcal
Protein: {targets.get("protein_g", 0)} g
Carbohydrates: {targets.get("carbohydrates_g", 0)} g
Fat: {targets.get("fat_g", 0)} g
Fiber: {targets.get("fiber_g", 0)} g


CONSUMED BEFORE CURRENT MEAL:

Calories: {consumed_before.get("calories", 0)} kcal
Protein: {consumed_before.get("protein_g", 0)} g
Carbohydrates: {consumed_before.get("carbohydrates_g", 0)} g
Fat: {consumed_before.get("fat_g", 0)} g
Fiber: {consumed_before.get("fiber_g", 0)} g


ORIGINAL ONE-DAY MEAL PLAN:

{json.dumps(planned_meals, ensure_ascii=False)}


ADAPTIVE GUIDANCE INSTRUCTIONS:

After estimating the nutrition of the CURRENT uploaded meal:

1. Add the current meal's estimated nutrition to the
   consumed-before-current-meal values.

2. Compare the resulting totals against the daily targets.

3. Consider the remaining planned meals only as a soft guide.

4. Produce a very short "rest_of_day_advice".

5. The advice should normally be 1-2 concise sentences.

6. Focus only on the most useful adjustment for the remainder
   of today.

7. If calories, carbohydrates or fat are already relatively
   high, suggest keeping the remaining food lighter where
   appropriate.

8. If protein or fiber are still relatively low, prioritize
   suitable protein, vegetables, fruit, legumes, or other
   appropriate foods.

9. Do NOT tell the user to completely skip dinner or another
   normal meal merely because they ate more than planned.

10. Do NOT recommend fasting, purging, excessive exercise,
    extreme calorie restriction, or other compensatory
    behavior.

11. Do NOT shame the user for eating at a party, buffet,
    restaurant, celebration, or for having an extra meal.

12. Do not repeat all dashboard nutrition numbers in the
    advice unless a number is genuinely useful.

13. Use the user's health profile and women's health context
    conservatively when relevant.

14. The original meal plan is guidance, not a rigid rule.
"""

    else:

        daily_context_text = """
============================================================
TODAY'S NUTRITION CONTEXT
============================================================

No daily nutrition target context is available.

Set "rest_of_day_advice" to null.

Do not invent daily targets or previously consumed nutrition.
"""


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a food analysis and personalized meal-feedback
system for an AI Dietplan Assistant called MealMind.

Analyze the uploaded meal image.

The following information belongs to the user who is
planning to eat this meal:

{user_context}


============================================================
USER MEAL CONTEXT
============================================================

{meal_context}


{daily_context_text}


============================================================
CONTEXT PRIORITY
============================================================

When identifying the meal, use information in this order:

1. Visual evidence from the uploaded meal image
2. Explicit information in the user's meal comment
3. State / Food Region as supporting context

The user's State / Food Region is:

{food_region}

Food region is ONLY supporting context.

Do not identify a food solely because it is common in
the user's selected region.

The image remains the primary source for visible foods.

If the user's comment explicitly identifies an ingredient
or preparation detail that cannot be seen in the image,
the comment may provide additional evidence.

Regional context may help when:

- two visually similar foods or dishes are plausible
- a regional dish name is more appropriate
- terminology differs between regions
- the visual appearance is consistent with a familiar
  regional preparation

For example, a similar food may have different familiar
names across different states.

Use the terminology that is natural for the user's region
when the visual evidence supports it.

Do NOT:

- invent regional foods that are not supported by the image
- assume the user eats a food merely because it is common
  in their state
- change a clearly identified food into a regional dish
  without visual or user-comment evidence
- allow regional assumptions to override explicit
  information provided by the user

If State / Food Region is "Not specified", analyze the meal
without making assumptions about regional background.


============================================================
HOW TO USE IMAGE + USER COMMENT
============================================================

The meal image is the primary source for identifying
visible food and estimating visible portions.

The optional user comment provides additional information
that may not be visually detectable.

For example, a user may tell you that:

- oil or ghee was used
- sugar was added
- cream was added
- coconut was used
- peanuts or cashews were blended into a curry
- butter was used
- a sauce contains additional ingredients
- ingredients were mixed or blended together
- a particular cooking method was used
- the meal is an extra meal at a party or buffet

When relevant, incorporate these details into the
nutrition estimate and personalized feedback.

If an explicitly mentioned ingredient contributes
meaningful calories or macronutrients, account for it
in the food analysis and meal total where reasonably
possible.

Do not double-count an ingredient if it is already
clearly represented in another estimated food item.

User-provided context improves the estimate but does not
make the nutrition calculation exact.


============================================================
PART 1 — MEAL ANALYSIS
============================================================

Identify every clearly visible food item.

Also account for nutritionally meaningful ingredients
explicitly mentioned by the user when they are part of
the meal but may not be visually distinguishable.

For EACH relevant food item or meaningful added
ingredient provide:

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

For an ingredient explicitly mentioned by the user that
cannot reasonably have its own visible bounding box,
use:

[0, 0, 0, 0]

Do not fabricate a bounding box for a hidden ingredient.


============================================================
PART 2 — PERSONALIZED FEEDBACK
============================================================

After analyzing the meal, provide a SHORT, CLEAN and
STRUCTURED explanation for the end user.

Use relevant user-provided meal context when it improves
the feedback.

The user's food region may influence terminology or
practical suggestions when appropriate, but it should
not dominate the nutritional feedback.

IMPORTANT:

Do NOT provide long lists.

Do NOT provide multiple recommendations.

Do NOT write a long nutrition report.

Do NOT repeat the same information across sections.

The personalized feedback MUST contain exactly these
six sections:

1. meal_overview
2. whats_good
3. what_to_consider
4. suggestion
5. healthy_add_on
6. overall


------------------------------------------------------------
1. MEAL OVERVIEW
------------------------------------------------------------

Write ONE sentence.

Mention:

- total estimated calories
- protein
- carbohydrates
- fat
- fiber

Example style:

"This meal provides approximately 620 kcal, with 32g
protein, 72g carbohydrates, 20g fat, and 9g fiber."


------------------------------------------------------------
2. WHAT'S GOOD
------------------------------------------------------------

Write a maximum of TWO short sentences.

Mention the strongest nutritional positives of this meal.

Focus on things such as:

- protein
- fiber
- vegetables
- nutrient balance

Do not list every positive feature.


------------------------------------------------------------
3. WHAT TO CONSIDER
------------------------------------------------------------

Write a maximum of TWO short sentences.

Mention ONLY the most important nutritional concern
or adjustment.

Relate it to the user's goal when appropriate.

Also consider the selected women's health context
when directly relevant.

Consider relevant user-provided meal context when it
changes the nutritional interpretation.

Use positive or neutral language.

Avoid alarming or judgmental language.


------------------------------------------------------------
4. SUGGESTION
------------------------------------------------------------

Write ONE short practical recommendation.

Do not provide a list of recommendations.

The recommendation may consider the user's goal,
health profile, women's health context, food region,
and user-provided meal context when relevant.

Regional preference should improve practicality and
familiarity, but nutritional appropriateness comes first.


------------------------------------------------------------
5. HEALTHY ADD-ON
------------------------------------------------------------

Recommend ONE suitable fresh fruit or vegetable based on:

- the user's goal
- the user's health profile
- the women's health context when relevant
- the current meal
- nutrients that could be improved
- regional familiarity when useful

The recommendation must make nutritional sense for this
specific user and this specific meal.

Regional familiarity is secondary to the nutritional
reason for the recommendation.

Do not recommend something merely because it is associated
with the user's selected state.

Briefly explain WHY the recommended fruit or vegetable
could be a useful addition.

Keep this section to a maximum of TWO short sentences.

Use a positive, natural and supportive tone.

Do not make this section sound like an advertisement.

Do not recommend a fruit or vegetable only because it is
available for purchase.

The health/nutrition reason must come first.

End naturally by mentioning that the user can find fresh
fruits and vegetables on Freshioz.

Example style:

"Adding guava could provide extra fiber and vitamin C while
keeping the addition relatively light. You can find fresh
fruits and vegetables like this on Freshioz."

Do not claim that a fruit or vegetable can treat, cure,
control, or prevent a medical condition.


------------------------------------------------------------
6. OVERALL
------------------------------------------------------------

Write ONE short concluding sentence.

Give a balanced overall assessment of the meal and its
alignment with the user's goal and relevant health context.


============================================================
WOMEN'S HEALTH PERSONALIZATION
============================================================

Selected Women's Health Context:

{women_health_text}

{women_health_instructions}


============================================================
MEDICAL SAFETY RULES
============================================================

Health information is provided only for general
nutrition personalization.

Do not diagnose medical conditions.

Do not infer that a user has a disease from a single
blood pressure or blood sugar measurement.

Do not recommend medications.

Do not recommend starting, stopping or changing
medications.

Do not claim that foods can treat, reverse, prevent
or cure diseases.

Do not prescribe therapeutic diets.

For pregnancy and breastfeeding, be especially
conservative.

Do not present image-based nutrition estimates as
medical measurements.

Do not recommend compensatory fasting or completely
skipping later meals simply because the user reports
eating more than planned.

If the user mentions overeating, a party, buffet, or an
extra meal, give balanced and non-judgmental feedback.

When today's nutrition context is available, use it to
provide balanced rest-of-day guidance without extreme
compensation.


============================================================
REST OF TODAY GUIDANCE
============================================================

When today's nutrition context is available:

- First estimate the current meal normally.
- Add the current meal estimate to the nutrition already
  consumed before this meal.
- Compare the combined values with the daily targets.
- Use the original meal plan only as a soft guide.
- Return "rest_of_day_advice" as 1-2 concise sentences.
- Focus on the most useful adjustment for the rest of today.
- Do not repeat the full dashboard nutrition values.
- Do not recommend fasting or skipping normal meals.
- Do not recommend extreme compensation for overeating.

When today's nutrition context is NOT available:

- Set "rest_of_day_advice" to null.
- Do not invent daily targets.
- Do not invent previous meals.


============================================================
FEEDBACK STYLE RULES
============================================================

The final feedback should be short and easy to understand.

STRICT RULES:

- Do not make the feedback unnecessarily long.
- Do not add additional feedback sections.
- Do not return arrays for personalized feedback.
- Do not give multiple alternatives in the suggestion.
- Recommend only ONE primary fruit or vegetable in
  healthy_add_on.
- Do not repeat the complete health profile.
- Use positive or neutral language.
- Keep explanations easy for a normal user to understand.
- Consider BP, blood sugar and thyroid information only
  when directly relevant.
- Consider women's health information only when directly
  relevant.
- Consider user-provided meal context only when relevant.
- Consider food region only when it genuinely improves
  identification, terminology or practicality.
- Do not diagnose medical conditions.
- Do not recommend medications.
- Do not claim that food can treat or cure a disease.


============================================================
GENERAL MEAL ANALYSIS RULES
============================================================

- Do not identify plates, spoons, glasses, tables,
  or other non-food objects.

- Do not invent visible foods that are not supported
  by the image.

- Ingredients explicitly stated by the user may be
  incorporated even when they are hidden inside the dish.

- Distinguish between something the user says was actually
  used and something they merely ask about.

- Estimate the edible portion.

- Nutrition values must correspond to the estimated portion.

- Calories must be in kcal.

- Protein, carbohydrates, fat and fiber must be in grams.

- Use realistic nutrition estimates.

- meal_total should be consistent with individual foods.

- Image-based portion and nutrition values are estimates,
  not exact measurements.

- User-described quantities are also approximate unless
  the user provides an exact quantity.

- If uncertain about a visible food, use a general food name
  rather than inventing a specific regional dish.

- Regional context may increase confidence only when it is
  consistent with visual evidence or the user's comment.

- Return valid JSON only.

- Do not add any text before or after the JSON.


============================================================
REQUIRED JSON FORMAT
============================================================

Return JSON in exactly this structure:

{{
    "foods": [
        {{
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
        }}
    ],

    "meal_total": {{
        "calories": 0,
        "protein_g": 0,
        "carbohydrates_g": 0,
        "fat_g": 0,
        "fiber_g": 0
    }},

    "personalized_feedback": {{
        "meal_overview": "...",
        "whats_good": "...",
        "what_to_consider": "...",
        "suggestion": "...",
        "healthy_add_on": "...",
        "overall": "..."
    }},

    "rest_of_day_advice": "..."
}}

IMPORTANT:

If today's nutrition context is available,
"rest_of_day_advice" must contain 1-2 concise sentences.

If today's nutrition context is NOT available,
"rest_of_day_advice" must be null.
"""


    # --------------------------------------------------------
    # SEND IMAGE + ALL CONTEXT TO DEEPSEEK
    # --------------------------------------------------------

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",

                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url":
                            f"data:image/jpeg;base64,{base64_image}",

                            "detail": "high"
                        }
                    }
                ]
            }
        ],

        response_format={
            "type": "json_object"
        }
    )


    # --------------------------------------------------------
    # GET RESPONSE
    # --------------------------------------------------------

    raw_text = (
        response
        .choices[0]
        .message
        .content
    )

    if not raw_text:
        raise ValueError(
            "DeepSeek returned an empty response"
        )


    # --------------------------------------------------------
    # CONVERT JSON STRING → PYTHON DICTIONARY
    # --------------------------------------------------------

    try:

        result = json.loads(
            raw_text
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "DeepSeek returned invalid JSON"
        ) from e


    return result