import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import "./Login.css";
import { login, register } from "../services/api";

type Mode = "login" | "register";

interface FormState {
  name: string;
  email: string;
  password: string;
  confirm: string;
}

export default function Login() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>(
    searchParams.get("mode") === "register" ? "register" : "login"
  );

  const [form, setForm] = useState<FormState>({
    name: "",
    email: "",
    password: "",
    confirm: "",
  });
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "login") {
        const result = await login(form.email, form.password);
        // Store token in localStorage
        localStorage.setItem("token", result.token);
        // Navigate to landing/dashboard
        navigate("/landing");
      } else {
        // Register mode
        if (form.password !== form.confirm) {
          setError("Passwords do not match");
          setLoading(false);
          return;
        }
        await register(form.name, form.email, form.password);
        // Switch to login after successful registration
        setMode("login");
        setForm({ name: "", email: "", password: "", confirm: "" });
      }
    } catch (err: any) {
      setError(err.response?.data?.msg || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (next: Mode) => {
    setForm({ name: "", email: "", password: "", confirm: "" });
    setMode(next);
  };

  const isLogin = mode === "login";

  return (
    <div className="login-page">
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      <div className={`login-card ${isLogin ? "mode-login" : "mode-register"}`}>
        {/* Header */}
        <div className="card-header">
          <h1 className="card-title">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h1>
          <p className="card-sub">
            {isLogin ? (
              <>
                Don't have an account?{" "}
                <button className="link-btn" onClick={() => switchMode("register")}>
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button className="link-btn" onClick={() => switchMode("login")}>
                  Log in
                </button>
              </>
            )}
          </p>
        </div>

        {/* Fields */}
        <div className="fields">
          {/* Name — register only */}
          <div className={`field-wrap ${!isLogin ? "visible" : "hidden"}`}>
            <label className="field-label" htmlFor="name">
              Full Name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              className="field-input"
              placeholder="John Knight"
              value={form.name}
              onChange={handleChange}
              tabIndex={!isLogin ? 0 : -1}
            />
          </div>

          <div className="field-wrap visible">
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="field-input"
              placeholder="you@ucf.edu"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div className="field-wrap visible">
            <label className="field-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="field-input"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
            />
          </div>

          {/* Confirm password — register only */}
          <div className={`field-wrap ${!isLogin ? "visible" : "hidden"}`}>
            <label className="field-label" htmlFor="confirm">
              Confirm Password
            </label>
            <input
              id="confirm"
              name="confirm"
              type="password"
              className="field-input"
              placeholder="••••••••"
              value={form.confirm}
              onChange={handleChange}
              tabIndex={!isLogin ? 0 : -1}
            />
          </div>
        </div>

        {/* Error message */}
        {error && <p className="error-message">{error}</p>}

        {/* Submit */}
        <button className="btn-submit" onClick={handleSubmit} disabled={loading}>
          {loading ? "Please wait..." : (isLogin ? "Sign in" : "Create Account")}
        </button>

        {/* Forgot password — login only */}
        {isLogin && (
          <button className="link-btn forgot">Forgot password?</button>
        )}
      </div>
    </div>
  );
}