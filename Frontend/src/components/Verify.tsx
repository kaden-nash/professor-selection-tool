import { useEffect, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Login.css";

export default function Verify() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    const token = searchParams.get("token");
    if (!token) {
      setStatus("error");
      setMessage("No verification token found.");
      return;
    }

    api.get(`/auth/verify?token=${token}`)
      .then((res) => {
        setStatus("success");
        setMessage(res.data.msg);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.msg || "Verification failed.");
      });
  }, []);

  return (
    <div className="login-page">
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="login-card mode-login" style={{ textAlign: "center" }}>
        <div className="card-header">
          <h1 className="card-title">
            {status === "loading" && "Verifying..."}
            {status === "success" && "Email Verified!"}
            {status === "error" && "Verification Failed"}
          </h1>
          <p className="card-sub">{message}</p>
        </div>
        {status !== "loading" && (
          <button className="btn-submit" onClick={() => navigate("/login")}>
            Go to Login
          </button>
        )}
      </div>
    </div>
  );
}
