import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";

import {
  Target,
  Utensils,
  Activity,
  Flame,
  Dumbbell,
  Wheat,
  Droplets,
  Leaf,
  Sparkles,
  RefreshCw,
  HeartPulse,
  CalendarDays,
} from "lucide-react";

import api, {
  generateWeeklyDietPlan,
  getWeeklyDietPlan,
} from "../services/api";

import WeeklyPlan from "../components/WeeklyPlan";
import DietCalendar from "../components/DietCalendar";


function DietPlan() {
  const { user: authUser } = useAuth();

  const USER_ID = authUser?.id;

  const [profile, setProfile] = useState(null);

  const [dietPlan, setDietPlan] = useState(null);

  const [weeklyPlan, setWeeklyPlan] = useState(null);

  const [foodAllergies, setFoodAllergies] =
    useState("");

  const [foodsToAvoid, setFoodsToAvoid] =
    useState("");

  const [mealsPerDay, setMealsPerDay] =
    useState(4);

  const [loading, setLoading] =
    useState(true);

  const [generating, setGenerating] =
    useState(false);

  const [error, setError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");


  // ============================================================
  // LOAD PAGE
  // ============================================================

  useEffect(() => {
    if (!USER_ID) {
      return;
    }

    loadPage();
  }, [USER_ID]);


  async function loadPage() {
    try {
      setLoading(true);
      setError("");

      // --------------------------------------------------------
      // LOAD HEALTH PROFILE
      // --------------------------------------------------------

      const profileResponse =
        await api.get(
          `/users/${USER_ID}/profile`
        );

      setProfile(
        profileResponse.data
      );


      // --------------------------------------------------------
      // LOAD CURRENT WEEKLY PLAN
      // --------------------------------------------------------

      try {
        const weeklyResponse =
          await getWeeklyDietPlan(
            USER_ID
          );

        setDietPlan(
          weeklyResponse
        );

        setWeeklyPlan(
          weeklyResponse.weekly_plan ||
            null
        );

        setFoodAllergies(
          (
            weeklyResponse.food_allergies ||
            []
          ).join(", ")
        );

        setFoodsToAvoid(
          (
            weeklyResponse.foods_to_avoid ||
            []
          ).join(", ")
        );

        setMealsPerDay(
          weeklyResponse.meals_per_day ||
            4
        );
      } catch (planError) {
        if (
          planError.response?.status ===
          404
        ) {
          setDietPlan(null);
          setWeeklyPlan(null);
        } else {
          throw planError;
        }
      }
    } catch (err) {
      console.error(
        "Diet plan page error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not load your profile."
      );
    } finally {
      setLoading(false);
    }
  }


  // ============================================================
  // CONVERT COMMA-SEPARATED INPUT INTO ARRAY
  // ============================================================

  function convertToList(value) {
    return value
      .split(",")
      .map((item) =>
        item.trim()
      )
      .filter(Boolean);
  }


  // ============================================================
  // GENERATE 7-DAY DIET PLAN
  // ============================================================

  async function generatePlan() {
    const isRegenerating =
      Boolean(weeklyPlan);

    try {
      setGenerating(true);
      setError("");
      setSuccessMessage("");

      const payload = {
        food_allergies:
          convertToList(
            foodAllergies
          ),

        foods_to_avoid:
          convertToList(
            foodsToAvoid
          ),

        meals_per_day:
          Number(mealsPerDay),
      };


      const response =
        await generateWeeklyDietPlan(
          USER_ID,
          payload
        );


      setDietPlan(
        response
      );

      setWeeklyPlan(
        response.weekly_plan ||
          null
      );


      setSuccessMessage(
        isRegenerating
          ? "Your 7-day diet plan has been regenerated successfully."
          : "Your personalized 7-day diet plan has been created successfully."
      );
    } catch (err) {
      console.error(
        "Weekly diet plan generation error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not generate your weekly diet plan."
      );
    } finally {
      setGenerating(false);
    }
  }


  // ============================================================
  // LOADING SCREEN
  // ============================================================

  if (loading) {
    return (
      <div className="page-state">

        <div className="loading-spinner">
        </div>

        <h2>
          Loading your diet plan
        </h2>

        <p>
          Getting your MealMind nutrition
          information.
        </p>

      </div>
    );
  }


  // ============================================================
  // PROFILE INFORMATION
  // ============================================================

  const health =
    profile?.health_profile;

  const user =
    profile?.user;


  const isFemale =
    String(
      user?.gender || ""
    )
      .toLowerCase()
      .trim() === "female";


  const womenHealthCondition =
    health?.women_health_condition ||
    dietPlan?.women_health_condition ||
    "none";


  const showWomenHealth =
    isFemale &&
    womenHealthCondition !== "none";


  // ============================================================
  // NUTRITION TARGETS
  // ============================================================

  const targets =
    dietPlan?.nutrition_targets ||
    {};


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="diet-plan-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <section className="diet-plan-header">

        <div>

          <p className="eyebrow">
            PERSONALIZED NUTRITION
          </p>

          <h1>
            My Diet Plan
          </h1>

          <p>
            Create a personalized 7-day meal
            plan based on your health profile,
            lifestyle and nutrition goal.
          </p>

        </div>


        <div className="diet-plan-status">

          {weeklyPlan ? (
            <CalendarDays size={18} />
          ) : (
            <Sparkles size={18} />
          )}

          {weeklyPlan
            ? "Weekly Plan Generated"
            : "Ready to Generate"}

        </div>

      </section>


      {/* ======================================================
          ERROR MESSAGE
      ====================================================== */}

      {error && (
        <div className="message-box error-message">
          {error}
        </div>
      )}


      {/* ======================================================
          SUCCESS MESSAGE
      ====================================================== */}

      {successMessage && (
        <div className="message-box success-message">

          <Sparkles size={17} />

          {successMessage}

        </div>
      )}


      {/* ======================================================
          PROFILE SUMMARY
      ====================================================== */}

      <section className="diet-profile-summary">

        <ProfileCard
          icon={
            <Target size={19} />
          }
          label="Goal"
          value={
            formatGoal(
              health?.goal
            )
          }
        />


        <ProfileCard
          icon={
            <Utensils size={19} />
          }
          label="Diet"
          value={
            formatDiet(
              health?.diet_preference
            )
          }
        />


        <ProfileCard
          icon={
            <Activity size={19} />
          }
          label="Activity"
          value={
            formatActivity(
              health?.activity_level
            )
          }
        />


        {showWomenHealth && (
          <ProfileCard
            icon={
              <HeartPulse
                size={19}
              />
            }
            label="Women's Health"
            value={
              formatWomenHealth(
                womenHealthCondition
              )
            }
          />
        )}

      </section>


      {/* ======================================================
          WEEKLY PLAN GENERATOR
      ====================================================== */}

      <section className="form-card">

        <div className="form-section-header">

          <div className="form-section-icon">

            {weeklyPlan ? (
              <RefreshCw size={21} />
            ) : (
              <Sparkles size={21} />
            )}

          </div>


          <div>

            <h2>
              {weeklyPlan
                ? "Regenerate Your Weekly Plan"
                : "Create Your Weekly Diet Plan"}
            </h2>

            <p>
              {weeklyPlan
                ? "Your current 7-day plan is shown below. Change your food restrictions or meals per day if needed, then regenerate the week."
                : "Add your food restrictions and MealMind will create a personalized 7-day nutrition plan."}
            </p>

          </div>

        </div>


        <div className="form-grid">

          {/* FOOD ALLERGIES */}

          <label className="form-field">

            <span>
              Food Allergies
            </span>

            <input
              type="text"
              value={
                foodAllergies
              }
              onChange={(
                event
              ) => {
                setFoodAllergies(
                  event.target.value
                );

                setSuccessMessage(
                  ""
                );
              }}
              placeholder="Example: peanut, lactose"
            />

            <small>
              Separate multiple allergies
              with commas.
            </small>

          </label>


          {/* FOODS TO AVOID */}

          <label className="form-field">

            <span>
              Foods You Want to Avoid
            </span>

            <input
              type="text"
              value={
                foodsToAvoid
              }
              onChange={(
                event
              ) => {
                setFoodsToAvoid(
                  event.target.value
                );

                setSuccessMessage(
                  ""
                );
              }}
              placeholder="Example: mushroom, brinjal"
            />

            <small>
              MealMind will avoid these
              foods.
            </small>

          </label>


          {/* MEALS PER DAY */}

          <label className="form-field">

            <span>
              Meals Per Day
            </span>

            <select
              value={
                mealsPerDay
              }
              onChange={(
                event
              ) => {
                setMealsPerDay(
                  Number(
                    event.target.value
                  )
                );

                setSuccessMessage(
                  ""
                );
              }}
            >

              <option value={3}>
                3 Meals
              </option>

              <option value={4}>
                4 Meals
              </option>

              <option value={5}>
                5 Meals
              </option>

              <option value={6}>
                6 Meals
              </option>

            </select>

          </label>

        </div>


        {/* GENERATE BUTTON */}

        <div className="diet-generator-action">

          <button
            type="button"
            className="primary-button"
            onClick={
              generatePlan
            }
            disabled={
              generating
            }
          >

            <RefreshCw
              size={18}
              className={
                generating
                  ? "spin-icon"
                  : ""
              }
            />


            {generating
              ? weeklyPlan
                ? "Regenerating Your Week..."
                : "Creating Your 7-Day Plan..."
              : weeklyPlan
                ? "Regenerate Weekly Plan"
                : "Generate 7-Day Diet Plan"}

          </button>

        </div>

      </section>


      {/* ======================================================
          DAILY NUTRITION TARGETS
      ====================================================== */}

      {weeklyPlan && (

        <div className="diet-plan-result">

          <section className="plan-section-heading">

            <div>

              <p className="eyebrow">
                YOUR DAILY TARGET
              </p>

              <h2>
                Daily Nutrition Goals
              </h2>

            </div>

          </section>


          <section className="nutrition-target-grid">

            <NutritionCard
              icon={
                <Flame size={20} />
              }
              label="Calories"
              value={
                targets.target_calories
              }
              unit="kcal"
            />


            <NutritionCard
              icon={
                <Dumbbell size={20} />
              }
              label="Protein"
              value={
                targets.protein_g
              }
              unit="g"
            />


            <NutritionCard
              icon={
                <Wheat size={20} />
              }
              label="Carbohydrates"
              value={
                targets.carbohydrates_g
              }
              unit="g"
            />


            <NutritionCard
              icon={
                <Droplets size={20} />
              }
              label="Fat"
              value={
                targets.fat_g
              }
              unit="g"
            />


            <NutritionCard
              icon={
                <Leaf size={20} />
              }
              label="Fiber"
              value={
                targets.fiber_g
              }
              unit="g"
            />

          </section>

        </div>

      )}


      {/* ======================================================
          7-DAY WEEKLY PLAN
      ====================================================== */}

      {weeklyPlan && (
        <WeeklyPlan
          weeklyPlan={
            weeklyPlan
          }
        />
      )}


      {/* ======================================================
          NUTRITION CALENDAR
      ====================================================== */}

      {weeklyPlan && (
        <DietCalendar
          userId={
            USER_ID
          }
        />
      )}

    </div>
  );
}


// ============================================================
// NUTRITION TARGET CARD
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

        {value !== undefined &&
          value !== null && (
            <small>
              {" "}
              {unit}
            </small>
          )}

      </strong>

    </div>
  );
}


// ============================================================
// PROFILE CARD
// ============================================================

function ProfileCard({
  icon,
  label,
  value,
}) {
  return (
    <div className="diet-profile-card">

      <div className="diet-profile-icon">
        {icon}
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

      </div>

    </div>
  );
}


// ============================================================
// FORMAT GOAL
// ============================================================

function formatGoal(value) {
  const values = {
    weight_loss:
      "Weight Loss",

    maintenance:
      "Maintain Weight",

    weight_gain:
      "Weight Gain",

    muscle_gain:
      "Muscle Gain",

    strength_gain:
      "Strength Gain",
  };

  return (
    values[value] ||
    "Not Set"
  );
}


// ============================================================
// FORMAT DIET
// ============================================================

function formatDiet(value) {
  const values = {
    vegetarian:
      "Vegetarian",

    "non-vegetarian":
      "Non-Vegetarian",

    vegan:
      "Vegan",

    eggetarian:
      "Eggetarian",
  };

  return (
    values[value] ||
    "Not Set"
  );
}


// ============================================================
// FORMAT ACTIVITY
// ============================================================

function formatActivity(value) {
  const values = {
    sedentary:
      "Sedentary",

    light:
      "Lightly Active",

    moderate:
      "Moderately Active",

    active:
      "Active",

    very_active:
      "Very Active",
  };

  return (
    values[value] ||
    "Not Set"
  );
}


// ============================================================
// FORMAT WOMEN'S HEALTH
// ============================================================

function formatWomenHealth(value) {
  const values = {
    pcos:
      "PCOS",

    menstrual_wellness:
      "Menstrual Wellness",

    pregnancy:
      "Pregnancy",

    breastfeeding:
      "Breastfeeding",
  };

  return (
    values[value] ||
    "Not Set"
  );
}


export default DietPlan;