import { useEffect, useRef } from "react";
import "./Landing.css";

interface ScoreMetric {
  label: string;
  val: number;
}

const metrics: ScoreMetric[] = [
  { label: "Retake", val: 95 },
  { label: "Quality", val: 88 },
  { label: "Difficulty", val: 72 },
];

export default function Landing() {
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const lines = headingRef.current?.querySelectorAll<HTMLElement>(".line");
    lines?.forEach((line, i) => {
      line.style.animationDelay = `${i * 0.15}s`;
    });
  }, []);

  return (
    <div className="landing">
      {/* Noise overlay */}
      <div className="noise" />

      {/* Gradient orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      {/* Nav */}
      <nav className="nav">
        <span className="nav-logo">KnightRate</span>
        <div className="nav-actions">
          <button className="btn-ghost">Login</button>
          <button className="btn-solid">Join</button>
        </div>
      </nav>

      {/* Hero */}
      <main className="hero">
        <div className="hero-content">
          <h1 className="heading" ref={headingRef}>
            <span className="line">THE SMART WAY</span>
            <span className="line">TO FIND PROFESSORS</span>
            <span className="line accent-line">AND COURSES AT UCF.</span>
          </h1>

          <p className="subtext">
            Our unique composite scoring algorithm finds the right professors
            for you — over 10 different metrics calculated into one number.
          </p>

          <button className="btn-cta">
            Get Started
            <span className="btn-arrow">→</span>
          </button>
        </div>

        {/* Decorative score card */}
        <div className="score-card">
          <div className="score-label">Composite Score</div>
          <div className="score-value">92.4</div>
          <div className="score-bars">
            {metrics.map((item) => (
              <div className="bar-row" key={item.label}>
                <span className="bar-label">{item.label}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ "--w": `${item.val}%` } as React.CSSProperties}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}