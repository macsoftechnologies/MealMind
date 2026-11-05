import os
import json

from dotenv import load_dotenv
from openai import OpenAI


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
# GENERATE DIET PLAN
# ============================================================

def generate_diet_plan(
    user,
    health_profile,
    nutrition_targets,
    food_allergies,
    foods_to_avoid,
    meals_per_day
):

    # --------------------------------------------------------
    # CONVERT LISTS INTO READABLE TEXT
    # --------------------------------------------------------

    allergies_text = (
        ", ".join(food_allergies)
        if food_allergies
        else "None reported"
    )

    avoid_text = (
        ", ".join(foods_to_avoid)
        if foods_to_avoid
        else "None"
    )


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

    food_region = str(food_region).strip()

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
    # USER CONTEXT
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


DIET PLAN PREFERENCES:

Food Allergies:
{allergies_text}

Foods to Avoid / Dislike:
{avoid_text}

Meals Per Day:
{meals_per_day}
"""


    # --------------------------------------------------------
    # NUTRITION TARGET CONTEXT
    # --------------------------------------------------------

    nutrition_context = f"""
ESTIMATED DAILY NUTRITION TARGETS:

BMR:
{nutrition_targets["bmr"]} kcal

TDEE:
{nutrition_targets["tdee"]} kcal

Daily Calorie Target:
{nutrition_targets["target_calories"]} kcal

Protein Target:
{nutrition_targets["protein_g"]} g

Carbohydrate Target:
{nutrition_targets["carbohydrates_g"]} g

Fat Target:
{nutrition_targets["fat_g"]} g

Fiber Target:
{nutrition_targets["fiber_g"]} g
"""


    # --------------------------------------------------------
    # WOMEN'S HEALTH INSTRUCTIONS
    # --------------------------------------------------------

    if women_health_condition == "pcos":

        women_health_instructions = """
IMPORTANT PERSONALIZATION CONTEXT:
The user has selected PCOS.

Actively apply this context when choosing the actual foods,
portions and meal combinations.

The effect should be visible in the generated meals,
not only mentioned in the daily tip.

While still respecting the user's calorie target, goal,
diet preference, allergies and foods to avoid:

- distribute protein and fiber across the day's meals
- pair carbohydrate-rich foods with protein, fiber or
  healthy fat where practical
- favor vegetables and whole fruits
- favor fiber-rich foods
- favor legumes where compatible with the diet preference
- favor nuts and seeds where appropriate
- favor unsaturated fat sources
- favor whole or minimally processed carbohydrate sources
  over highly refined carbohydrate sources
- avoid making sugary foods or refined carbohydrates major
  components of the meal plan
- use realistic portions
- maintain adequate overall nutrition for the user's goal

Do not unnecessarily eliminate carbohydrates.

Do not create an extreme or highly restrictive diet.

Do NOT claim that this diet treats, reverses or cures PCOS.

Do NOT diagnose PCOS.

Do NOT present any food as a medical treatment.
"""

    elif women_health_condition == "menstrual_wellness":

        women_health_instructions = """
IMPORTANT PERSONALIZATION CONTEXT:
The user has selected Menstrual Wellness.

Actively apply this context when choosing the actual foods,
portions and meal combinations.

The effect should be visible in the generated meals,
not only mentioned in the daily tip.

While still respecting the user's calorie target, goal,
diet preference, allergies and foods to avoid:

- include appropriate protein sources throughout the day
- include iron-containing foods where appropriate
- include magnesium-containing foods where appropriate
- include fiber-rich foods
- include fruits and vegetables
- include adequate fluids
- where suitable, pair plant-based iron sources with
  vitamin-C-containing foods
- maintain balanced carbohydrate and healthy-fat sources
- keep meals practical and nutritionally balanced

Do NOT assume the user has anemia, iron deficiency,
magnesium deficiency or another nutritional deficiency.

Do NOT claim that foods will treat menstrual symptoms,
hormonal problems or another medical condition.

Do NOT diagnose a menstrual disorder.
"""

    elif women_health_condition == "pregnancy":

        women_health_instructions = """
IMPORTANT PERSONALIZATION CONTEXT:
The user has selected Pregnancy.

Pregnancy takes priority over an ordinary weight-loss goal
when constructing the meal plan.

Actively apply pregnancy context when selecting the actual
foods, portions and meal combinations.

The effect should be visible in the generated meals,
not only mentioned in the daily tip.

The calculated calorie and macro targets are rough prototype
estimates.

Do NOT present them as medically prescribed pregnancy
requirements.

Do NOT intentionally create a calorie-restriction or
weight-loss diet during pregnancy, even if the user's
general goal says weight loss.

Prefer balanced, practical, nutrient-dense meals containing
appropriate food sources of:

- protein
- iron
- folate
- calcium
- fiber
- fruits
- vegetables
- whole grains where appropriate
- healthy fats

Maintain variety across the day's meals.

Apply basic pregnancy food-safety awareness.

Do not recommend:

- alcohol
- raw or undercooked eggs
- raw or undercooked meat
- raw or undercooked seafood
- unpasteurized dairy products
- obviously unsafe foods during pregnancy

Do NOT recommend medications.

Do NOT recommend supplements or supplement doses.

Do NOT diagnose pregnancy-related conditions.

Do NOT claim that foods can prevent, treat or cure
pregnancy complications.

Keep the plan conservative and suitable only for
general wellness guidance.

Individualized pregnancy nutrition requirements should
be discussed with a qualified healthcare professional.
"""

    elif women_health_condition == "breastfeeding":

        women_health_instructions = """
IMPORTANT PERSONALIZATION CONTEXT:
The user has selected Breastfeeding.

Actively apply breastfeeding context when choosing the
actual foods, portions and meal combinations.

The effect should be visible in the generated meals,
not only mentioned in the daily tip.

The calculated calorie and macro targets are rough prototype
estimates.

Do NOT present them as medically prescribed breastfeeding
requirements.

Do NOT intentionally create an aggressive calorie
restriction or rapid weight-loss diet.

While respecting the user's diet preference, allergies and
foods to avoid, construct balanced meals with:

- adequate protein
- fruits
- vegetables
- whole grains where appropriate
- healthy fat sources
- calcium-containing foods where appropriate
- iron-containing foods where appropriate
- fiber-rich foods
- adequate hydration

Distribute nutritious foods across the day's meals instead
of concentrating most nutrition into a single meal.

Keep meals practical and nutritionally varied.

Do NOT recommend medications.

Do NOT recommend supplements or supplement doses.

Do NOT claim that a particular food will increase,
guarantee or medically alter milk supply.

Do NOT claim that foods can treat or cure postpartum
or breastfeeding-related conditions.

Keep the advice conservative and suitable only for
general wellness guidance.

Individual requirements should be discussed with a
qualified healthcare professional when needed.
"""

    else:

        women_health_instructions = """
No specific women's health condition has been selected.

Do not add special women's-health dietary restrictions
or assumptions.

Generate the diet plan primarily from the user's goal,
diet preference, nutrition targets, health information,
allergies and foods to avoid.
"""


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the diet-plan generation component of an
AI Dietplan Assistant called MealMind.

Create a practical ONE-DAY personalized diet plan.

Use the user's profile, goal, diet preference,
state / food region, health information, food restrictions
and calculated nutrition targets.


{user_context}


{nutrition_context}


============================================================
DIET PLAN REQUIREMENTS
============================================================

Create exactly {meals_per_day} meals.

Choose appropriate meal names depending on the number
of meals requested.

For example:

3 meals:
Breakfast
Lunch
Dinner

4 meals:
Breakfast
Lunch
Snack
Dinner

5 meals:
Breakfast
Morning Snack
Lunch
Evening Snack
Dinner


For EACH meal provide:

1. meal_name
2. foods
3. portion for every food
4. estimated_calories
5. protein_g
6. carbohydrates_g
7. fat_g
8. fiber_g


============================================================
IMPORTANT NUTRITION RULES
============================================================

The complete day's meals should approximately match:

Calories:
{nutrition_targets["target_calories"]} kcal

Protein:
{nutrition_targets["protein_g"]} g

Carbohydrates:
{nutrition_targets["carbohydrates_g"]} g

Fat:
{nutrition_targets["fat_g"]} g

Fiber:
{nutrition_targets["fiber_g"]} g


The totals do not need to be mathematically exact,
but they should be reasonably close to the daily targets.

Use realistic portions.

Use common, practical foods that a normal person can
reasonably prepare or obtain.

Follow the user's diet preference.

Do not make the plan unnecessarily complicated.


============================================================
REGIONAL / CULTURAL FOOD PERSONALIZATION
============================================================

The user's selected State / Food Region is:

{food_region}

If a State / Food Region is specified:

- Prefer familiar foods, dishes, ingredients and food
  terminology from that region when nutritionally appropriate.

- Make the regional preference visible in the actual meals,
  not only in the daily tip.

- Use regional foods naturally. Do not force every food or
  every meal to be region-specific.

- Prefer foods that are realistic and commonly available to
  someone from the selected region.

- Use familiar regional terminology where appropriate.

- Regional preference is intended to improve familiarity,
  practicality and adherence to the diet plan.

- Do not assume that every person from a state eats exactly
  the same foods.

- Do not invent unusual regional dishes merely to make the
  plan appear regional.

If the State / Food Region is "Not specified", generate a
practical general Indian diet plan without making assumptions
about the user's regional background.


IMPORTANT PRIORITY ORDER:

When two preferences or constraints conflict, use this
priority order:

1. Food allergy and safety requirements
2. Health and women's-health context
3. Nutrition and calorie targets
4. Diet preference
5. Foods the user explicitly wants to avoid
6. Regional / cultural food preference

Regional food preference must NEVER override an allergy,
safety requirement, important health context, diet preference
or explicit food exclusion.


============================================================
ALLERGY RULE — VERY IMPORTANT
============================================================

Reported food allergies:

{allergies_text}

If food allergies are provided:

- NEVER intentionally include those foods.
- NEVER recommend them as optional foods.
- NEVER use them as toppings, snacks or ingredients.
- Do not suggest obvious derivatives of an explicitly
  listed allergen when they clearly contain that allergen.

Food allergies are a strict exclusion constraint.


============================================================
FOODS TO AVOID
============================================================

Foods the user dislikes or wants to avoid:

{avoid_text}

Do not intentionally include these foods in the plan.

Choose reasonable alternatives instead.


============================================================
GENERAL HEALTH INFORMATION
============================================================

Consider the supplied blood pressure, blood sugar,
thyroid status and other health information when relevant.

However:

- Do not diagnose a medical condition.
- Do not claim that a single measurement proves a disease.
- Do not recommend medications.
- Do not recommend changing medications.
- Do not claim that foods can treat or cure diseases.
- Do not make extreme dietary restrictions based only
  on the supplied information.

Keep the plan practical and supportive.


============================================================
WOMEN'S HEALTH CONTEXT
============================================================

Selected Women's Health Context:

{women_health_text}


{women_health_instructions}


============================================================
IMPORTANT SAFETY RULE
============================================================

Health information is context for general nutrition
personalization only.

Never transform MealMind into a diagnostic or medical
treatment system.

Do not claim that this meal plan treats, prevents,
reverses or cures a disease.

Do not recommend starting, stopping or changing
medications.

Do not invent medical diagnoses from the user's profile.

For pregnancy and breastfeeding, be especially
conservative and do not present estimated nutrition
targets as individualized medical requirements.


============================================================
DAILY TIP
============================================================

Provide ONE short daily_tip.

The tip should be relevant to the user's:

- goal
- diet plan
- nutrition balance
- selected food region when useful
- women's health context when applicable

Keep it to a maximum of two short sentences.

Do not provide a long explanation.

Do not make medical treatment claims.


============================================================
OUTPUT RULES
============================================================

Return valid JSON only.

Do not write Markdown.

Do not add explanations before the JSON.

Do not add explanations after the JSON.

Return JSON exactly in this structure:

{{
    "meals": [
        {{
            "meal_name": "Breakfast",

            "foods": [
                {{
                    "food_name": "...",
                    "portion": "..."
                }}
            ],

            "estimated_calories": 0,
            "protein_g": 0,
            "carbohydrates_g": 0,
            "fat_g": 0,
            "fiber_g": 0
        }}
    ],

    "daily_tip": "..."
}}
"""


    # --------------------------------------------------------
    # SEND REQUEST TO DEEPSEEK
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
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
            "DeepSeek returned an empty diet plan response"
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


    # --------------------------------------------------------
    # BASIC RESPONSE VALIDATION
    # --------------------------------------------------------

    if "meals" not in result:
        raise ValueError(
            "DeepSeek response does not contain meals"
        )

    if not isinstance(
        result["meals"],
        list
    ):
        raise ValueError(
            "DeepSeek meals must be a list"
        )

    if len(result["meals"]) != meals_per_day:
        raise ValueError(
            "DeepSeek returned an incorrect number of meals"
        )


    return result

from datetime import date, timedelta


def get_week_dates():
    today = date.today()

    # Monday of the current week
    week_start = today - timedelta(
        days=today.weekday()
    )

    week_end = week_start + timedelta(days=6)

    return week_start, week_end

# ============================================================
# GENERATE WEEKLY DIET PLAN
# ============================================================

def generate_weekly_diet_plan(
    user,
    health_profile,
    nutrition_targets,
    food_allergies,
    foods_to_avoid,
    meals_per_day
):
    # --------------------------------------------------------
    # WEEK DATES
    # --------------------------------------------------------

    week_start, week_end = get_week_dates()

    # --------------------------------------------------------
    # CONVERT LISTS TO TEXT
    # --------------------------------------------------------

    allergies_text = (
        ", ".join(food_allergies)
        if food_allergies
        else "None reported"
    )

    avoid_text = (
        ", ".join(foods_to_avoid)
        if foods_to_avoid
        else "None"
    )

    # --------------------------------------------------------
    # FOOD REGION
    # --------------------------------------------------------

    food_region = (
        getattr(
            health_profile,
            "food_region",
            None
        )
        or "Not specified"
    )

    food_region = str(food_region).strip()

    if not food_region:
        food_region = "Not specified"

    # --------------------------------------------------------
    # WOMEN'S HEALTH
    # --------------------------------------------------------

    women_health_condition = (
        getattr(
            health_profile,
            "women_health_condition",
            None
        )
        or "none"
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
    # ADDITIONAL HEALTH INFORMATION
    # --------------------------------------------------------

    additional_health_info = (
        getattr(
            health_profile,
            "additional_health_info",
            []
        )
        or []
    )

    additional_health_text = json.dumps(
        additional_health_info,
        ensure_ascii=False,
        default=str
    )

    # --------------------------------------------------------
    # SPECIAL WOMEN'S HEALTH INSTRUCTIONS
    # --------------------------------------------------------

    if women_health_condition == "pcos":

        special_health_instructions = """
The user selected PCOS.

Apply this context to the actual meals.

Prefer:
- balanced protein distribution
- fiber-rich foods
- vegetables
- whole fruits
- legumes where appropriate
- nuts and seeds where appropriate
- minimally processed carbohydrate sources

Pair carbohydrate-rich foods with protein, fiber,
or healthy fats where practical.

Do not create an extreme low-carbohydrate diet.

Do not claim that the diet treats or cures PCOS.
"""

    elif women_health_condition == "menstrual_wellness":

        special_health_instructions = """
The user selected Menstrual Wellness.

Where appropriate include:
- protein-rich foods
- iron-containing foods
- magnesium-containing foods
- fruits
- vegetables
- fiber-rich foods
- balanced carbohydrate sources
- adequate hydration

Do not assume that the user has a nutritional deficiency.

Do not claim that foods treat menstrual disorders.
"""

    elif women_health_condition == "pregnancy":

        special_health_instructions = """
The user selected Pregnancy.

Pregnancy safety takes priority over an ordinary
weight-loss goal.

Do NOT intentionally create a calorie-restriction
or weight-loss diet.

Prefer balanced nutrient-dense meals.

Where appropriate include:
- protein
- iron-containing foods
- folate-containing foods
- calcium-containing foods
- fruits
- vegetables
- fiber
- whole grains
- healthy fats

Do not recommend:
- alcohol
- raw or undercooked eggs
- raw or undercooked meat
- raw or undercooked seafood
- unpasteurized dairy products

Do not recommend medications or supplement doses.

Do not present this plan as medically prescribed
pregnancy nutrition.
"""

    elif women_health_condition == "breastfeeding":

        special_health_instructions = """
The user selected Breastfeeding.

Do not create aggressive calorie restriction.

Prefer balanced meals containing:
- adequate protein
- fruits
- vegetables
- whole grains where appropriate
- healthy fats
- calcium-containing foods where appropriate
- iron-containing foods where appropriate
- fiber-rich foods
- adequate hydration

Do not claim that foods will medically increase
or guarantee milk supply.

Do not recommend medications or supplement doses.
"""

    else:

        special_health_instructions = """
No specific women's health condition has been selected.

Use the user's normal health profile, goal,
nutrition targets and food preferences.
"""

    # --------------------------------------------------------
    # WEEKLY PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the weekly diet-plan generation component of
an AI Dietplan Assistant called MealMind.

Create a personalized SEVEN-DAY diet plan.

The plan starts on:
{week_start.isoformat()}

The plan ends on:
{week_end.isoformat()}


============================================================
USER INFORMATION
============================================================

Age:
{user.age}

Gender:
{user.gender}

Height:
{user.height_cm} cm

Weight:
{user.weight_kg} kg


============================================================
HEALTH PROFILE
============================================================

BMI:
{health_profile.bmi}

Blood Pressure:
{health_profile.systolic_bp}/{health_profile.diastolic_bp}

Blood Sugar:
{health_profile.blood_sugar_mg_dl} mg/dL

Thyroid Status:
{health_profile.thyroid_status}

Activity Level:
{health_profile.activity_level}

Diet Preference:
{health_profile.diet_preference}

Goal:
{health_profile.goal}

State / Food Region:
{food_region}

Women's Health Context:
{women_health_text}


Additional confirmed health information:

{additional_health_text}


============================================================
FOOD RESTRICTIONS
============================================================

Food Allergies:

{allergies_text}

Foods To Avoid / Dislike:

{avoid_text}


============================================================
DAILY NUTRITION TARGETS
============================================================

Target Calories:
{nutrition_targets["target_calories"]} kcal

Protein:
{nutrition_targets["protein_g"]} g

Carbohydrates:
{nutrition_targets["carbohydrates_g"]} g

Fat:
{nutrition_targets["fat_g"]} g

Fiber:
{nutrition_targets["fiber_g"]} g


============================================================
WEEKLY PLAN REQUIREMENTS
============================================================

Create exactly 7 days.

Each day must contain exactly:

{meals_per_day} meals.

Use appropriate meal names depending on the number
of meals requested.

Examples:

3 meals:
Breakfast
Lunch
Dinner

4 meals:
Breakfast
Lunch
Snack
Dinner

5 meals:
Breakfast
Morning Snack
Lunch
Evening Snack
Dinner


For every meal provide:

- meal_name
- planned_time
- foods
- portion for each food
- estimated_calories
- protein_g
- carbohydrates_g
- fat_g
- fiber_g

IMPORTANT MEAL TIMING RULES:

- Every meal MUST contain "planned_time".
- planned_time MUST use 24-hour HH:MM format.
- Example: "08:00", "13:00", "19:30".
- Choose realistic meal times according to the meal type.
- Meal times must be in chronological order during the day.
- Consider the user's number of meals per day when spacing meals.
- Do not give two meals the same planned_time.
- Breakfast should normally be in the morning.
- Lunch should normally be around midday.
- Dinner should normally be in the evening.
- Snacks should be sensibly placed between main meals.


============================================================
VERY IMPORTANT — WEEKLY VARIETY
============================================================

This is a weekly plan, not seven copies of the
same one-day plan.

Avoid unnecessarily repeating the same meals.

Provide reasonable variety across the seven days.

Some ingredients may naturally repeat, but the
overall meals should feel varied and practical.

Do not create variety by using unusual or unrealistic
foods.

Prefer foods that the user can reasonably obtain
and prepare.


============================================================
REGIONAL FOOD PERSONALIZATION
============================================================

The user's State / Food Region is:

{food_region}

When appropriate, prefer familiar foods, ingredients,
dishes and terminology from this region.

Regional personalization should be visible in the
actual weekly meals.

However, do not force every meal to be regional.

If the region is Not specified, use practical
general Indian foods.

Regional preference must NEVER override:

1. food allergies
2. health and safety requirements
3. nutrition requirements
4. diet preference
5. foods explicitly excluded by the user


============================================================
ALLERGY SAFETY
============================================================

Reported allergies:

{allergies_text}

Food allergies are strict exclusions.

Never intentionally include a reported allergen.

Never suggest it as an optional ingredient.


============================================================
FOODS TO AVOID
============================================================

{avoid_text}

Do not intentionally include these foods.

Choose practical alternatives.


============================================================
HEALTH PERSONALIZATION
============================================================

Consider:

- blood pressure
- blood sugar
- thyroid information
- confirmed additional health information
- activity level
- user's goal

when selecting meals.

Do not diagnose medical conditions.

Do not recommend medications.

Do not recommend changing medications.

Do not claim that food treats, reverses,
prevents or cures a disease.


============================================================
WOMEN'S HEALTH PERSONALIZATION
============================================================

{special_health_instructions}


============================================================
DAILY NUTRITION BALANCE
============================================================

Each day's complete meals should approximately match:

Calories:
{nutrition_targets["target_calories"]} kcal

Protein:
{nutrition_targets["protein_g"]} g

Carbohydrates:
{nutrition_targets["carbohydrates_g"]} g

Fat:
{nutrition_targets["fat_g"]} g

Fiber:
{nutrition_targets["fiber_g"]} g

The values do not need to be mathematically exact,
but they should be reasonably close.

Do NOT treat the weekly calorie target as one large
pool.

Each individual day should remain reasonably balanced.


============================================================
DAILY TIP
============================================================

Provide one short daily_tip for every day.

Maximum two short sentences.

Make the tip relevant to that day's meals,
the user's goal or health context.

Do not make medical treatment claims.


============================================================
WEEKLY NOTE
============================================================

Provide one short weekly_note.

It should briefly explain the main nutrition strategy
for this week's plan.

Maximum three short sentences.


============================================================
OUTPUT RULES
============================================================

Return valid JSON only.

Do not use Markdown.

Do not write explanations before or after the JSON.

Return exactly this general structure:

{{
    "week_start_date": "{week_start.isoformat()}",
    "week_end_date": "{week_end.isoformat()}",

    "days": [
        {{
            "day_number": 1,
            "day_name": "Monday",
            "date": "{week_start.isoformat()}",

            "meals": [
                {{
                    "meal_name": "Breakfast",
                    
                    "planned_time": "08:00",

                    "foods": [
                        {{
                            "food_name": "...",
                            "portion": "..."
                        }}
                    ],

                    "estimated_calories": 0,
                    "protein_g": 0,
                    "carbohydrates_g": 0,
                    "fat_g": 0,
                    "fiber_g": 0
                }}
            ],

            "total_calories": 0,
            "total_protein_g": 0,
            "total_carbohydrates_g": 0,
            "total_fat_g": 0,
            "total_fiber_g": 0,

            "daily_tip": "..."
        }}
    ],

    "weekly_note": "..."
}}
"""

    # --------------------------------------------------------
    # DEEPSEEK REQUEST
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    # --------------------------------------------------------
    # RESPONSE TEXT
    # --------------------------------------------------------

    raw_text = (
        response
        .choices[0]
        .message
        .content
    )

    if not raw_text:
        raise ValueError(
            "DeepSeek returned an empty weekly diet plan"
        )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:
        result = json.loads(raw_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "DeepSeek returned invalid weekly diet plan JSON"
        ) from exc

    # --------------------------------------------------------
    # VALIDATE TOP-LEVEL STRUCTURE
    # --------------------------------------------------------

    if "days" not in result:
        raise ValueError(
            "Weekly diet plan does not contain days"
        )

    if not isinstance(result["days"], list):
        raise ValueError(
            "Weekly diet plan days must be a list"
        )

    if len(result["days"]) != 7:
        raise ValueError(
            "DeepSeek must return exactly 7 diet-plan days"
        )

    # --------------------------------------------------------
    # VALIDATE EACH DAY
    # --------------------------------------------------------

    expected_date = week_start

    for index, day_plan in enumerate(
        result["days"],
        start=1
    ):
        if not isinstance(day_plan, dict):
            raise ValueError(
                f"Weekly diet plan day {index} is invalid"
            )

        if "meals" not in day_plan:
            raise ValueError(
                f"Day {index} does not contain meals"
            )

        if not isinstance(
            day_plan["meals"],
            list
        ):
            raise ValueError(
                f"Day {index} meals must be a list"
            )

        if len(
            day_plan["meals"]
        ) != meals_per_day:
            raise ValueError(
                f"Day {index} contains an incorrect "
                f"number of meals"
            )

        # We control the date instead of trusting AI output.
        day_plan["day_number"] = index

        day_plan["date"] = (
            expected_date.isoformat()
        )

        day_plan["day_name"] = (
            expected_date.strftime("%A")
        )

        meals = day_plan.get(
            "meals",
            []
        )

        default_meal_times = {
            3: [
                "08:00",
                "13:00",
                "20:00",
            ],
            4: [
                "08:00",
                "13:00",
                "17:00",
                "20:00",
            ],
            5: [
                "08:00",
                "11:00",
                "13:30",
                "17:00",
                "20:00",
            ],
        }

        fallback_times = (
            default_meal_times.get(
                meals_per_day,
                []
            )
        )

        for meal_index, meal in enumerate(
            meals
        ):
            planned_time = meal.get(
                "planned_time"
            )

            if not is_valid_planned_time(
                planned_time
            ):
                if meal_index < len(
                    fallback_times
                ):
                    meal["planned_time"] = (
                        fallback_times[
                            meal_index
                        ]
                    )
                else:
                    meal["planned_time"] = None

        # Move to the next day ONCE.
        expected_date += timedelta(days=1)

    # --------------------------------------------------------
    # FORCE CORRECT WEEK DATES
    # --------------------------------------------------------

    result["week_start_date"] = (
        week_start.isoformat()
    )

    result["week_end_date"] = (
        week_end.isoformat()
    )

    return result


def is_valid_planned_time(value):
    if not isinstance(value, str):
        return False

    try:
        hour_text, minute_text = value.split(":")

        hour = int(hour_text)
        minute = int(minute_text)

        return (
            0 <= hour <= 23
            and 0 <= minute <= 59
            and len(hour_text) == 2
            and len(minute_text) == 2
        )

    except (ValueError, AttributeError):
        return False