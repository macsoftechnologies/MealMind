import React, {
  useEffect,
  useState,
} from "react";

import {
  getDietPlanByDate,
  getMealsByDate,
} from "../services/api";

import "./DietCalendar.css";


function DietCalendar({ userId }) {
  const [selectedDate, setSelectedDate] =
    useState(
      new Date()
        .toISOString()
        .split("T")[0]
    );

  const [plannedDay, setPlannedDay] =
    useState(null);

  const [actualMeals, setActualMeals] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  // ============================================================
  // LOAD DATA WHEN DATE CHANGES
  // ============================================================

  useEffect(() => {
    if (!userId || !selectedDate) {
      return;
    }

    loadSelectedDate();
  }, [userId, selectedDate]);


  // ============================================================
  // LOAD PLANNED + ACTUAL MEALS
  // ============================================================

  const loadSelectedDate = async () => {
    setLoading(true);
    setError("");

    try {
      const [
        planResponse,
        mealsResponse,
      ] = await Promise.all([
        getDietPlanByDate(
          userId,
          selectedDate
        ),

        getMealsByDate(
          userId,
          selectedDate
        ),
      ]);


      setPlannedDay(
        planResponse.day_plan || null
      );


      setActualMeals(
        Array.isArray(
          mealsResponse.meals
        )
          ? mealsResponse.meals
          : []
      );

    } catch (err) {
      console.error(
        "Calendar loading error:",
        err
      );

      setPlannedDay(null);
      setActualMeals([]);

      setError(
        err.response?.data?.detail ||
          "No diet information available for this date."
      );

    } finally {
      setLoading(false);
    }
  };


  // ============================================================
  // CALCULATE ACTUAL CALORIES
  // ============================================================

  const actualCalories =
    actualMeals.reduce(
      (total, meal) =>
        total +
        Number(
          meal.meal_total?.calories ||
            0
        ),
      0
    );


  // ============================================================
  // CALCULATE ACTUAL PROTEIN
  // ============================================================

  const actualProtein =
    actualMeals.reduce(
      (total, meal) =>
        total +
        Number(
          meal.meal_total?.protein_g ||
            0
        ),
      0
    );


  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="diet-calendar">

      {/* HEADER */}

      <div className="calendar-header">

        <div>

          <h2>
            Nutrition Calendar
          </h2>

          <p>
            View your planned and actual
            meals for any day.
          </p>

        </div>


        <input
          type="date"
          value={selectedDate}
          onChange={(event) =>
            setSelectedDate(
              event.target.value
            )
          }
        />

      </div>


      {/* LOADING */}

      {loading && (
        <p>
          Loading nutrition day...
        </p>
      )}


      {/* ERROR */}

      {!loading && error && (
        <div className="calendar-message">
          {error}
        </div>
      )}


      {/* SELECTED DAY */}

      {!loading &&
        !error &&
        plannedDay && (

          <div className="selected-day">

            {/* DAY HEADER */}

            <div className="selected-day-title">

              <div>

                <h3>
                  {plannedDay.day_name}
                </h3>

                <span>
                  {selectedDate}
                </span>

              </div>


              <div>
                {actualMeals.length}{" "}
                meals logged
              </div>

            </div>


            {/* ACTUAL NUTRITION SUMMARY */}

            <div className="daily-summary">

              <div className="summary-card">

                <span>
                  Actual Calories
                </span>

                <strong>
                  {Math.round(
                    actualCalories
                  )}{" "}
                  kcal
                </strong>

              </div>


              <div className="summary-card">

                <span>
                  Actual Protein
                </span>

                <strong>
                  {actualProtein.toFixed(
                    1
                  )}{" "}
                  g
                </strong>

              </div>


              <div className="summary-card">

                <span>
                  Meals Logged
                </span>

                <strong>
                  {actualMeals.length}
                </strong>

              </div>

            </div>


            {/* PLANNED VS ACTUAL */}

            <div className="planned-actual-grid">

              {/* PLANNED */}

              <div className="day-column">

                <h3>
                  Planned
                </h3>


                {(plannedDay.meals || [])
                  .map(
                    (meal, index) => (

                      <div
                        className="calendar-meal-card"
                        key={
                          `${selectedDate}-planned-${index}`
                        }
                      >

                        <strong>
                          {meal.meal_name ||
                            `Meal ${index + 1}`}
                        </strong>


                        {(meal.foods || [])
                          .map(
                            (
                              food,
                              foodIndex
                            ) => (

                              <p
                                key={
                                  foodIndex
                                }
                              >

                                {food.food_name ||
                                  food.name ||
                                  "Food"}

                                {food.portion &&
                                  ` — ${food.portion}`}

                              </p>

                            )
                          )}


                        <small>

                          {Math.round(
                            Number(
                              meal.estimated_calories ||
                                0
                            )
                          )}{" "}
                          kcal

                        </small>

                      </div>

                    )
                  )}

              </div>


              {/* ACTUALLY EATEN */}

              <div className="day-column">

                <h3>
                  Actually Eaten
                </h3>


                {actualMeals.length ===
                0 ? (

                  <div className="calendar-meal-card">

                    No meals logged for
                    this date.

                  </div>

                ) : (

                  actualMeals.map(
                    (meal, mealIndex) => (

                      <div
                        className="calendar-meal-card"
                        key={
                          meal.meal_id ||
                          `${selectedDate}-actual-${mealIndex}`
                        }
                      >

                        {(meal.foods || [])
                          .map(
                            (
                              food,
                              foodIndex
                            ) => (

                              <p
                                key={
                                  foodIndex
                                }
                              >

                                {food.food_name ||
                                  food.name ||
                                  "Food"}

                                {(food.approximate_portion ||
                                  food.portion ||
                                  food.quantity) &&
                                  ` — ${
                                    food.approximate_portion ||
                                    food.portion ||
                                    food.quantity
                                  }`}

                              </p>

                            )
                          )}


                        <small>

                          {Math.round(
                            Number(
                              meal.meal_total
                                ?.calories ||
                                0
                            )
                          )}{" "}
                          kcal

                        </small>

                      </div>

                    )
                  )

                )}

              </div>

            </div>

          </div>

        )}

    </div>
  );
}


export default DietCalendar;