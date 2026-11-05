import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { HeartPulse } from "lucide-react";

import { registerUser } from "../services/auth";
import { useAuth } from "../context/AuthContext";


function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const payload = {
        ...formData,
        age: Number(formData.age),
        height_cm: Number(formData.height_cm),
        weight_kg: Number(formData.weight_kg),
      };

      const data = await registerUser(payload);

      // registerUser already saves the JWT
      login(data.user);

      navigate("/health-profile");
    } catch (error) {
      const detail = error.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Unable to create account. Please check your details.");
      }
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-page">

      <div className="auth-card register-card">

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
          <h2>Create your account</h2>
          <p>
            Start building a nutrition plan personalized to you.
          </p>
        </div>


        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <div className="form-group">
            <label>Full name</label>

            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
            />
          </div>


          <div className="form-group">
            <label>Email</label>

            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
            />
          </div>


          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Minimum 8 characters"
              minLength={8}
              required
            />
          </div>


          <div className="auth-form-row">

            <div className="form-group">
              <label>Age</label>

              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                placeholder="Age"
                min="1"
                max="119"
                required
              />
            </div>


            <div className="form-group">
              <label>Gender</label>

              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                required
              >
                <option value="">Select</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

          </div>


          <div className="auth-form-row">

            <div className="form-group">
              <label>Height (cm)</label>

              <input
                type="number"
                name="height_cm"
                value={formData.height_cm}
                onChange={handleChange}
                placeholder="175"
                min="1"
                step="0.1"
                required
              />
            </div>


            <div className="form-group">
              <label>Weight (kg)</label>

              <input
                type="number"
                name="weight_kg"
                value={formData.weight_kg}
                onChange={handleChange}
                placeholder="70"
                min="1"
                step="0.1"
                required
              />
            </div>

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
            {loading ? "Creating account..." : "Create Account"}
          </button>

        </form>


        <div className="auth-footer">
          <span>Already have an account?</span>

          <button
            type="button"
            onClick={() => navigate("/login")}
          >
            Sign in
          </button>
        </div>

      </div>

    </div>
  );
}


export default Register;