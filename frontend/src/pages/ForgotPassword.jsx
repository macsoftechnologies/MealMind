import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    ArrowLeft,
    HeartPulse,
} from "lucide-react";

import api from "../services/api";


function ForgotPassword() {
    const navigate = useNavigate();

    const [step, setStep] = useState(1);

    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");

    const [newPassword, setNewPassword] =
    useState("");

    const [confirmPassword, setConfirmPassword] =
    useState("");

    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);


    const sendOTP = async (event) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
        const response = await api.post(
        "/auth/forgot-password",
        {
            email: email.trim(),
        }
        );

        setMessage(response.data.message);
        setStep(2);

    } catch (error) {
        setError(
        error.response?.data?.detail ||
        "Unable to send verification code."
        );
    } finally {
        setLoading(false);
    }
    };


    const verifyOTP = async (event) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
        await api.post(
        "/auth/verify-reset-otp",
        {
            email: email.trim(),
            otp: otp.trim(),
        }
        );

        setMessage(
        "Verification successful."
        );

        setStep(3);

    } catch (error) {
        setError(
        error.response?.data?.detail ||
        "Invalid verification code."
        );
    } finally {
        setLoading(false);
    }
    };


    const resetPassword = async (event) => {
    event.preventDefault();

    setError("");
    setMessage("");

    if (newPassword.length < 8) {
        setError(
        "Password must contain at least 8 characters."
        );
        return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post(
        "/auth/reset-password",
        {
          email: email.trim(),
          otp: otp.trim(),
          new_password: newPassword,
        }
      );

      setMessage(response.data.message);
      setStep(4);

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        "Unable to reset password."
      );
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
            <p>
              Smart Nutrition, Made Personal.
            </p>
          </div>
        </div>


        {step === 1 && (
          <>
            <div className="auth-heading">
              <h2>Forgot password?</h2>

              <p>
                Enter your registered email and
                we'll send you a verification code.
              </p>
            </div>

            <form
              onSubmit={sendOTP}
              className="auth-form"
            >
              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="Enter your email"
                  required
                />
              </div>

              <Status
                error={error}
                message={message}
              />

              <button
                type="submit"
                className="auth-submit-button"
                disabled={loading}
              >
                {loading
                  ? "Sending..."
                  : "Send Verification Code"}
              </button>
            </form>
          </>
        )}


        {step === 2 && (
          <>
            <div className="auth-heading">
              <h2>Check your email</h2>

              <p>
                Enter the 6-digit code sent to
                your registered email.
              </p>
            </div>

            <form
              onSubmit={verifyOTP}
              className="auth-form"
            >
              <div className="form-group">
                <label>Verification Code</label>

                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  value={otp}
                  onChange={(event) =>
                    setOtp(
                      event.target.value.replace(
                        /\D/g,
                        ""
                      )
                    )
                  }
                  placeholder="Enter 6-digit code"
                  required
                />
              </div>

              <Status
                error={error}
                message={message}
              />

              <button
                type="submit"
                className="auth-submit-button"
                disabled={
                  loading ||
                  otp.length !== 6
                }
              >
                {loading
                  ? "Verifying..."
                  : "Verify Code"}
              </button>
            </form>
          </>
        )}


        {step === 3 && (
          <>
            <div className="auth-heading">
              <h2>Create new password</h2>

              <p>
                Choose a new password for your
                MealMind account.
              </p>
            </div>

            <form
              onSubmit={resetPassword}
              className="auth-form"
            >
              <div className="form-group">
                <label>New Password</label>

                <input
                  type="password"
                  value={newPassword}
                  onChange={(event) =>
                    setNewPassword(
                      event.target.value
                    )
                  }
                  placeholder="Minimum 8 characters"
                  minLength={8}
                  required
                />
              </div>

              <div className="form-group">
                <label>Confirm Password</label>

                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter password again"
                  minLength={8}
                  required
                />
              </div>

              <Status
                error={error}
                message={message}
              />

              <button
                type="submit"
                className="auth-submit-button"
                disabled={loading}
              >
                {loading
                  ? "Resetting..."
                  : "Reset Password"}
              </button>
            </form>
          </>
        )}


        {step === 4 && (
          <>
            <div className="auth-heading">
              <h2>Password changed</h2>

              <p>
                Your password has been reset
                successfully. You can now sign in.
              </p>
            </div>

            <Status
              error={error}
              message={message}
            />

            <button
              type="button"
              className="auth-submit-button"
              onClick={() => navigate("/login")}
            >
              Sign In
            </button>
          </>
        )}


        {step !== 4 && (
          <div className="auth-footer">
            <button
              type="button"
              onClick={() => navigate("/login")}
            >
              <ArrowLeft size={16} />
              Back to Sign In
            </button>
          </div>
        )}

      </div>

    </div>
  );
}


function Status({
  error,
  message,
}) {
  return (
    <>
      {error && (
        <div className="auth-error">
          {error}
        </div>
      )}

      {message && (
        <div className="auth-success">
          {message}
        </div>
      )}
    </>
  );
}


export default ForgotPassword;