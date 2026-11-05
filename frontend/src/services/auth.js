import api from "./api";

export const registerUser = async (userData) => {
  const response = await api.post("/auth/register", userData);

  if (response.data.access_token) {
    localStorage.setItem(
      "access_token",
      response.data.access_token
    );
  }

  return response.data;
};


export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  if (response.data.access_token) {
    localStorage.setItem(
      "access_token",
      response.data.access_token
    );
  }

  return response.data;
};


export const getCurrentUser = async () => {
  const response = await api.get("/auth/me");

  return response.data;
};


export const logoutUser = () => {
  localStorage.removeItem("access_token");
};


export const getToken = () => {
  return localStorage.getItem("access_token");
};