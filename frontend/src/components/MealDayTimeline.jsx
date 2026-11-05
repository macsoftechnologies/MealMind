import {
  Clock,
  Flame,
} from "lucide-react";

import "./MealDayTimeline.css";


function MealDayTimeline({
  meals = [],
  selectedDate,
  dayPlan = null,
  planLoading = false,
}) {
  /*
   * Actual meals logged by the user
   * for the selected calendar date.
   */
  const selectedMeals = meals
    .filter((meal) =>
      isMealOnDate(
        meal.created_at ||
          meal.analyzed_at ||
          meal.date,
        selectedDate
      )
    )
    .sort(
      (a, b) =>
        getMealTime(a) -
        getMealTime(b)
    );


  /*
   * Planned meals from weekly
   * diet plan.
   */
  const plannedMeals =
    getPlannedMeals(dayPlan);


  /*
   * Convert planned meals into
   * simple calendar events.
   *
   * Example:
   * 08:00 -> Time for Breakfast
   */
  const plannedEvents =
    plannedMeals
      .filter((meal) =>
        isValidPlannedTime(
          meal.planned_time
        )
      )
      .map((meal, index) => {
        const [hour, minute] =
          meal.planned_time
            .split(":")
            .map(Number);

        return {
          id: `planned-${index}`,
          type: "planned",
          hour,
          minute,
          meal,
        };
      });


  /*
   * Convert actual logged meals
   * into calendar events.
   */
  const actualEvents =
    selectedMeals.map(
      (meal, index) => {
        const mealTime =
          getMealTime(meal);

        return {
          id:
            meal.id ??
            meal.meal_id ??
            `actual-${index}`,

          type: "actual",

          hour:
            mealTime.getHours(),

          minute:
            mealTime.getMinutes(),

          meal,
        };
      }
    );


  /*
   * Combine planned + actual
   * events and sort by time.
   */
  const timelineEvents = [
    ...plannedEvents,
    ...actualEvents,
  ].sort((a, b) => {
    const aMinutes =
      a.hour * 60 +
      a.minute;

    const bMinutes =
      b.hour * 60 +
      b.minute;

    return aMinutes - bMinutes;
  });


  /*
   * Generate only the useful
   * hours around the events.
   */
  const timelineHours =
    getTimelineHours(
      timelineEvents
    );


  return (
    <section className="meal-timeline-card">

      {/* Header */}

      <div className="meal-timeline-header">
        <div>
          <div className="meal-timeline-heading">
            <Clock size={18} />

            <h2>
              {formatSelectedDate(
                selectedDate
              )}
            </h2>
          </div>

          <p>
            Your schedule for this day.
          </p>
        </div>

        <div className="meal-timeline-count">
          {timelineEvents.length}{" "}
          {timelineEvents.length === 1
            ? "event"
            : "events"}
        </div>
      </div>


      {/* Loading */}

      {planLoading ? (
        <div className="meal-timeline-empty">
          <Clock size={24} />

          <p>
            Loading schedule...
          </p>
        </div>
      ) : timelineEvents.length === 0 ? (

        /* Empty day */

        <div className="meal-timeline-empty">
          <Clock size={24} />

          <p>
            No events available for
            this date.
          </p>
        </div>

      ) : (

        /* Hourly calendar */

        <div className="meal-timeline">

          {timelineHours.map(
            (hour) => {
              const hourEvents =
                timelineEvents.filter(
                  (event) =>
                    event.hour === hour
                );

              return (
                <div
                  className="meal-timeline-row"
                  key={hour}
                >

                  {/* Hour */}

                  <div className="meal-timeline-hour">
                    {formatHour(hour)}
                  </div>


                  {/* Timeline line */}

                  <div className="meal-timeline-slot">

                    <div className="meal-timeline-line" />

                    <div className="meal-timeline-events">

                      {hourEvents.map(
                        (event) => {

                          if (
                            event.type ===
                            "planned"
                          ) {
                            return (
                              <TimelinePlannedEvent
                                key={
                                  event.id
                                }
                                meal={
                                  event.meal
                                }
                              />
                            );
                          }

                          return (
                            <TimelineMealEvent
                              key={
                                event.id
                              }
                              meal={
                                event.meal
                              }
                            />
                          );
                        }
                      )}

                    </div>
                  </div>
                </div>
              );
            }
          )}

        </div>
      )}

    </section>
  );
}


/*
 * SIMPLE PLANNED EVENT
 *
 * No calories.
 * No foods.
 * No macros.
 *
 * Only:
 * Time for Breakfast
 * 8:00 AM
 */
function TimelinePlannedEvent({
  meal,
}) {
  const mealName =
    meal.meal_name ||
    "Meal";

  return (
    <button
      type="button"
      className="
        calendar-event
        calendar-event-planned
      "
    >
      <div className="calendar-event-main">

        <strong>
          Time for {mealName}
        </strong>

        <span>
          {formatPlannedTime(
            meal.planned_time
          )}
        </span>

      </div>
    </button>
  );
}


/*
 * ACTUAL LOGGED MEAL
 *
 * Keeps actual meal information
 * separate from planned events.
 */
function TimelineMealEvent({
  meal,
}) {
  const foods =
    getFoods(meal);

  const calories =
    meal.total_calories ??
    meal.meal_total?.calories ??
    meal.nutrition?.calories ??
    "--";

  const date =
    getMealTime(meal);

  return (
    <article className="timeline-meal-event">

      <div className="timeline-meal-marker" />

      <div className="timeline-meal-event-content">

        <div className="timeline-meal-event-top">

          <div>
            <span className="timeline-meal-status">
              MEAL LOGGED
            </span>

            <strong>
              {getMealTitle(
                foods
              )}
            </strong>
          </div>

          <span className="timeline-meal-clock">
            {formatMealTime(
              date
            )}
          </span>

        </div>


        <div className="timeline-meal-meta">

          <span>
            <Flame size={13} />

            {calories} kcal
          </span>

          {meal.total_protein_g !==
            undefined &&
            meal.total_protein_g !==
              null && (
              <span>
                {
                  meal.total_protein_g
                }
                g protein
              </span>
            )}

        </div>

      </div>

    </article>
  );
}


/*
 * Generate timeline hours.
 *
 * Example:
 *
 * Breakfast = 8 AM
 * Lunch = 1 PM
 * Dinner = 8 PM
 *
 * Timeline:
 * 7 AM -> 10 PM
 */
function getTimelineHours(events) {
  if (
    !events ||
    events.length === 0
  ) {
    return [];
  }

  const eventHours =
    events.map(
      (event) =>
        event.hour
    );

  const earliestHour =
    Math.min(
      ...eventHours
    );

  const latestHour =
    Math.max(
      ...eventHours
    );

  const startHour =
    Math.max(
      5,
      earliestHour - 1
    );

  const endHour =
    Math.min(
      23,
      latestHour + 2
    );

  const hours = [];

  for (
    let hour = startHour;
    hour <= endHour;
    hour += 1
  ) {
    hours.push(hour);
  }

  return hours;
}


/*
 * Get actual meal timestamp.
 */
function getMealTime(meal) {
  const value =
    meal.created_at ||
    meal.analyzed_at ||
    meal.date;

  return new Date(value);
}


/*
 * Check whether actual meal
 * belongs to selected date.
 */
function isMealOnDate(
  value,
  selectedDate
) {
  if (
    !value ||
    !selectedDate
  ) {
    return false;
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return false;
  }

  return (
    getLocalDateString(
      date
    ) === selectedDate
  );
}


/*
 * Convert Date -> YYYY-MM-DD
 */
function getLocalDateString(
  date
) {
  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(
      2,
      "0"
    );

  const day =
    String(
      date.getDate()
    ).padStart(
      2,
      "0"
    );

  return `${year}-${month}-${day}`;
}


/*
 * 8 -> 8 AM
 * 13 -> 1 PM
 */
function formatHour(hour) {
  const date =
    new Date();

  date.setHours(
    hour,
    0,
    0,
    0
  );

  return date.toLocaleTimeString(
    undefined,
    {
      hour: "numeric",
    }
  );
}


/*
 * Format actual logged meal time.
 */
function formatMealTime(date) {
  if (
    !(date instanceof Date) ||
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  return date.toLocaleTimeString(
    undefined,
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );
}


/*
 * Selected calendar date heading.
 */
function formatSelectedDate(
  value
) {
  if (!value) {
    return "Selected Day";
  }

  const [
    year,
    month,
    day,
  ] =
    value
      .split("-")
      .map(Number);

  const date =
    new Date(
      year,
      month - 1,
      day
    );

  return date.toLocaleDateString(
    undefined,
    {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    }
  );
}


/*
 * Get foods from different
 * possible meal response shapes.
 */
function getFoods(meal) {
  if (
    Array.isArray(
      meal.foods
    )
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


/*
 * Build simple actual meal title.
 */
function getMealTitle(foods) {
  if (!foods.length) {
    return "Logged Meal";
  }

  const names =
    foods
      .slice(0, 3)
      .map(
        (food) =>
          food.food_name ||
          food.name
      )
      .filter(Boolean);

  if (!names.length) {
    return "Logged Meal";
  }

  const title =
    names.join(", ");

  return foods.length > 3
    ? `${title} +${
        foods.length - 3
      } more`
    : title;
}


/*
 * Get selected day's planned
 * meals from API response.
 */
function getPlannedMeals(
  dayPlan
) {
  if (!dayPlan) {
    return [];
  }

  if (
    Array.isArray(
      dayPlan.meals
    )
  ) {
    return dayPlan.meals;
  }

  if (
    dayPlan.day &&
    Array.isArray(
      dayPlan.day.meals
    )
  ) {
    return dayPlan.day.meals;
  }

  if (
    dayPlan.day_plan &&
    Array.isArray(
      dayPlan.day_plan.meals
    )
  ) {
    return dayPlan.day_plan.meals;
  }

  return [];
}


/*
 * Validate HH:MM
 */
function isValidPlannedTime(
  value
) {
  if (
    typeof value !==
      "string" ||
    !/^\d{2}:\d{2}$/.test(
      value
    )
  ) {
    return false;
  }

  const [
    hour,
    minute,
  ] =
    value
      .split(":")
      .map(Number);

  return (
    hour >= 0 &&
    hour <= 23 &&
    minute >= 0 &&
    minute <= 59
  );
}


/*
 * 08:00 -> 8:00 AM
 * 13:00 -> 1:00 PM
 */
function formatPlannedTime(
  value
) {
  if (
    !isValidPlannedTime(
      value
    )
  ) {
    return "";
  }

  const [
    hour,
    minute,
  ] =
    value
      .split(":")
      .map(Number);

  const date =
    new Date();

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


export default MealDayTimeline;