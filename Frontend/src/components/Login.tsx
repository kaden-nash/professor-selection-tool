import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { login } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(form.email, form.password);
      localStorage.setItem("token", result.token);
      navigate("/search");
    } catch (err: any) {
      setError(err.response?.data?.msg || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-sub">
          Don't have an account yet?{" "}
          <button className="auth-link" onClick={() => navigate("/register")}>Sign up</button>
        </p>

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">Email</label>
            <input
              className="auth-input"
              name="email"
              type="email"
              placeholder="john@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Password</label>
            <input
              className="auth-input"
              name="password"
              type="password"
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-forgot-container">
            <button 
              type="button" 
              className="auth-link-small" 
              onClick={() => navigate("/forgot-password")}
            >
              Forgot password?
            </button>
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? "Please wait..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}