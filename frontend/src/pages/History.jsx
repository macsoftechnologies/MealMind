import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  History as HistoryIcon,
  CalendarDays,
  Flame,
  Dumbbell,
  Wheat,
  Droplets,
  Leaf,
  Utensils,
  ChevronDown,
  ChevronUp,
  Sparkles,
  AlertCircle,
  RefreshCw,
  Trash2,
} from "lucide-react";


import api, {
  getDietPlanByDate,
  getCalendarEvents,
  createCalendarEvent,
} from "../services/api";

import MealCalendar from "../components/MealCalendar";



function History() {
  const { user: authUser } = useAuth();
  const USER_ID = authUser.id;

  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [expandedMealId, setExpandedMealId] =
    useState(null);

  const [deletingMealId, setDeletingMealId] =
    useState(null);

  const [selectedDate, setSelectedDate] =
    useState(getLocalDateString());

  const [visibleMonth, setVisibleMonth] =
    useState(() => new Date());

  const [selectedDayPlan, setSelectedDayPlan] =
    useState(null);

  const [dayPlanLoading, setDayPlanLoading] =
    useState(false);

  const [
  calendarEvents,
  setCalendarEvents,
  ] = useState([]);


  useEffect(() => {
    loadMealHistory();
  }, []);

  useEffect(() => {
  if (!USER_ID || !selectedDate) {
    return;
  }

      loadSelectedDayPlan();
    }, [USER_ID, selectedDate]);

    useEffect(() => {
  if (
    !USER_ID ||
    !selectedDate
  ) {
    return;
  }

  loadCalendarEvents();
    }, [
    USER_ID,
    selectedDate,
  ]);

  async function loadCalendarEvents() {
  try {
    const data =
      await getCalendarEvents(
        USER_ID,
        selectedDate
      );

    setCalendarEvents(
      Array.isArray(data)
        ? data
        : []
    );
  } catch (err) {
    console.error(
      "Calendar events error:",
      err
    );

    setCalendarEvents([]);
  }
}


  async function loadMealHistory() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/users/${USER_ID}/meals`
      );

      const data = response.data;

      const mealList = Array.isArray(data)
        ? data
        : Array.isArray(data?.meals)
          ? data.meals
          : [];

      setMeals(mealList);

    } catch (err) {
      console.error(
        "Meal history error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not load your meal history."
      );

    } finally {
      setLoading(false);
    }
  }

  async function loadSelectedDayPlan() {
  try {
    setDayPlanLoading(true);

    const data =
      await getDietPlanByDate(
        USER_ID,
        selectedDate
      );

    setSelectedDayPlan(data);
  } catch (err) {
    /*
     * 404 simply means there is no generated
     * diet plan covering this date.
     */
    if (err.response?.status === 404) {
      setSelectedDayPlan(null);
      return;
    }

    console.error(
      "Selected day diet plan error:",
      err
    );

    setSelectedDayPlan(null);
  } finally {
    setDayPlanLoading(false);
  }
}


  function toggleMeal(mealId) {
    setExpandedMealId((currentId) =>
      currentId === mealId
        ? null
        : mealId
    );
  }


  async function deleteMeal(meal) {
    const mealId =
      meal.id ??
      meal.meal_id;

    if (!mealId) {
      setError(
        "Could not identify this meal."
      );
      return;
    }


    const confirmed = window.confirm(
      "Delete this meal permanently?\n\n" +
      "This will remove the meal and its nutrition data " +
      "from your history and PostgreSQL database."
    );


    if (!confirmed) {
      return;
    }


    try {
      setDeletingMealId(mealId);
      setError("");


      await api.delete(
        `/users/${USER_ID}/meals/${mealId}`
      );


      /*
       * Remove the deleted meal from the page
       * immediately without needing another GET request.
       */
      setMeals((currentMeals) =>
        currentMeals.filter((item) => {
          const currentMealId =
            item.id ??
            item.meal_id;

          return currentMealId !== mealId;
        })
      );


      if (expandedMealId === mealId) {
        setExpandedMealId(null);
      }

    } catch (err) {
      console.error(
        "Delete meal error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not delete this meal."
      );

    } finally {
      setDeletingMealId(null);
    }
  }


  if (loading) {
    return (
      <div className="page-state">

        <div className="loading-spinner"></div>

        <h2>
          Loading meal history
        </h2>

        <p>
          Getting your previous MealMind analyses.
        </p>

      </div>
    );
  }


  return (
    <div className="history-page">

      {/* Header */}

      <section className="history-header">

        <div>

          <p className="eyebrow">
            YOUR NUTRITION JOURNEY
          </p>

          <h1>
            Meal History
          </h1>

          <p>
            Review your previously analyzed meals,
            nutrition estimates and personalized feedback.
          </p>

        </div>


        <button
          type="button"
          className="history-refresh-button"
          onClick={loadMealHistory}
        >
          <RefreshCw size={16} />
          Refresh
        </button>

      </section>

      {/* Meal Calendar */}

      <MealCalendar
  meals={meals}
  selectedDate={selectedDate}
  onDateSelect={setSelectedDate}
  visibleMonth={visibleMonth}
  onMonthChange={setVisibleMonth}
  dayPlan={selectedDayPlan}
  planLoading={dayPlanLoading}
  customEvents={calendarEvents}
  userId={USER_ID}
  onEventCreated={
    loadCalendarEvents
  }
  />


      {/* Error */}

      {error && (
        <div className="message-box error-message">
          <AlertCircle size={17} />
          {error}
        </div>
      )}


      {/* Empty History */}

      {!error && meals.length === 0 && (

        <section className="history-empty-state">

          <div className="history-empty-icon">
            <HistoryIcon size={30} />
          </div>

          <h2>
            No meals analyzed yet
          </h2>

          <p>
            Analyze your first meal and it will
            automatically appear here.
          </p>

        </section>

      )}


      {/* History List */}

      {meals.length > 0 && (

        <section className="history-list">

          <div className="history-summary">

            <div>

              <HistoryIcon size={18} />

              <span>
                {meals.length}{" "}
                {meals.length === 1
                  ? "meal"
                  : "meals"}{" "}
                analyzed
              </span>

            </div>

          </div>


          {meals.map((meal, index) => {

            const mealId =
              meal.id ??
              meal.meal_id ??
              index;

            const isExpanded =
              expandedMealId === mealId;

            return (

              <MealHistoryCard
                key={mealId}
                meal={meal}
                number={index + 1}
                isExpanded={isExpanded}
                deleting={
                  deletingMealId === mealId
                }
                onToggle={() =>
                  toggleMeal(mealId)
                }
                onDelete={() =>
                  deleteMeal(meal)
                }
              />

            );
          })}

        </section>

      )}

    </div>
  );
}



function MealHistoryCard({
  meal,
  number,
  isExpanded,
  deleting,
  onToggle,
  onDelete,
}) {
  const foods =
    getFoods(meal);

  const nutrition =
    getNutrition(meal);


  const feedback =
    meal.personalized_feedback ||
    meal.feedback ||
    {};


  const date =
    meal.created_at ||
    meal.analyzed_at ||
    meal.date;


  return (
    <article className="history-meal-card">

      {/* Main row */}

      <div className="history-meal-row">

        <button
          type="button"
          className="history-meal-summary"
          onClick={onToggle}
        >

          <div className="history-meal-main">

            <div className="history-meal-number">
              <Utensils size={18} />
            </div>


            <div>

              <span className="history-meal-label">
                Meal Analysis {number}
              </span>


              <h3>
                {getMealTitle(foods)}
              </h3>


              <div className="history-meal-date">

                <CalendarDays size={13} />

                <span>
                  {formatDate(date)}
                </span>

              </div>

            </div>

          </div>


          <div className="history-meal-right">

            <div className="history-calories">

              <Flame size={16} />

              <strong>
                {nutrition.calories ?? "--"}
              </strong>

              <span>
                kcal
              </span>

            </div>


            <div className="history-expand-icon">

              {isExpanded ? (
                <ChevronUp size={19} />
              ) : (
                <ChevronDown size={19} />
              )}

            </div>

          </div>

        </button>


        <button
          type="button"
          className="history-delete-button"
          onClick={onDelete}
          disabled={deleting}
          title="Delete meal permanently"
        >

          <Trash2 size={17} />

          <span>
            {deleting
              ? "Deleting..."
              : "Delete"}
          </span>

        </button>

      </div>


      {/* Expanded details */}

      {isExpanded && (

        <div className="history-meal-details">

          {/* Nutrition */}

          <div className="history-detail-section">

            <h4>
              Estimated Nutrition
            </h4>


            <div className="history-nutrition-grid">

              <HistoryNutritionItem
                icon={<Flame size={17} />}
                label="Calories"
                value={nutrition.calories}
                unit="kcal"
              />


              <HistoryNutritionItem
                icon={<Dumbbell size={17} />}
                label="Protein"
                value={nutrition.protein_g}
                unit="g"
              />


              <HistoryNutritionItem
                icon={<Wheat size={17} />}
                label="Carbs"
                value={
                  nutrition.carbohydrates_g
                }
                unit="g"
              />


              <HistoryNutritionItem
                icon={<Droplets size={17} />}
                label="Fat"
                value={nutrition.fat_g}
                unit="g"
              />


              <HistoryNutritionItem
                icon={<Leaf size={17} />}
                label="Fiber"
                value={nutrition.fiber_g}
                unit="g"
              />

            </div>

          </div>


          {/* Foods */}

          {foods.length > 0 && (

            <div className="history-detail-section">

              <h4>
                Detected Foods
              </h4>


              <div className="history-food-list">

                {foods.map(
                  (food, index) => (

                    <div
                      className="history-food-item"
                      key={
                        food.id ??
                        `${food.food_name}-${index}`
                      }
                    >

                      <div>

                        <strong>
                          {food.food_name ||
                            food.name ||
                            `Food ${index + 1}`}
                        </strong>


                        {(food.approximate_portion ||
                          food.portion) && (

                          <span>
                            {food.approximate_portion ||
                              food.portion}
                          </span>

                        )}

                      </div>


                      {food.calories !== undefined &&
                        food.calories !== null && (

                          <span className="history-food-calories">
                            {food.calories} kcal
                          </span>

                        )}

                    </div>

                  )
                )}

              </div>

            </div>

          )}


          {/* Feedback */}

          {hasFeedback(feedback) && (

            <div className="history-detail-section">

              <h4>
                <Sparkles size={16} />
                Personalized Feedback
              </h4>


              <div className="history-feedback-grid">

                <FeedbackItem
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


                <FeedbackItem
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


                <FeedbackItem
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


                <FeedbackItem
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


                <FeedbackItem
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


                <FeedbackItem
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

            </div>

          )}

        </div>

      )}

    </article>
  );
}



function HistoryNutritionItem({
  icon,
  label,
  value,
  unit,
}) {
  return (
    <div className="history-nutrition-item">

      <div className="history-nutrition-icon">
        {icon}
      </div>


      <div>

        <span>
          {label}
        </span>

        <strong>
          {value ?? "--"}

          {value !== undefined &&
            value !== null && (
              <small> {unit}</small>
            )}
        </strong>

      </div>

    </div>
  );
}



function FeedbackItem({
  title,
  content,
}) {
  if (
    content === undefined ||
    content === null ||
    content === ""
  ) {
    return null;
  }


  return (
    <div className="history-feedback-item">

      <strong>
        {title}
      </strong>


      {Array.isArray(content) ? (

        <ul>

          {content.map(
            (item, index) => (

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
  );
}



function getFoods(meal) {
  if (
    Array.isArray(meal.foods)
  ) {
    return meal.foods;
  }


  if (
    Array.isArray(
      meal.meal_foods
    )
  ) {
    return meal.meal_foods;
  }


  if (
    Array.isArray(
      meal.detected_foods
    )
  ) {
    return meal.detected_foods;
  }


  return [];
}



function getNutrition(meal) {
  const nested =
    meal.meal_total ||
    meal.nutrition ||
    meal.total_nutrition ||
    {};


  return {
    calories:
      meal.total_calories ??
      nested.calories ??
      nested.total_calories,

    protein_g:
      meal.total_protein_g ??
      nested.protein_g ??
      nested.total_protein_g,

    carbohydrates_g:
      meal.total_carbohydrates_g ??
      nested.carbohydrates_g ??
      nested.total_carbohydrates_g,

    fat_g:
      meal.total_fat_g ??
      nested.fat_g ??
      nested.total_fat_g,

    fiber_g:
      meal.total_fiber_g ??
      nested.fiber_g ??
      nested.total_fiber_g,
  };
}



function getMealTitle(foods) {
  if (!foods.length) {
    return "Analyzed Meal";
  }


  const names = foods
    .slice(0, 3)
    .map(
      (food) =>
        food.food_name ||
        food.name
    )
    .filter(Boolean);


  if (!names.length) {
    return "Analyzed Meal";
  }


  const title =
    names.join(", ");


  return foods.length > 3
    ? `${title} +${foods.length - 3} more`
    : title;
}



function getFeedbackValue(
  feedback,
  possibleKeys
) {
  for (
    const key of possibleKeys
  ) {
    if (
      feedback[key] !== undefined &&
      feedback[key] !== null
    ) {
      return feedback[key];
    }
  }


  return null;
}



function hasFeedback(feedback) {
  return (
    feedback &&
    typeof feedback === "object" &&
    !Array.isArray(feedback) &&
    Object.keys(feedback).length > 0
  );
}



function formatDate(value) {
  if (!value) {
    return "Date unavailable";
  }


  const date =
    new Date(value);


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value);
  }


  return date.toLocaleString(
    undefined,
    {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }
  );
}

function getLocalDateString(
  date = new Date()
) {
  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(2, "0");

  const day =
    String(
      date.getDate()
    ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}


export default History;