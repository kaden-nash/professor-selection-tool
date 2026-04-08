import { useNavigate } from "react-router-dom";
import "./Landing.css";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Nav */}
      <nav className="landing-nav">
        <button className="nav-login-link" onClick={() => navigate("/login")}>Login</button>
        <button className="nav-join-btn" onClick={() => navigate("/register")}>Join</button>
      </nav>

      {/* Hero */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            THE SMART WAY<br />
            TO FIND PROFESSORS<br />
            AND COURSES AT UCF.
          </h1>
          <p className="hero-sub">
            Our unique composite scoring algorithm finds the right professors
            for you – over 10 different metrics calculated into one number.
          </p>
          <button className="hero-cta" onClick={() => navigate("/register")}>
            Get Started
          </button>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-section">
        <h2 className="how-title">HOW IT WORKS</h2>
        <p className="how-sub">
          Our application web-scrapes data from the following sources to
          calculate a unique professor rating:
        </p>
        <ul className="how-list">
          <li>RateMyProfessor</li>
          <li>SPI Surveys</li>
          <li>LinkedIn</li>
          <li>+ more</li>
        </ul>
      </section>
    </div>
  );
}
