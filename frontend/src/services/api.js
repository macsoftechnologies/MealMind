import axios from "axios";


// ============================================================
// AXIOS API INSTANCE
// ============================================================

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,
});


// ============================================================
// AUTOMATICALLY ATTACH JWT TOKEN
// ============================================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


// ============================================================
// GENERATE WEEKLY DIET PLAN
// ============================================================

export const generateWeeklyDietPlan = async (
  userId,
  data
) => {
  const response = await api.post(
    `/users/${userId}/diet-plan/weekly`,
    data,
    {
      timeout: 180000,
    }
  );

  return response.data;
};


// ============================================================
// GET CURRENT WEEKLY DIET PLAN
// ============================================================

export const getWeeklyDietPlan = async (
  userId
) => {
  const response = await api.get(
    `/users/${userId}/diet-plan/weekly`
  );

  return response.data;
};


// ============================================================
// GET DIET PLAN FOR SELECTED DATE
// ============================================================

export const getDietPlanByDate = async (
  userId,
  selectedDate
) => {
  const response = await api.get(
    `/users/${userId}/diet-plan/date/${selectedDate}`
  );

  return response.data;
};


// ============================================================
// GET ACTUAL MEALS FOR SELECTED DATE
// ============================================================

export const getMealsByDate = async (
  userId,
  selectedDate
) => {
  const response = await api.get(
    `/users/${userId}/meals`,
    {
      params: {
        date: selectedDate,
      },
    }
  );

  return response.data;
};


export const getCalendarEvents =
  async (
    userId,
    selectedDate
  ) => {
    const response =
      await api.get(
        `/users/${userId}/calendar-events`,
        {
          params: {
            date: selectedDate,
          },
        }
      );

    return response.data;
  };


export const createCalendarEvent =
  async (
    userId,
    data
  ) => {
    const response =
      await api.post(
        `/users/${userId}/calendar-events`,
        data
      );

    return response.data;
  };


export const updateCalendarEvent =
  async (
    userId,
    eventId,
    data
  ) => {
    const response =
      await api.patch(
        `/users/${userId}/calendar-events/${eventId}`,
        data
      );

    return response.data;
  };


export const deleteCalendarEvent =
  async (
    userId,
    eventId
  ) => {
    const response =
      await api.delete(
        `/users/${userId}/calendar-events/${eventId}`
      );

    return response.data;
  };

// ============================================================
// DEFAULT EXPORT
// ============================================================

export default api;