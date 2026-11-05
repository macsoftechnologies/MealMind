import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import DietPlan from "./pages/DietPlan";
import HealthProfile from "./pages/HealthProfile";
import History from "./pages/History";
import Login from "./pages/Login";
import MealAnalysis from "./pages/MealAnalysis";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  return (
    <BrowserRouter>

      <AuthProvider>

        <Routes>

          {/* ================================
              PUBLIC ROUTES
          ================================= */}

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />

          <Route
            path="/forgot-password"
            element={<ForgotPassword />}
          />


          {/* ================================
              PROTECTED ROUTES
          ================================= */}

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >

            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/health-profile"
              element={<HealthProfile />}
            />

            <Route
              path="/diet-plan"
              element={<DietPlan />}
            />

            <Route
              path="/meal-analysis"
              element={<MealAnalysis />}
            />

            <Route
              path="/history"
              element={<History />}
            />

          </Route>

        </Routes>

      </AuthProvider>

    </BrowserRouter>
  );
}


export default App;