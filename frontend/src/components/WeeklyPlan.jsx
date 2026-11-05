import React from "react";
import "./WeeklyPlan.css";
function WeeklyPlan({ weeklyPlan }) {
  if (
    !weeklyPlan ||
    !Array.isArray(weeklyPlan.days)
  ) {
    return null;
  }

  return (
    <div className="weekly-plan">
      <div className="weekly-plan-header">
        <div>
          <h2>Your 7-Day Diet Plan</h2>

          <p>
            {weeklyPlan.week_start_date}
            {" → "}
            {weeklyPlan.week_end_date}
          </p>
        </div>
      </div>

      {weeklyPlan.weekly_note && (
        <div className="weekly-note">
          <strong>Weekly guidance</strong>

          <p>
            {weeklyPlan.weekly_note}
          </p>
        </div>
      )}

      <div className="weekly-days">
        {weeklyPlan.days.map((day) => (
          <div
            className="weekly-day-card"
            key={day.date}
          >
            <div className="weekly-day-header">
              <div>
                <h3>{day.day_name}</h3>
                <span>{day.date}</span>
              </div>

              <div className="day-calories">
                {Math.round(
                  Number(day.total_calories || 0)
                )}{" "}
                kcal
              </div>
            </div>

            <div className="weekly-meals">
              {(day.meals || []).map(
                (meal, index) => (
                  <div
                    className="weekly-meal"
                    key={`${day.date}-${index}`}
                  >
                    <div className="meal-heading">
  <div>
    <h4>
      {meal.meal_name}
    </h4>

    {meal.planned_time && (
      <small className="meal-planned-time">
        {formatPlannedTime(
          meal.planned_time
        )}
      </small>
    )}
  </div>

  <span>
    {Math.round(
      Number(
        meal.estimated_calories ||
          0
      )
    )}{" "}
    kcal
  </span>
</div>

                    <div className="meal-foods">
                      {(meal.foods || []).map(
                        (food, foodIndex) => (
                          <div
                            className="meal-food"
                            key={foodIndex}
                          >
                            <span>
                              {food.food_name}
                            </span>

                            <small>
                              {food.portion}
                            </small>
                          </div>
                        )
                      )}
                    </div>

                    <div className="meal-macros">
                      <span>
                        Protein{" "}
                        {meal.protein_g || 0}g
                      </span>

                      <span>
                        Carbs{" "}
                        {meal.carbohydrates_g ||
                          0}
                        g
                      </span>

                      <span>
                        Fat{" "}
                        {meal.fat_g || 0}g
                      </span>

                      <span>
                        Fiber{" "}
                        {meal.fiber_g || 0}g
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>

            {day.daily_tip && (
              <div className="daily-tip">
                <strong>Daily tip</strong>
                <p>{day.daily_tip}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function formatPlannedTime(value) {
  if (
    !value ||
    !/^\d{2}:\d{2}$/.test(value)
  ) {
    return "";
  }

  const [hour, minute] =
    value.split(":").map(Number);

  const date = new Date();

  date.setHours(
    hour,
    minute,
    0,
    0
  );

  return date.toLocaleTimeString(
    undefined,
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );
}
export default WeeklyPlan;