import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";

import {
  Upload,
  ImagePlus,
  Sparkles,
  X,
  Flame,
  Dumbbell,
  Wheat,
  Droplets,
  Leaf,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
  Apple,
  ScanLine,
  Target,
  MessageSquareText,
  Clock3,
} from "lucide-react";

import api from "../services/api";


function MealAnalysis() {
  const { user: authUser } = useAuth();
  const USER_ID = authUser.id;

  const fileInputRef = useRef(null);

  const [selectedImage, setSelectedImage] =
    useState(null);

  const [previewUrl, setPreviewUrl] =
    useState("");

  const [comment, setComment] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [savingMeal, setSavingMeal] =
    useState(false);

  const [mealSaved, setMealSaved] =
    useState(false);

  const [saveMessage, setSaveMessage] =
    useState("");


  // ============================================================
  // CLEAN UP TEMPORARY IMAGE URL
  // ============================================================

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(
          previewUrl
        );
      }
    };
  }, [previewUrl]);


  // ============================================================
  // IMAGE SELECTION
  // ============================================================

  function handleImageSelect(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    if (
      !file.type.startsWith(
        "image/"
      )
    ) {
      setError(
        "Please select a valid image file."
      );

      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(
        previewUrl
      );
    }

    const newPreviewUrl =
      URL.createObjectURL(
        file
      );

    setSelectedImage(
      file
    );

    setPreviewUrl(
      newPreviewUrl
    );

    setResult(null);
    setError("");
  }


  // ============================================================
  // REMOVE IMAGE
  // ============================================================

  function removeImage() {
    if (previewUrl) {
      URL.revokeObjectURL(
        previewUrl
      );
    }

    setSelectedImage(null);
    setPreviewUrl("");

    setResult(null);
    setError("");

    if (
      fileInputRef.current
    ) {
      fileInputRef.current.value =
        "";
    }
  }


  // ============================================================
  // ANALYZE MEAL
  // ============================================================

  async function analyzeMeal() {
    if (!selectedImage) {
      setError(
        "Please upload a meal photo first."
      );

      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setResult(null);
      setMealSaved(false);
      setSaveMessage("");

      const formData =
        new FormData();


      // --------------------------------------------------------
      // MEAL IMAGE
      // --------------------------------------------------------

      formData.append(
        "image",
        selectedImage
      );


      // --------------------------------------------------------
      // OPTIONAL USER COMMENT
      // --------------------------------------------------------

      if (
        comment.trim()
      ) {
        formData.append(
          "comment",
          comment.trim()
        );
      }


      // --------------------------------------------------------
      // SAME EXISTING API REQUEST
      // --------------------------------------------------------

      const response =
        await api.post(
          `/analyze-meal?user_id=${USER_ID}`,
          formData
        );

      setResult(
        response.data
      );

    } catch (err) {
      console.error(
        "Meal analysis error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not analyze this meal. Please try again."
      );

    } finally {
      setAnalyzing(false);
    }
  }


  // ============================================================
  // SAVE MEAL
  // ============================================================

  async function saveMeal() {
    if (!result || mealSaved) {
      return;
    }

    try {
      setSavingMeal(true);
      setError("");
      setSaveMessage("");

      const response =
        await api.post(
          `/users/${USER_ID}/meals/save`,
          {
            image_filename:
              result.image_filename ||
              selectedImage?.name ||
              null,

            user_comment:
              result.user_comment ??
              (
                comment.trim()
                  ? comment.trim()
                  : null
              ),

            analysis: result,
          }
        );

      setMealSaved(true);

      setSaveMessage(
        response.data?.message ||
          "Meal saved successfully."
      );

    } catch (err) {
      console.error(
        "Save meal error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not save this meal."
      );

    } finally {
      setSavingMeal(false);
    }
  }


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="meal-analysis-page">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <section className="meal-analysis-header">

        <div>

          <p className="eyebrow">
            AI MEAL ANALYSIS
          </p>

          <h1>
            Analyze Your Meal
          </h1>

          <p>
            Upload a clear photo of your meal and
            MealMind will estimate the foods,
            portions and nutrition, then provide
            feedback based on your health profile
            and goal.
          </p>

        </div>


        <div className="meal-analysis-status">

          <ScanLine size={18} />

          AI Powered

        </div>

      </section>

      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="message-box error-message">

          <AlertCircle size={17} />

          {error}

        </div>

      )}


      {/* ======================================================
          UPLOAD CARD
      ====================================================== */}

      <section className="meal-upload-card">


        <div className="form-section-header">

          <div className="form-section-icon">

            <ImagePlus size={21} />

          </div>


          <div>

            <h2>
              Upload Meal Photo
            </h2>

            <p>
              Use a clear photo where the foods
              on your plate are visible.
            </p>

          </div>

        </div>


        {/* ==================================================
            IMAGE UPLOAD / PREVIEW
        ================================================== */}

        {!previewUrl ? (

          <button
            type="button"
            className="meal-upload-zone"
            onClick={() =>
              fileInputRef.current?.click()
            }
          >

            <div className="meal-upload-icon">

              <Upload size={28} />

            </div>

            <strong>
              Choose a meal photo
            </strong>

            <span>
              JPG, JPEG, PNG or other supported
              image formats
            </span>

          </button>

        ) : (

          <div className="meal-image-preview">

            <img
              src={previewUrl}
              alt="Selected meal"
            />

            <button
              type="button"
              className="remove-meal-image"
              onClick={removeImage}
              disabled={analyzing}
              aria-label="Remove selected meal image"
            >

              <X size={18} />

            </button>

          </div>

        )}


        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          hidden
        />


        {/* ==================================================
            OPTIONAL MEAL DETAILS
        ================================================== */}

        <div
          style={{
            marginTop: "24px",
            padding: "18px",
            borderRadius: "14px",
            border:
              "1px solid rgba(148, 163, 184, 0.25)",
            background:
              "rgba(248, 250, 249, 0.75)",
          }}
        >

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "7px",
            }}
          >

            <MessageSquareText
              size={19}
            />

            <label
              htmlFor="meal-comment"
              style={{
                fontWeight: 700,
              }}
            >

              Additional details{" "}

              <span
                style={{
                  fontWeight: 400,
                  opacity: 0.65,
                }}
              >
                (optional)
              </span>

            </label>

          </div>


          <p
            style={{
              marginTop: 0,
              marginBottom: "12px",
              fontSize: "14px",
              lineHeight: 1.5,
              opacity: 0.72,
            }}
          >

            Add hidden ingredients, cooking
            details, quantities, or meal context
            that may not be visible in the photo.

          </p>


          <textarea
            id="meal-comment"
            value={comment}
            onChange={(event) =>
              setComment(
                event.target.value
              )
            }
            disabled={analyzing}
            maxLength={1000}
            rows={4}
            placeholder={
              "Example: This curry contains coconut, cashews and 2 tsp oil. Or: I'm at a buffet and this is an extra meal outside my plan."
            }
            style={{
              width: "100%",
              boxSizing: "border-box",
              resize: "vertical",
              minHeight: "105px",
              padding: "13px 14px",
              borderRadius: "12px",
              border:
                "1px solid rgba(148, 163, 184, 0.35)",
              background: "#ffffff",
              font: "inherit",
              lineHeight: 1.5,
              outline: "none",
            }}
          />


          <div
            style={{
              display: "flex",
              justifyContent:
                "space-between",
              alignItems: "center",
              gap: "12px",
              marginTop: "7px",
              fontSize: "12px",
              opacity: 0.65,
            }}
          >

            <span>
              MealMind will use these details
              together with the photo.
            </span>

            <span>
              {comment.length} / 1000
            </span>

          </div>

        </div>


        {/* ==================================================
            ACTIONS
        ================================================== */}

        <div className="meal-analysis-actions">

          {selectedImage && (

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={analyzing}
            >

              <ImagePlus size={17} />

              Change Photo

            </button>

          )}


          <button
            type="button"
            className="primary-button"
            onClick={analyzeMeal}
            disabled={
              !selectedImage ||
              analyzing
            }
          >

            <Sparkles size={18} />

            {analyzing
              ? "Analyzing Your Meal..."
              : "Analyze Meal"}

          </button>

        </div>


        {/* ==================================================
            LOADING
        ================================================== */}

        {analyzing && (

          <div className="analysis-progress">

            <div className="loading-spinner">
            </div>

            <div>

              <strong>
                MealMind is analyzing your meal
              </strong>

              <span>
                Identifying foods, estimating
                portions and preparing
                personalized feedback.
              </span>

            </div>

          </div>

        )}

      </section>


      {/* ======================================================
          ANALYSIS RESULT
      ====================================================== */}

      {result && (
  <MealAnalysisResult
    result={result}
    onSave={saveMeal}
    savingMeal={savingMeal}
    mealSaved={mealSaved}
    saveMessage={saveMessage}
  />
)}

    </div>
  );
}


// ============================================================
// ANALYSIS RESULT
// ============================================================

function MealAnalysisResult({
  result,
  onSave,
  savingMeal,
  mealSaved,
  saveMessage,
}) {

  const mealTotal =
    result?.meal_total || {};

  const foods =
    Array.isArray(
      result?.foods
    )
      ? result.foods
      : [];

  const feedback =
    result?.personalized_feedback ||
    {};

  const restOfDayAdvice =
    result?.rest_of_day_advice;


  return (

    <div className="meal-analysis-result">


      {/* ====================================================
          NUTRITION SUMMARY
      ==================================================== */}

      <section className="plan-section-heading">

        <div>

          <p className="eyebrow">
            MEAL SUMMARY
          </p>

          <h2>
            Estimated Nutrition
          </h2>

        </div>


        {result.processing_time_seconds && (

          <span className="processing-time">

            Analyzed in{" "}

            {
              result.processing_time_seconds
            }s

          </span>

        )}

      </section>


      <section className="nutrition-target-grid">

        <NutritionCard
          icon={
            <Flame size={20} />
          }
          label="Calories"
          value={
            mealTotal.calories
          }
          unit="kcal"
        />

        <NutritionCard
          icon={
            <Dumbbell size={20} />
          }
          label="Protein"
          value={
            mealTotal.protein_g
          }
          unit="g"
        />

        <NutritionCard
          icon={
            <Wheat size={20} />
          }
          label="Carbohydrates"
          value={
            mealTotal.carbohydrates_g
          }
          unit="g"
        />

        <NutritionCard
          icon={
            <Droplets size={20} />
          }
          label="Fat"
          value={
            mealTotal.fat_g
          }
          unit="g"
        />

        <NutritionCard
          icon={
            <Leaf size={20} />
          }
          label="Fiber"
          value={
            mealTotal.fiber_g
          }
          unit="g"
        />

      </section>


      {/* ====================================================
          DETECTED FOODS
      ==================================================== */}

      <section className="detected-foods-section">

        <div className="plan-section-heading">

          <div>

            <p className="eyebrow">
              DETECTED FOODS
            </p>

            <h2>
              What's on Your Plate
            </h2>

          </div>

        </div>


        <div className="detected-food-grid">

          {foods.map(
            (
              food,
              index
            ) => (

              <article
                className="detected-food-card"
                key={
                  `${food.food_name}-${index}`
                }
              >

                <div className="detected-food-header">

                  <div className="food-number">
                    {index + 1}
                  </div>

                  <div>

                    <h3>
                      {
                        food.food_name
                      }
                    </h3>

                    <span>
                      {
                        food.approximate_portion ||
                        "Portion estimated"
                      }
                    </span>

                  </div>

                </div>


                <div className="food-details">

                  <FoodDetail
                    label="Plate"
                    value={
                      food.approximate_percentage_of_visible_meal !==
                      undefined
                        ? `${food.approximate_percentage_of_visible_meal}%`
                        : "--"
                    }
                  />

                  <FoodDetail
                    label="Calories"
                    value={
                      food.calories !==
                      undefined
                        ? `${food.calories} kcal`
                        : "--"
                    }
                  />

                  <FoodDetail
                    label="Protein"
                    value={
                      food.protein_g !==
                      undefined
                        ? `${food.protein_g} g`
                        : "--"
                    }
                  />

                  <FoodDetail
                    label="Carbs"
                    value={
                      food.carbohydrates_g !==
                      undefined
                        ? `${food.carbohydrates_g} g`
                        : "--"
                    }
                  />

                  <FoodDetail
                    label="Fat"
                    value={
                      food.fat_g !==
                      undefined
                        ? `${food.fat_g} g`
                        : "--"
                    }
                  />

                  <FoodDetail
                    label="Fiber"
                    value={
                      food.fiber_g !==
                      undefined
                        ? `${food.fiber_g} g`
                        : "--"
                    }
                  />

                </div>

              </article>

            )
          )}

        </div>

      </section>


      {/* ====================================================
          PERSONALIZED FEEDBACK
      ==================================================== */}

      <section className="feedback-section">

        <div className="plan-section-heading">

          <div>

            <p className="eyebrow">
              PERSONALIZED FEEDBACK
            </p>

            <h2>
              MealMind's Guidance
            </h2>

          </div>

        </div>


        <div className="feedback-grid">

          <FeedbackCard
            icon={
              <Sparkles size={19} />
            }
            title="Meal Overview"
            content={
              getFeedbackValue(
                feedback,
                [
                  "meal_overview",
                  "overview",
                ]
              )
            }
          />


          <FeedbackCard
            icon={
              <CheckCircle2
                size={19}
              />
            }
            title="What's Good"
            content={
              getFeedbackValue(
                feedback,
                [
                  "whats_good",
                  "what_is_good",
                  "good",
                ]
              )
            }
          />


          <FeedbackCard
            icon={
              <AlertCircle
                size={19}
              />
            }
            title="What to Consider"
            content={
              getFeedbackValue(
                feedback,
                [
                  "what_to_consider",
                  "considerations",
                ]
              )
            }
          />


          <FeedbackCard
            icon={
              <Lightbulb
                size={19}
              />
            }
            title="Suggestion"
            content={
              getFeedbackValue(
                feedback,
                [
                  "suggestion",
                  "suggestions",
                ]
              )
            }
          />


          <FeedbackCard
            icon={
              <Apple size={19} />
            }
            title="Healthy Add-on"
            content={
              getFeedbackValue(
                feedback,
                [
                  "healthy_add_on",
                  "healthy_addon",
                ]
              )
            }
          />


          <FeedbackCard
            icon={
              <Target size={19} />
            }
            title="Overall"
            content={
              getFeedbackValue(
                feedback,
                [
                  "overall",
                  "overall_feedback",
                ]
              )
            }
          />

        </div>

      </section>


      {/* ====================================================
          REST OF TODAY — ADAPTIVE GUIDANCE
      ==================================================== */}

      {restOfDayAdvice && (

        <section
          style={{
            marginTop: "24px",
            padding: "22px",
            borderRadius: "16px",
            border:
              "1px solid rgba(34, 197, 94, 0.22)",
            background:
              "rgba(240, 253, 244, 0.92)",
          }}
        >

          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "13px",
            }}
          >

            <div
              style={{
                width: "42px",
                height: "42px",
                minWidth: "42px",
                borderRadius: "12px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background:
                  "rgba(34, 197, 94, 0.12)",
                color: "#15803d",
              }}
            >

              <Clock3 size={21} />

            </div>


            <div>

              <p
                className="eyebrow"
                style={{
                  marginTop: 0,
                  marginBottom: "4px",
                }}
              >
                ADAPTIVE GUIDANCE
              </p>

              <h3
                style={{
                  margin:
                    "0 0 7px 0",
                  fontSize: "18px",
                  color: "#166534",
                }}
              >
                Rest of Today
              </h3>

              <p
                style={{
                  margin: 0,
                  fontSize: "14px",
                  lineHeight: 1.7,
                  color: "#334155",
                }}
              >
                {restOfDayAdvice}
              </p>

              <span
                style={{
                  display: "block",
                  marginTop: "9px",
                  fontSize: "12px",
                  color: "#64748b",
                }}
              >
                Based on today's analyzed meals
                and your daily nutrition plan.
              </span>

            </div>

          </div>

        </section>

      )}

      {/* ====================================================
          SAVE MEAL
      ==================================================== */}

      <section
        style={{
          marginTop: "28px",
          padding: "22px",
          borderRadius: "16px",
          border:
            "1px solid rgba(34, 197, 94, 0.22)",
          background:
            "rgba(240, 253, 244, 0.72)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "20px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <h3
              style={{
                margin: "0 0 5px 0",
                color: "#166534",
              }}
            >
              Did you have this meal?
            </h3>

            <p
              style={{
                margin: 0,
                color: "#64748b",
                fontSize: "14px",
              }}
            >
              Save it only if you actually consumed
              this meal. Otherwise, this analysis
              remains a temporary preview.
            </p>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={onSave}
            disabled={
              savingMeal ||
              mealSaved
            }
          >
            <CheckCircle2 size={18} />

            {savingMeal
              ? "Saving..."
              : mealSaved
                ? "Meal Saved"
                : "Save Meal"}
          </button>
        </div>

        {saveMessage && (
          <div
            style={{
              marginTop: "14px",
              color: "#15803d",
              fontSize: "14px",
              fontWeight: 600,
            }}
          >
            ✓ {saveMessage}
          </div>
        )}
      </section>

    </div>
  );
}


// ============================================================
// NUTRITION CARD
// ============================================================

function NutritionCard({
  icon,
  label,
  value,
  unit,
}) {

  return (

    <div className="nutrition-target-card">

      <div className="nutrition-target-icon">
        {icon}
      </div>

      <span>
        {label}
      </span>

      <strong>

        {value ?? "--"}

        {
          value !== undefined &&
          value !== null && (

            <small>
              {" "}
              {unit}
            </small>

          )
        }

      </strong>

    </div>
  );
}


// ============================================================
// FOOD DETAIL
// ============================================================

function FoodDetail({
  label,
  value,
}) {

  return (

    <div className="food-detail">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


// ============================================================
// FEEDBACK CARD
// ============================================================

function FeedbackCard({
  icon,
  title,
  content,
}) {

  if (!content) {
    return null;
  }

  return (

    <article className="feedback-card">

      <div className="feedback-card-icon">
        {icon}
      </div>

      <div>

        <h3>
          {title}
        </h3>

        {Array.isArray(content) ? (

          <ul>

            {content.map(
              (
                item,
                index
              ) => (

                <li key={index}>
                  {String(item)}
                </li>

              )
            )}

          </ul>

        ) : (

          <p>
            {String(content)}
          </p>

        )}

      </div>

    </article>
  );
}


// ============================================================
// GET FEEDBACK VALUE
// ============================================================

function getFeedbackValue(
  feedback,
  possibleKeys
) {

  for (
    const key of possibleKeys
  ) {

    if (
      feedback[key] !==
        undefined &&
      feedback[key] !==
        null
    ) {

      return feedback[key];

    }
  }

  return null;
}


export default MealAnalysis;