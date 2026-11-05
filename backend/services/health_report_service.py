import base64
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not DEEPSEEK_API_KEY:
    raise ValueError(
        "DEEPSEEK_API_KEY is not set in the .env file"
    )


if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is not set in the .env file"
    )


# ============================================================
# AI CLIENTS
# ============================================================

deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


gemini_client = genai.Client(
    api_key=GOOGLE_API_KEY
)


DEEPSEEK_MODEL = "deepseek-flash"

GEMINI_MODEL = "gemini-3.5-flash-lite"


# ============================================================
# HEALTH REPORT EXTRACTION PROMPT
# ============================================================

HEALTH_REPORT_EXTRACTION_PROMPT = """
You are a medical/health-report information extraction system.

Your ONLY job is to read the uploaded health report and extract
information that is explicitly present in the report.

Do NOT provide medical advice.
Do NOT diagnose diseases.
Do NOT interpret results beyond what the report itself explicitly says.


============================================================
CORE EXTRACTION RULES
============================================================

1. NEVER invent, estimate, assume, or guess a value.

2. If a value is not clearly present in the report,
   return null for dedicated fields or omit it from
   additional_health_info.

3. Extract the PATIENT'S ACTUAL RESULT only.

4. NEVER mistake any of the following for the patient's result:
   - reference range
   - normal range
   - biological reference interval
   - method information
   - previous/reference values
   - example values

5. Preserve the unit exactly as shown whenever possible.

6. Only return a report flag such as:
   - High
   - Low
   - Normal
   - Borderline
   - Critical

   when the report itself explicitly states or clearly marks it.

7. If a result is unclear, unreadable, partially visible,
   or uncertain, DO NOT GUESS.

8. Missing information does NOT mean normal.

9. Do not infer a medical condition from laboratory values.

10. Do not convert one laboratory test into another.

11. Do not calculate new medical values from other values.

12. Return ONLY valid JSON.

13. Do not return markdown.

14. Do not return explanations outside the JSON.


============================================================
PRIVACY / INFORMATION TO IGNORE
============================================================

Do NOT extract administrative or identifying information such as:

- patient name
- phone number
- email
- home address
- patient ID
- hospital ID
- laboratory ID
- doctor name
- hospital/laboratory name
- billing information
- QR codes
- barcodes

Only extract information useful for the user's health,
nutrition, diet planning, or wellness context.


============================================================
DEDICATED HEALTH PROFILE FIELDS
============================================================

Some information already has dedicated fields in our
health profile.

Extract these separately when they are explicitly present.


------------------------------------------------------------
BLOOD PRESSURE
------------------------------------------------------------

Extract:

- systolic_bp
- diastolic_bp

ONLY when an actual patient blood-pressure reading is present.

Example:

120/80 mmHg

means:

"systolic_bp": 120
"diastolic_bp": 80

Do not extract blood-pressure reference ranges.


------------------------------------------------------------
BLOOD SUGAR / GLUCOSE
------------------------------------------------------------

Extract the patient's actual measured blood-glucose value
when clearly present.

Store it in:

"blood_sugar_mg_dl"

ONLY when the result is expressed in mg/dL.

Do not silently convert another unit to mg/dL.

If the glucose test type is clearly stated, preserve it in:

"blood_sugar_test_type"

Examples include:

- Fasting
- Random
- Postprandial
- PPBS
- FBS

HbA1c is NOT the same thing as a blood-glucose mg/dL result.

Therefore:

HbA1c should normally be placed inside
additional_health_info with its actual percentage value
and unit.

Never use a glucose reference range as the patient's result.


------------------------------------------------------------
THYROID
------------------------------------------------------------

Use:

"thyroid_status"

ONLY if the report explicitly provides a thyroid status or
diagnosis such as:

- Hypothyroid
- Hyperthyroid
- Euthyroid
- Normal thyroid status

If the report only contains laboratory measurements such as:

- TSH
- T3
- T4
- Free T3
- Free T4

DO NOT diagnose thyroid disease yourself.

Instead, put those measured laboratory results inside:

"additional_health_info"


============================================================
DYNAMIC ADDITIONAL HEALTH INFORMATION
============================================================

Any useful measured health result that does not belong in
the dedicated fields above should be stored inside:

"additional_health_info"

This field is DYNAMIC.

Do NOT restrict extraction only to the examples listed below.

Possible examples include:

- Hemoglobin
- Vitamin D
- Vitamin B12
- Ferritin
- Iron
- Calcium
- Sodium
- Potassium
- Magnesium
- LDL
- HDL
- Total Cholesterol
- Triglycerides
- Creatinine
- Urea
- Uric Acid
- HbA1c
- TSH
- T3
- T4
- Free T3
- Free T4
- Albumin
- Bilirubin
- AST
- ALT
- ALP
- Total Protein
- Platelet Count
- RBC
- WBC

or another clearly measured health result that may be
relevant to nutrition, diet planning, or health context.


IMPORTANT:

The examples above are NOT a fixed list.

If another useful measured health parameter is clearly
present in the report, it may also be included.


For every additional result, return:

{
    "name": "test name",
    "value": "actual patient result",
    "unit": "unit if available",
    "report_flag": "report-provided flag if available"
}


Do not create an item when there is no actual patient result.

Do not add reference ranges as separate items.

Do not duplicate a value in additional_health_info when it
has already been correctly represented in one of the
dedicated fields.


============================================================
REPORT DATE
============================================================

Extract the report/test/collection date only when it is
clearly identifiable.

Return the date as:

YYYY-MM-DD


Prefer a clinically relevant specimen collection/test/report
date over unrelated administrative dates when clearly
distinguishable.


If no reliable date is present:

"report_date": null


Do NOT use today's date.

Do NOT guess missing day, month, or year information.


============================================================
MULTIPLE RESULTS
============================================================

A report may contain many laboratory tests.

Extract every clearly visible and useful measured result,
not just the first result.


For example, if the report contains:

Hemoglobin
Vitamin D
Vitamin B12
LDL
HDL
Triglycerides
Creatinine

all useful actual patient results should be included in
additional_health_info.


============================================================
FINAL OUTPUT FORMAT
============================================================

Return EXACTLY one valid JSON object following this structure:

{
    "report_date": null,

    "systolic_bp": null,
    "diastolic_bp": null,

    "blood_sugar_mg_dl": null,
    "blood_sugar_test_type": null,

    "thyroid_status": null,

    "additional_health_info": [
        {
            "name": "",
            "value": "",
            "unit": null,
            "report_flag": null
        }
    ]
}


If there are no additional useful measured health results,
return:

"additional_health_info": []


Use null for missing dedicated values.

Never invent information simply to fill the JSON structure.

Return JSON only.
"""


# ============================================================
# IMAGE → BASE64
# ============================================================

def _encode_image(
    image_bytes: bytes,
    content_type: str
) -> str:

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{content_type};base64,{encoded}"
    )


# ============================================================
# CLEAN JSON RESPONSE
# ============================================================

def _clean_json_response(
    text: str
) -> str:

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# ============================================================
# IMAGE HEALTH REPORT → DEEPSEEK
# ============================================================

def analyze_health_report_image(
    image_bytes: bytes,
    content_type: str
) -> Dict[str, Any]:

    allowed_image_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    if content_type not in allowed_image_types:
        raise ValueError(
            "Unsupported image type. "
            "Use JPG, JPEG, PNG or WEBP."
        )


    if not image_bytes:
        raise ValueError(
            "The uploaded image is empty."
        )


    image_data = _encode_image(
        image_bytes=image_bytes,
        content_type=content_type
    )


    response = deepseek_client.chat.completions.create(
        model=DEEPSEEK_MODEL,

        messages=[
            {
                "role": "user",

                "content": [
                    {
                        "type": "text",
                        "text": HEALTH_REPORT_EXTRACTION_PROMPT
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],

        temperature=0,

        response_format={
            "type": "json_object"
        }
    )


    response_text = (
        response
        .choices[0]
        .message
        .content
    )


    if not response_text:
        raise ValueError(
            "DeepSeek returned an empty response."
        )


    cleaned = _clean_json_response(
        response_text
    )


    try:

        data = json.loads(
            cleaned
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "DeepSeek returned invalid JSON."
        ) from exc


    return _normalize_extracted_data(
        data
    )
    
    # ============================================================
# PDF HEALTH REPORT → GEMINI
# ============================================================

def analyze_health_report_pdf(
    pdf_bytes: bytes
) -> Dict[str, Any]:

    if not pdf_bytes:
        raise ValueError(
            "The uploaded PDF is empty."
        )

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,

        contents=[
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf",
            ),

            HEALTH_REPORT_EXTRACTION_PROMPT,
        ],

        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    response_text = response.text

    if not response_text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    cleaned = _clean_json_response(
        response_text
    )

    try:
        data = json.loads(
            cleaned
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    return _normalize_extracted_data(
        data
    )
    
    # ============================================================
# HEALTH REPORT ROUTER
# ============================================================

def analyze_health_report(
    file_bytes: bytes,
    content_type: str
) -> Dict[str, Any]:

    if not file_bytes:
        raise ValueError(
            "The uploaded health report is empty."
        )

    if not content_type:
        raise ValueError(
            "Could not determine the file type."
        )

    content_type = (
        content_type
        .lower()
        .strip()
    )

    # ========================================================
    # PDF → GEMINI
    # ========================================================

    if content_type == "application/pdf":

        return analyze_health_report_pdf(
            pdf_bytes=file_bytes
        )

    # ========================================================
    # IMAGE → DEEPSEEK
    # ========================================================

    allowed_image_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    if content_type in allowed_image_types:

        return analyze_health_report_image(
            image_bytes=file_bytes,
            content_type=content_type
        )

    # ========================================================
    # UNSUPPORTED
    # ========================================================

    raise ValueError(
        "Unsupported health report format. "
        "Upload PDF, JPG, JPEG, PNG or WEBP."
    )


# ============================================================
# NORMALIZE MODEL OUTPUT
# ============================================================

def _normalize_extracted_data(
    data: Dict[str, Any]
) -> Dict[str, Any]:

    normalized = {

        "report_date": data.get(
            "report_date"
        ),

        "systolic_bp": _safe_number(
            data.get(
                "systolic_bp"
            )
        ),

        "diastolic_bp": _safe_number(
            data.get(
                "diastolic_bp"
            )
        ),

        "blood_sugar_mg_dl": _safe_number(
            data.get(
                "blood_sugar_mg_dl"
            )
        ),

        "blood_sugar_test_type": (
            data.get(
                "blood_sugar_test_type"
            )
            or None
        ),

        "thyroid_status": (
            data.get(
                "thyroid_status"
            )
            or None
        ),

        "additional_health_info": []
    }


    additional_items = data.get(
        "additional_health_info"
    )


    if not isinstance(
        additional_items,
        list
    ):
        additional_items = []


    for item in additional_items:

        if not isinstance(
            item,
            dict
        ):
            continue


        name = item.get(
            "name"
        )

        value = item.get(
            "value"
        )


        if (
            not name
            or value is None
            or value == ""
        ):
            continue


        normalized[
            "additional_health_info"
        ].append(
            {

                "name": str(
                    name
                ).strip(),

                "value": str(
                    value
                ).strip(),

                "unit": (
                    str(
                        item["unit"]
                    ).strip()

                    if item.get(
                        "unit"
                    )

                    else None
                ),

                "report_flag": (
                    str(
                        item[
                            "report_flag"
                        ]
                    ).strip()

                    if item.get(
                        "report_flag"
                    )

                    else None
                )
            }
        )


    return normalized


# ============================================================
# SAFE NUMBER CONVERSION
# ============================================================

def _safe_number(
    value: Any
):

    if value is None:
        return None


    if isinstance(
        value,
        (int, float)
    ):
        return float(
            value
        )


    try:

        cleaned = (
            str(
                value
            )
            .strip()
            .replace(
                ",",
                ""
            )
        )


        return float(
            cleaned
        )


    except (
        ValueError,
        TypeError
    ):

        return None