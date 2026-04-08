import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css"; // Reuse your existing login styles for consistency
// import { requestPasswordReset } from "../services/api"; // You'll likely need this helper

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Replace this with your actual API call
      // await requestPasswordReset(email);
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      setSubmitted(true);
    } catch (err: any) {
      setError(err.response?.data?.msg || "Failed to send reset email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {!submitted ? (
          <>
            <h1 className="auth-title">Reset Password</h1>
            <p className="auth-sub">
              Enter your email and we'll send you a link to get back into your account.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="auth-field">
                <label className="auth-label">Email</label>
                <input
                  className="auth-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                />
              </div>

              {error && <p className="auth-error">{error}</p>}

              <button className="auth-btn" type="submit" disabled={loading}>
                {loading ? "Sending..." : "Send Reset Link"}
              </button>

              <div className="auth-forgot-container" style={{ marginTop: "1.5rem", textAlign: "center" }}>
                <button 
                  type="button" 
                  className="auth-link-small" 
                  onClick={() => navigate("/login")}
                >
                  Back to login
                </button>
              </div>
            </form>
          </>
        ) : (
          <div style={{ textAlign: "center" }}>
            <h1 className="auth-title">Check your email</h1>
            <p className="auth-sub" style={{ marginBottom: "2rem" }}>
              We've sent a password reset link to <strong>{email}</strong>.
            </p>
            <button className="auth-btn" onClick={() => navigate("/login")}>
              Return to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}