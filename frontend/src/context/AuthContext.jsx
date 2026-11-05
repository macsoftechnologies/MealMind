import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getCurrentUser,
  getToken,
  logoutUser,
} from "../services/auth";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    const loadUser = async () => {
      const token = getToken();

      // No token = user is not logged in
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // Token automatically goes through api.js
        const currentUser = await getCurrentUser();

        setUser(currentUser);
      } catch (error) {
        // Token may be invalid or expired
        logoutUser();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);


  const login = (userData) => {
    setUser(userData);
  };


  const logout = () => {
    logoutUser();
    setUser(null);
  };


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  return useContext(AuthContext);
}