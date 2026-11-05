import {
  ChevronLeft,
  ChevronRight,
  ArrowLeft,
  Plus,
  Clock,
} from "lucide-react";

import { useMemo, useState } from "react";

import "./MealCalendar.css";

import {
  createCalendarEvent,
} from "../services/api";


function MealCalendar({
  meals = [],
  selectedDate,
  onDateSelect,
  visibleMonth,
  onMonthChange,
  dayPlan = null,
  planLoading = false,
  customEvents = [],
  userId,
  onEventCreated,
}) {
  const [view, setView] =
    useState("month");

  const [
  showEventForm,
  setShowEventForm,
] = useState(false);

const [
  eventTitle,
  setEventTitle,
] = useState("");

const [
  eventTime,
  setEventTime,
] = useState("");

const [
  eventNotes,
  setEventNotes,
] = useState("");

const [
  savingEvent,
  setSavingEvent,
] = useState(false);

const [
  eventError,
  setEventError,
] = useState("");


  /*
   * MONTH CALENDAR DATA
   */

  const year =
    visibleMonth.getFullYear();

  const month =
    visibleMonth.getMonth();

  const monthName =
    visibleMonth.toLocaleDateString(
      undefined,
      {
        month: "long",
        year: "numeric",
      }
    );


  /*
   * Sunday based JS index:
   * Sun = 0
   *
   * We convert calendar to:
   * Mon Tue Wed Thu Fri Sat Sun
   */
  const firstDay =
    new Date(
      year,
      month,
      1
    );

  const firstDayIndex =
    (firstDay.getDay() + 6) % 7;


  const daysInMonth =
    new Date(
      year,
      month + 1,
      0
    ).getDate();


  /*
   * Previous month's trailing dates.
   */
  const previousMonthDays =
    new Date(
      year,
      month,
      0
    ).getDate();


  /*
   * Build 6 calendar rows.
   */
  const calendarDays =
    useMemo(() => {
      const days = [];

      for (
        let index = firstDayIndex - 1;
        index >= 0;
        index -= 1
      ) {
        const day =
          previousMonthDays -
          index;

        const date =
          new Date(
            year,
            month - 1,
            day
          );

        days.push({
          date,
          currentMonth: false,
        });
      }


      for (
        let day = 1;
        day <= daysInMonth;
        day += 1
      ) {
        days.push({
          date: new Date(
            year,
            month,
            day
          ),
          currentMonth: true,
        });
      }


      let nextDay = 1;

      while (
        days.length < 42
      ) {
        days.push({
          date: new Date(
            year,
            month + 1,
            nextDay
          ),
          currentMonth: false,
        });

        nextDay += 1;
      }

      return days;
    }, [
      year,
      month,
      firstDayIndex,
      previousMonthDays,
      daysInMonth,
    ]);


  /*
   * Dates containing actual
   * logged meals.
   */
  const mealDates =
    useMemo(() => {
      const dateSet =
        new Set();

      meals.forEach(
        (meal) => {
          const value =
            meal.created_at ||
            meal.analyzed_at ||
            meal.date;

          if (!value) {
            return;
          }

          const date =
            new Date(value);

          if (
            Number.isNaN(
              date.getTime()
            )
          ) {
            return;
          }

          dateSet.add(
            getLocalDateString(
              date
            )
          );
        }
      );

      return dateSet;
    }, [meals]);


  /*
   * When user clicks a date:
   *
   * Month view disappears.
   * Same card opens day schedule.
   */
  function handleDateClick(
    date
  ) {
    const value =
      getLocalDateString(
        date
      );

    onDateSelect(value);

    setView("day");
  }


  function goPreviousMonth() {
    onMonthChange(
      new Date(
        year,
        month - 1,
        1
      )
    );
  }


  function goNextMonth() {
    onMonthChange(
      new Date(
        year,
        month + 1,
        1
      )
    );
  }


  function goBackToCalendar() {
    setView("month");
  }


  /*
   * DAY VIEW DATA
   */

  const plannedMeals =
    getPlannedMeals(
      dayPlan
    );


  const plannedEvents =
    plannedMeals
      .filter((meal) =>
        isValidPlannedTime(
          meal.planned_time
        )
      )
      .map(
        (meal, index) => {
          const [
            hour,
            minute,
          ] =
            meal.planned_time
              .split(":")
              .map(Number);

          return {
            id:
              `planned-${index}`,

            type: "planned",

            title:
              `Time for ${
                formatMealName(
                  meal.meal_name
                )
              }`,

            hour,
            minute,

            time:
              meal.planned_time,
          };
        }
      );


  /*
   * Actual logged meals for
   * selected date.
   */
  const actualEvents =
    meals
      .filter((meal) =>
        isMealOnDate(
          meal.created_at ||
            meal.analyzed_at ||
            meal.date,
          selectedDate
        )
      )
      .map(
        (meal, index) => {
          const date =
            getMealTime(
              meal
            );

          return {
            id:
              meal.id ??
              meal.meal_id ??
              `actual-${index}`,

            type: "actual",

            title:
              "Meal logged",

            hour:
              date.getHours(),

            minute:
              date.getMinutes(),

            date,
          };
        }
      );


  const customTimelineEvents =
  customEvents
    .filter((event) =>
      event.event_date === selectedDate
    )
    .map((event) => {
      const timeValue =
        normalizeTime(event.start_time);

      const [hour, minute] =
        timeValue
          .split(":")
          .map(Number);

      return {
        id: `custom-${event.id}`,
        databaseId: event.id,
        type: "custom",
        title: event.title,
        notes: event.notes,
        hour,
        minute,
        time: timeValue,
      };
    });

const events = [
  ...plannedEvents,
  ...actualEvents,
  ...customTimelineEvents,
].sort((a, b) => {
  const aTime =
    a.hour * 60 + a.minute;

  const bTime =
    b.hour * 60 + b.minute;

  return aTime - bTime;
});

  const hours =
    getDayHours(events);

    async function handleSaveEvent(event) {
  event.preventDefault();

  setEventError("");

  const cleanTitle =
    eventTitle.trim();

  if (!cleanTitle) {
    setEventError(
      "Please enter an event title."
    );
    return;
  }

  if (!eventTime) {
    setEventError(
      "Please select a time."
    );
    return;
  }

  if (!userId || !selectedDate) {
    setEventError(
      "Unable to create event."
    );
    return;
  }

  try {
    setSavingEvent(true);

    await createCalendarEvent(
      userId,
      {
        event_date: selectedDate,
        start_time: eventTime,
        title: cleanTitle,
        notes: eventNotes.trim()
          ? eventNotes.trim()
          : null,
      }
    );

    setEventTitle("");
    setEventTime("");
    setEventNotes("");
    setEventError("");

    setShowEventForm(false);

    if (onEventCreated) {
      await onEventCreated();
    }
  } catch (err) {
    console.error(
      "Create calendar event error:",
      err
    );

    setEventError(
      err.response?.data?.detail ||
        "Could not save event."
    );
  } finally {
    setSavingEvent(false);
  }
}


function handleCloseEventForm() {
  if (savingEvent) {
    return;
  }

  setShowEventForm(false);

  setEventTitle("");
  setEventTime("");
  setEventNotes("");
  setEventError("");
}



  return (
    <section className="meal-calendar-card">

      {view === "month" ? (

/* ========================
MONTH VIEW
======================== */

        <>
          <div className="meal-calendar-header">

            <button
              type="button"
              className="calendar-nav-button"
              onClick={
                goPreviousMonth
              }
              aria-label="Previous month"
            >
              <ChevronLeft
                size={18}
              />
            </button>


            <h2>
              {monthName}
            </h2>


            <button
              type="button"
              className="calendar-nav-button"
              onClick={
                goNextMonth
              }
              aria-label="Next month"
            >
              <ChevronRight
                size={18}
              />
            </button>

          </div>


          <div className="calendar-weekdays">

            {[
              "Mon",
              "Tue",
              "Wed",
              "Thu",
              "Fri",
              "Sat",
              "Sun",
            ].map(
              (day) => (
                <span key={day}>
                  {day}
                </span>
              )
            )}

          </div>


          <div className="calendar-grid">

            {calendarDays.map(
              (
                item,
                index
              ) => {
                const dateString =
                  getLocalDateString(
                    item.date
                  );

                const isToday =
                  dateString ===
                  getLocalDateString(
                    new Date()
                  );

                const isSelected =
                  dateString ===
                  selectedDate;

                const hasMeal =
                  mealDates.has(
                    dateString
                  );

                return (
                  <button
                    type="button"
                    key={
                      `${dateString}-${index}`
                    }
                    className={[
                      "calendar-day",

                      !item.currentMonth
                        ? "calendar-day-muted"
                        : "",

                      isToday
                        ? "calendar-day-today"
                        : "",

                      isSelected
                        ? "calendar-day-selected"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() =>
                      handleDateClick(
                        item.date
                      )
                    }
                  >
                    <span>
                      {
                        item.date.getDate()
                      }
                    </span>

                    {hasMeal && (
                      <i className="calendar-meal-dot" />
                    )}

                  </button>
                );
              }
            )}

          </div>


          <div className="calendar-footer">
            <span>
              <i className="calendar-meal-dot calendar-footer-dot" />

              Logged meal
            </span>

            <small>
              Select a date to
              view schedule
            </small>
          </div>
        </>

      ) : (

        /* ========================
           DAY / EVENT VIEW
        ======================== */

        <>

          <div className="day-schedule-header">

            <button
              type="button"
              className="day-back-button"
              onClick={
                goBackToCalendar
              }
            >
              <ArrowLeft
                size={19}
              />
            </button>


            <div>
              <h2>
                {
                  formatSelectedDate(
                    selectedDate
                  )
                }
              </h2>

              <p>
                Daily schedule
              </p>
            </div>

          </div>


          {planLoading ? (

            <div className="day-schedule-empty">

              <Clock
                size={24}
              />

              <p>
                Loading schedule...
              </p>

            </div>

          ) : (

            <div className="day-schedule">

              {hours.map(
                (hour) => {
                  const hourEvents =
                    events.filter(
                      (event) =>
                        event.hour ===
                        hour
                    );

                  return (
                    <div
                      className="schedule-hour-row"
                      key={hour}
                    >

                      <div className="schedule-hour-label">
                        {
                          formatHour(
                            hour
                          )
                        }
                      </div>


                      <div className="schedule-hour-content">

                        <div className="schedule-hour-line" />


                        {hourEvents.length >
                          0 && (
                          <div className="schedule-events">

                            {hourEvents.map(
                              (
                                event
                              ) => (
                                <CalendarEvent
                                  key={
                                    event.id
                                  }
                                  event={
                                    event
                                  }
                                />
                              )
                            )}

                          </div>
                        )}

                      </div>

                    </div>
                  );
                }
              )}

            </div>
          )}


          <div className="schedule-add-area">

            <button
              type="button"
              className="schedule-add-button"
              onClick={() => {
              setEventError("");
              setShowEventForm(true);
            }}
            >
              <Plus
                size={17}
              />

              Add event
            </button>

          </div>

          {showEventForm && (
  <div
    className="calendar-modal-overlay"
    onMouseDown={
      handleCloseEventForm
    }
  >
    <div
      className="calendar-event-modal"
      onMouseDown={(event) =>
        event.stopPropagation()
      }
    >
      <div className="event-modal-header">
        <div>
          <h3>Add event</h3>

          <p>
            {formatSelectedDate(
              selectedDate
            )}
          </p>
        </div>

        <button
          type="button"
          className="event-modal-close"
          onClick={
            handleCloseEventForm
          }
        >
          ×
        </button>
      </div>


      <form
        onSubmit={
          handleSaveEvent
        }
      >
        <div className="event-form-group">
          <label>
            Event title
          </label>

          <input
            type="text"
            value={eventTitle}
            onChange={(event) =>
              setEventTitle(
                event.target.value
              )
            }
            placeholder="Example: Gym"
            maxLength={200}
            autoFocus
          />
        </div>


        <div className="event-form-group">
          <label>
            Time
          </label>

          <input
            type="time"
            value={eventTime}
            onChange={(event) =>
              setEventTime(
                event.target.value
              )
            }
          />
        </div>


        <div className="event-form-group">
          <label>
            Notes
            <span>Optional</span>
          </label>

          <textarea
            value={eventNotes}
            onChange={(event) =>
              setEventNotes(
                event.target.value
              )
            }
            placeholder="Add details..."
            rows={3}
          />
        </div>


        {eventError && (
          <div className="event-form-error">
            {eventError}
          </div>
        )}


        <div className="event-modal-actions">
          <button
            type="button"
            className="event-cancel-button"
            onClick={
              handleCloseEventForm
            }
            disabled={savingEvent}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="event-save-button"
            disabled={savingEvent}
          >
            {savingEvent
              ? "Saving..."
              : "Save event"}
          </button>
        </div>
      </form>
    </div>
  </div>
)}

        </>
      )}

    </section>
  );
}


function normalizeTime(value) {
  if (!value) {
    return "00:00";
  }

  return String(value).substring(0, 5);
}


function CalendarEvent({
  event,
}) {
  let displayTime = "";

  if (event.type === "actual") {
    displayTime =
      formatMealTime(event.date);
  } else {
    displayTime =
      formatPlannedTime(event.time);
  }

  return (
    <button
      type="button"
      className={[
        "schedule-event",

        event.type === "planned"
          ? "schedule-event-planned"
          : "",

        event.type === "actual"
          ? "schedule-event-actual"
          : "",

        event.type === "custom"
          ? "schedule-event-custom"
          : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="schedule-event-info">
        <strong>
          {event.type === "actual"
            ? `✓ ${event.title}`
            : event.title}
        </strong>

        {event.type === "custom" &&
          event.notes && (
            <small>
              {event.notes}
            </small>
          )}
      </div>

      <span>
        {displayTime}
      </span>
    </button>
  );
}
function getDayHours(
  events
) {
  /*
   * Always show a useful
   * daily range.
   *
   * This makes it feel like
   * a normal calendar even
   * when there are no events.
   */

  let startHour = 6;
  let endHour = 22;


  if (
    events.length > 0
  ) {
    const eventHours =
      events.map(
        (event) =>
          event.hour
      );

    const earliest =
      Math.min(
        ...eventHours
      );

    const latest =
      Math.max(
        ...eventHours
      );

    startHour =
      Math.min(
        startHour,
        Math.max(
          0,
          earliest - 1
        )
      );

    endHour =
      Math.max(
        endHour,
        Math.min(
          23,
          latest + 1
        )
      );
  }


  const hours = [];

  for (
    let hour = startHour;
    hour <= endHour;
    hour += 1
  ) {
    hours.push(
      hour
    );
  }

  return hours;
}


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


function formatMealName(
  value
) {
  if (!value) {
    return "Meal";
  }

  const normalized =
    String(value)
      .trim()
      .toLowerCase();

  return (
    normalized
      .charAt(0)
      .toUpperCase() +
    normalized.slice(1)
  );
}


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

  return formatMealTime(
    date
  );
}


function getMealTime(
  meal
) {
  return new Date(
    meal.created_at ||
      meal.analyzed_at ||
      meal.date
  );
}


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


function formatHour(
  hour
) {
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


function formatMealTime(
  date
) {
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


function formatSelectedDate(
  value
) {
  if (!value) {
    return "Selected day";
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
      month: "long",
      day: "numeric",
      year: "numeric",
    }
  );
}


export default MealCalendar;