import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { register } from "../services/api";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const result = await register(form.name, form.email, form.password);
      setSuccess(result.msg);
      setForm({ name: "", email: "", password: "" });
    } catch (err: any) {
      setError(err.response?.data?.msg || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-sub">
          Already have an account yet?{" "}
          <button className="auth-link" onClick={() => navigate("/login")}>Log in</button>
        </p>

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">Full Name</label>
            <input
              className="auth-input"
              name="name"
              type="text"
              placeholder="John Doe"
              value={form.name}
              onChange={handleChange}
              required
            />
          </div>

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
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          {error && <p className="auth-error">{error}</p>}
          {success && <p className="auth-success">{success}</p>}

          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? "Please wait..." : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}