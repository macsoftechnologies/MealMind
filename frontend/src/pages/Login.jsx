import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { HeartPulse } from "lucide-react";

import { loginUser } from "../services/auth";
import { useAuth } from "../context/AuthContext";


function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await loginUser(email, password);

      // JWT was already stored by loginUser()
      // Now save the logged-in user in AuthContext
      login(data.user);

      navigate("/");
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Unable to login. Please try again.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-brand">
          <div className="brand-icon">
            <HeartPulse size={26} />
          </div>

          <div>
            <h1>MealMind</h1>
            <p>Smart Nutrition, Made Personal.</p>
          </div>
        </div>


        <div className="auth-heading">
          <h2>Welcome back</h2>
          <p>Sign in to continue to your nutrition dashboard.</p>
        </div>


        <form onSubmit={handleSubmit} className="auth-form">

          <div className="form-group">
            <label>Email</label>

            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>


          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="forgot-password-row">
            <button
              type="button"
              className="forgot-password-button"
              onClick={() => navigate("/forgot-password")}
              >
              Forgot password?
              </button>
          </div> 


          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}


          <button
            type="submit"
            className="auth-submit-button"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

        </form>


        <div className="auth-footer">
          <span>Don't have an account?</span>

          <button
            type="button"
            onClick={() => navigate("/register")}
          >
            Create account
          </button>
        </div>

      </div>

    </div>
  );
}


export default Login;