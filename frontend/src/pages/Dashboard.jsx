import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  Camera,
  Utensils,
  Flame,
  Beef,
  Wheat,
  Droplets,
  ArrowRight,
  Circle,
  UserRound,
  History,
} from "lucide-react";

import { Link } from "react-router-dom";
import api, {
  getWeeklyDietPlan,
  getMealsByDate,
} from "../services/api";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

function Dashboard() {
  const { user: authUser } = useAuth();
  const USER_ID = authUser.id;
  const [profile, setProfile] = useState(null);
  const [dietPlan, setDietPlan] = useState(null);
  const [meals, setMeals] = useState([]);

  const [weeklyGraphData, setWeeklyGraphData] =
  useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    loadDashboard();
  }, []);


  async function loadDashboard() {
  try {
    setLoading(true);
    setError("");

    const today = getLocalDateString();

    // ========================================================
    // LOAD PROFILE + WEEKLY PLAN + TODAY'S MEALS
    // ========================================================

    const [
      profileResult,
      dietPlanResult,
      mealsResult,
    ] = await Promise.allSettled([
      api.get(
        `/users/${USER_ID}/profile`
      ),

      getWeeklyDietPlan(
        USER_ID
      ),

      getMealsByDate(
        USER_ID,
        today
      ),
    ]);


    // ========================================================
    // PROFILE
    // ========================================================

    if (
      profileResult.status ===
      "fulfilled"
    ) {
      setProfile(
        profileResult.value.data
      );
    }


    // ========================================================
    // TODAY'S ACTUAL MEALS
    // ========================================================

    if (
      mealsResult.status ===
      "fulfilled"
    ) {
      const data =
        mealsResult.value;

      setMeals(
        Array.isArray(data)
          ? data
          : Array.isArray(
              data?.meals
            )
            ? data.meals
            : []
      );
    }


    // ========================================================
    // WEEKLY DIET PLAN
    // ========================================================

    if (
      dietPlanResult.status ===
      "fulfilled"
    ) {
      const plan =
        dietPlanResult.value;

      setDietPlan(plan);


      const weeklyPlan =
        plan?.weekly_plan;


      if (
        weeklyPlan &&
        Array.isArray(
          weeklyPlan.days
        )
      ) {
        const targetCalories =
          Number(
            plan
              ?.nutrition_targets
              ?.target_calories ||
              0
          );


        // ====================================================
        // LOAD ACTUAL MEALS FOR ALL 7 DAYS
        // ====================================================

        const graphData = await Promise.all(
  weeklyPlan.days.map(async (day) => {
    try {
      const mealData = await getMealsByDate(
        USER_ID,
        day.date
      );

      const dayMeals = Array.isArray(mealData)
        ? mealData
        : Array.isArray(mealData?.meals)
          ? mealData.meals
          : [];

      const nutrition =
        calculateConsumedNutrition(dayMeals);

      const actualCalories = Math.round(
        nutrition.calories
      );

      const adherence =
        calculateCalorieAdherence(
          actualCalories,
          targetCalories
        );

      const isFuture = day.date > today;
      const isToday = day.date === today;

      return {
        date: day.date,

        day: getShortDayName(
          day.day_name
        ),

        actualCalories: isFuture
          ? null
          : actualCalories,

        targetCalories: Math.round(
          targetCalories
        ),

        adherence: isFuture
          ? null
          : adherence,

        status: isFuture
          ? "upcoming"
          : isToday
            ? "today"
            : "completed",
      };
    } catch (dayMealError) {
      console.error(
        `Could not load meals for ${day.date}:`,
        dayMealError
      );

      const isFuture = day.date > today;
      const isToday = day.date === today;

      return {
        date: day.date,

        day: getShortDayName(
          day.day_name
        ),

        actualCalories: isFuture
          ? null
          : 0,

        targetCalories: Math.round(
          targetCalories
        ),

        adherence: isFuture
          ? null
          : 0,

        status: isFuture
          ? "upcoming"
          : isToday
            ? "today"
            : "completed",
      };
    }
  })
);
        setWeeklyGraphData(
          graphData
        );
      }
    }


    if (
      profileResult.status ===
      "rejected"
    ) {
      setError(
        "Could not load your health profile."
      );
    }

  } catch (err) {
    console.error(
      "Dashboard error:",
      err
    );

    setError(
      "Could not load your dashboard."
    );

  } finally {
    setLoading(false);
  }
}

  if (loading) {
    return (
      <div className="page-state">

        <div className="loading-spinner"></div>

        <h2>
          Loading your dashboard
        </h2>

        <p>
          Preparing your MealMind nutrition overview.
        </p>

      </div>
    );
  }


  const user =
    profile?.user || profile;


  const health =
    profile?.health_profile;


  const targets =
    dietPlan?.nutrition_targets || {};


  const today =
  getLocalDateString();


  const weeklyDays =
    dietPlan?.weekly_plan?.days;


  const todayPlan =
    Array.isArray(weeklyDays)
      ? weeklyDays.find(
          (day) =>
            day.date === today
        )
      : null;


  const plannedMeals =
    Array.isArray(
      todayPlan?.meals
    )
      ? todayPlan.meals
      : [];


  /*
   * These are today's meals only.
   */
  const consumed =
    calculateConsumedNutrition(meals);


  return (
    <div className="dashboard">

      {/* Welcome */}

      <section className="welcome-section">

        <div>

          <p className="eyebrow">
            YOUR DAILY NUTRITION
          </p>


          <h1>
            Good to see you
            {user?.name
              ? `, ${user.name}`
              : ""}{" "}
            👋
          </h1>


          <p className="welcome-description">
            Stay consistent with your meals and keep
            moving toward your nutrition goal.
          </p>

        </div>


        <div className="goal-badge">

          Goal

          <strong>
            {formatGoal(
              health?.goal
            )}
          </strong>

        </div>

      </section>


      {/* Error */}

      {error && (
        <div className="message-box error-message">
          {error}
        </div>
      )}


      {/* Today's Nutrition */}

      <section className="nutrition-section">

        <div className="section-heading">

          <div>

            <h2>
              Today's Nutrition
            </h2>

            <p>
              Nutrition from meals analyzed today
              compared with your daily targets
            </p>

          </div>


          <span className="date-label">
            Today
          </span>

        </div>


        {dietPlan ? (

          <div className="nutrition-grid">

            <NutritionCard
              icon={
                <Flame size={22} />
              }
              label="Calories"
              consumed={
                consumed.calories
              }
              target={
                targets.target_calories
              }
              unit="kcal"
            />


            <NutritionCard
              icon={
                <Beef size={22} />
              }
              label="Protein"
              consumed={
                consumed.protein
              }
              target={
                targets.protein_g
              }
              unit="g"
            />


            <NutritionCard
              icon={
                <Wheat size={22} />
              }
              label="Carbohydrates"
              consumed={
                consumed.carbohydrates
              }
              target={
                targets.carbohydrates_g
              }
              unit="g"
            />


            <NutritionCard
              icon={
                <Droplets size={22} />
              }
              label="Fat"
              consumed={
                consumed.fat
              }
              target={
                targets.fat_g
              }
              unit="g"
            />

          </div>

        ) : (

          <div className="dashboard-empty-card">

            <Utensils size={25} />

            <div>

              <strong>
                No diet plan yet
              </strong>

              <p>
                Generate your personalized diet plan
                to see your daily nutrition targets.
              </p>

            </div>


            <Link
              to="/diet-plan"
              className="text-link"
            >
              Create plan
              <ArrowRight size={15} />
            </Link>

          </div>

        )}

      </section>


{/* ======================================================
    WEEKLY NUTRITION PROGRESS
====================================================== */}

<section className="weekly-progress-section">

  <div className="section-heading">

    <div>

      <h2>
        Weekly Nutrition Progress
      </h2>

      <p>
        Your actual calorie intake compared
        with your daily calorie target.
      </p>

    </div>

  </div>


  {weeklyGraphData.length > 0 ? (

    <div className="weekly-chart-card">

      <div className="weekly-chart-header">
        <div>
          <strong>
            Weekly Calorie Trend
          </strong>

        <span>
          Daily calorie intake compared with your target
        </span>
      </div>

    <div className="chart-period-badge">
      7 Days
    </div>
  </div>


      <div
        className="weekly-chart-container"
      >

        <ResponsiveContainer
  width="100%"
  height="100%"
>
  <AreaChart
    data={weeklyGraphData}
    margin={{
      top: 15,
      right: 25,
      left: 0,
      bottom: 5,
    }}
  >
    <defs>
      <linearGradient
        id="calorieAreaGradient"
        x1="0"
        y1="0"
        x2="0"
        y2="1"
      >
        <stop
          offset="0%"
          stopColor="#16A34A"
          stopOpacity={0.22}
        />

        <stop
          offset="70%"
          stopColor="#16A34A"
          stopOpacity={0.06}
        />

        <stop
          offset="100%"
          stopColor="#16A34A"
          stopOpacity={0}
        />
      </linearGradient>
    </defs>

    <CartesianGrid
      stroke="#E5E7EB"
      strokeDasharray="3 6"
      vertical={false}
    />

    <XAxis
      dataKey="day"
      axisLine={false}
      tickLine={false}
      tick={{
        fill: "#64748B",
        fontSize: 12,
        fontWeight: 500,
      }}
      dy={8}
    />

    <YAxis
      axisLine={false}
      tickLine={false}
      tick={{
        fill: "#94A3B8",
        fontSize: 11,
      }}
      width={45}
    />

    <Tooltip
      cursor={{
        stroke: "#CBD5E1",
        strokeWidth: 1,
        strokeDasharray: "4 4",
      }}
      contentStyle={{
        backgroundColor: "#FFFFFF",
        border: "1px solid #E2E8F0",
        borderRadius: "12px",
        padding: "10px 14px",
        boxShadow:
          "0 10px 30px rgba(15, 23, 42, 0.12)",
      }}
      labelStyle={{
        color: "#0F172A",
        fontWeight: 700,
        marginBottom: "6px",
      }}
      formatter={(value, name) => {
        if (value === null) {
          return ["Upcoming", "Actual Calories"];
        }

        return [
          `${Math.round(Number(value))} kcal`,
          name === "actualCalories"
            ? "Actual Calories"
            : "Target Calories",
        ];
      }}
    />

    <Legend
      verticalAlign="top"
      align="right"
      height={38}
      iconType="circle"
      wrapperStyle={{
        fontSize: "12px",
        color: "#475569",
      }}
      formatter={(value) =>
        value === "actualCalories"
          ? "Actual Calories"
          : "Target Calories"
      }
    />

    <Area
      type="monotone"
      dataKey="actualCalories"
      name="actualCalories"
      stroke="#16A34A"
      strokeWidth={3}
      fill="url(#calorieAreaGradient)"
      connectNulls={false}
      dot={{
        r: 4,
        fill: "#FFFFFF",
        stroke: "#16A34A",
        strokeWidth: 2.5,
      }}
      activeDot={{
        r: 6,
        fill: "#16A34A",
        stroke: "#FFFFFF",
        strokeWidth: 3,
      }}
      animationDuration={900}
      animationEasing="ease-out"
    />

    <Line
      type="monotone"
      dataKey="targetCalories"
      name="targetCalories"
      stroke="#DC2626"
      strokeWidth={2}
      strokeDasharray="7 6"
      dot={false}
      activeDot={{
        r: 4,
        fill: "#DC2626",
        stroke: "#FFFFFF",
        strokeWidth: 2,
      }}
      animationDuration={900}
    />
  </AreaChart>
</ResponsiveContainer>

      </div>


      <div className="weekly-adherence-grid">
        {weeklyGraphData.map((day) => (
          <div
            className="weekly-adherence-item"
            key={day.date}
          >
            <span>
              {day.day}
            </span>

            {day.status === "upcoming" ? (
              <>
                <strong>—</strong>
                <small>Upcoming</small>
              </>
            ) : day.status === "today" ? (
              <>
                <strong>{day.adherence}%</strong>
                <small>Today</small>
              </>
            ) : (
              <>
                <strong>{day.adherence}%</strong>
                <small>Adherence</small>
              </>
            )}
          </div>
        ))}
      </div>

    </div>

  ) : (

    <div className="dashboard-empty-card">

      <Utensils size={24} />

      <div>

        <strong>
          No weekly data yet
        </strong>

        <p>
          Generate your 7-day diet plan
          to start tracking your weekly
          nutrition progress.
        </p>

      </div>


      <Link
        to="/diet-plan"
        className="text-link"
      >
        Create weekly plan
        <ArrowRight size={15} />
      </Link>

    </div>

  )}

</section>

      <section>

        <div className="section-heading">

          <div>

            <h2>
              Quick Actions
            </h2>

            <p>
              What would you like to do?
            </p>

          </div>

        </div>


        <div className="action-grid">

          <Link
            to="/meal-analysis"
            className="action-card primary-action"
          >

            <div className="action-icon">
              <Camera size={27} />
            </div>


            <div>

              <h3>
                Analyze Your Meal
              </h3>

              <p>
                Upload a meal photo and get nutrition
                estimates with personalized feedback.
              </p>

              <span>
                Analyze meal
                <ArrowRight size={17} />
              </span>

            </div>

          </Link>


          <Link
            to="/diet-plan"
            className="action-card"
          >

            <div className="action-icon">
              <Utensils size={27} />
            </div>


            <div>

              <h3>
                My Diet Plan
              </h3>

              <p>
                View your personalized daily meals,
                nutrition targets and recommendations.
              </p>

              <span>
                View diet plan
                <ArrowRight size={17} />
              </span>

            </div>

          </Link>

        </div>

      </section>


      {/* Current Diet Plan */}

      <section className="today-plan">

        <div className="section-heading">

          <div>

            <h2>
              Today's Meal Plan
            </h2>

            <p>
              Meals from your latest personalized
              diet plan
            </p>

          </div>


          <Link
            to="/diet-plan"
            className="text-link"
          >
            View full plan
            <ArrowRight size={16} />
          </Link>

        </div>


        {plannedMeals.length > 0 ? (

          <div className="meal-list">

            {plannedMeals.map(
              (meal, index) => (

                <MealStatus
                  key={index}
                  name={
                    meal.meal_name ||
                    meal.name ||
                    meal.meal ||
                    `Meal ${index + 1}`
                  }
                  description={
                    getMealDescription(
                      meal
                    )
                  }
                  calories={
                    getMealCalories(
                      meal
                    )
                  }
                />

              )
            )}

          </div>

        ) : (

          <div className="dashboard-empty-card">

            <Utensils size={24} />

            <div>

              <strong>
                No planned meals
              </strong>

              <p>
                Generate a diet plan to see your
                personalized meals here.
              </p>

            </div>

          </div>

        )}

      </section>


      {/* Today's Activity */}

      <section>

        <div className="section-heading">

          <div>

            <h2>
              Today's Activity
            </h2>

            <p>
              Meals you analyzed today
            </p>

          </div>


          <Link
            to="/history"
            className="text-link"
          >
            View history
            <ArrowRight size={16} />
          </Link>

        </div>


        <div className="dashboard-activity-card">

          <div className="dashboard-activity-icon">
            <History size={21} />
          </div>


          <div>

            <strong>
              {meals.length}{" "}
              {meals.length === 1
                ? "meal analyzed today"
                : "meals analyzed today"}
            </strong>


            <span>
              Your complete meal history is available
              in Meal History.
            </span>

          </div>


          <Link
            to="/history"
            className="dashboard-activity-arrow"
          >
            <ArrowRight size={18} />
          </Link>

        </div>

      </section>


      {/* Profile Shortcut */}

      <section>

        <div className="dashboard-profile-strip">

          <div className="dashboard-profile-icon">
            <UserRound size={21} />
          </div>


          <div>

            <strong>
              Health Profile
            </strong>


            <span>
              {formatActivity(
                health?.activity_level
              )}

              {" • "}

              {formatDiet(
                health?.diet_preference
              )}
            </span>

          </div>


          <Link
            to="/health-profile"
            className="text-link"
          >
            View profile
            <ArrowRight size={15} />
          </Link>

        </div>

      </section>

    </div>
  );
}



function NutritionCard({
  icon,
  label,
  consumed,
  target,
  unit,
}) {
  const consumedNumber =
    Number(consumed) || 0;

  const targetNumber =
    Number(target) || 0;


  const progress =
    calculateProgress(
      consumedNumber,
      targetNumber
    );


  const status =
    getNutritionStatus(
      progress
    );


  const difference =
    consumedNumber -
    targetNumber;


  return (
    <div
      className={
        `nutrition-card nutrition-card-${status}`
      }
    >

      <div className="nutrition-card-top">

        <div className="nutrition-icon">
          {icon}
        </div>

        <span>
          {label}
        </span>

      </div>


      <div className="nutrition-value">
        {formatNumber(
          consumedNumber
        )}
        {unit === "g"
          ? "g"
          : ""}
      </div>


      <div className="nutrition-target">
        of{" "}
        {formatNumber(
          targetNumber
        )}{" "}
        {unit}
      </div>


      <div
        className={`progress-track progress-track-${status}`}
      >

        <div
          className={
            `progress-fill progress-fill-${status}`
          }
          style={{
            width: `${Math.min(
              progress,
              100
            )}%`,
          }}
        />

      </div>


      <div
        className={
          `progress-label progress-label-${status}`
        }
      >

        {status === "exceeded" ? (

          <>
            {formatNumber(
              Math.abs(difference)
            )}{" "}
            {unit} over target
          </>

        ) : status === "warning" ? (

          <>
            {progress}% of daily target
            {" • "}
            approaching limit
          </>

        ) : (

          <>
            {progress}% of daily target
          </>

        )}

      </div>

    </div>
  );
}



function MealStatus({
  name,
  description,
  calories,
}) {
  return (
    <div className="meal-status">

      <div className="meal-status-icon">
        <Circle size={22} />
      </div>


      <div className="meal-information">

        <strong>
          {name}
        </strong>

        <span>
          {description}
        </span>

      </div>


      <span className="meal-calories">
        {calories}
      </span>

    </div>
  );
}



function calculateConsumedNutrition(meals) {
  return meals.reduce(
    (total, meal) => {

      total.calories += Number(
        meal.total_calories ??
        meal.meal_total?.calories ??
        0
      );


      total.protein += Number(
        meal.total_protein_g ??
        meal.meal_total?.protein_g ??
        0
      );


      total.carbohydrates += Number(
        meal.total_carbohydrates_g ??
        meal.meal_total?.carbohydrates_g ??
        0
      );


      total.fat += Number(
        meal.total_fat_g ??
        meal.meal_total?.fat_g ??
        0
      );


      return total;

    },
    {
      calories: 0,
      protein: 0,
      carbohydrates: 0,
      fat: 0,
    }
  );
}



function calculateProgress(
  consumed,
  target
) {
  const targetNumber =
    Number(target);


  if (
    !targetNumber ||
    targetNumber <= 0
  ) {
    return 0;
  }


  return Math.round(
    (
      Number(consumed) /
      targetNumber
    ) * 100
  );
}



function getNutritionStatus(
  progress
) {
  /*
   * 0 - 90%   = safe
   * 91 - 100% = warning
   * > 100%    = exceeded
   */

  if (progress > 100) {
    return "exceeded";
  }


  if (progress > 90) {
    return "warning";
  }


  return "safe";
}



function getMealDescription(meal) {
  const foods =
    meal.foods ||
    meal.items ||
    meal.food_items ||
    [];


  if (!Array.isArray(foods)) {
    return "Personalized meal";
  }


  const names = foods
    .slice(0, 3)
    .map((food) => {

      if (
        typeof food === "string"
      ) {
        return food;
      }


      return (
        food.food_name ||
        food.name
      );

    })
    .filter(Boolean);


  if (!names.length) {
    return "Personalized meal";
  }


  return names.join(", ");
}



function getMealCalories(meal) {
  const calories =
    meal.estimated_calories ??
    meal.calories;


  if (
    calories === undefined ||
    calories === null
  ) {
    return "--";
  }


  return `${Math.round(
    Number(calories)
  )} kcal`;
}



function getLocalDateString() {
  const now =
    new Date();


  const year =
    now.getFullYear();


  const month =
    String(
      now.getMonth() + 1
    ).padStart(
      2,
      "0"
    );


  const day =
    String(
      now.getDate()
    ).padStart(
      2,
      "0"
    );


  return `${year}-${month}-${day}`;
}



function formatNumber(value) {
  const number =
    Number(value);


  if (
    Number.isNaN(number)
  ) {
    return 0;
  }


  return Math.round(number);
}



function formatGoal(goal) {
  const goals = {
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
    goals[goal] ||
    "Not Set"
  );
}



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
    "Diet Not Set"
  );
}



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
    "Activity Not Set"
  );
}

function getShortDayName(
  dayName
) {
  if (!dayName) {
    return "";
  }

  return dayName
    .substring(0, 3);
}


function calculateCalorieAdherence(
  actualCalories,
  targetCalories
) {
  const actual =
    Number(
      actualCalories
    );

  const target =
    Number(
      targetCalories
    );


  if (
    !target ||
    target <= 0
  ) {
    return 0;
  }


  if (
    actual <= 0
  ) {
    return 0;
  }


  const difference =
    Math.abs(
      actual - target
    );


  const score =
    100 -
    (
      difference /
      target
    ) *
      100;


  return Math.max(
    0,
    Math.min(
      100,
      Math.round(score)
    )
  );
}

export default Dashboard;