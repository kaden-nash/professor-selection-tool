import { useState } from "react";
import Navbar from "./Navbar";
import "./Starred.css";

type Tab = "professors" | "courses";

const MOCK_STARRED_PROFS = [
  {
    id: "1",
    name: "Andrew Steinberg",
    sentimentRating: 24.5,
    rmpTags: 42.5,
    rmpDifficulty: 12.8,
    rmpQuality: 15.4,
    clarityScore: 17.9,
    total: 92.7,
    overview: ["Fair grader", "Accessible outside of class", "Extra credit", "Polarizing → Yes"],
  },
  {
    id: "2",
    name: "Aashish Yadavally",
    sentimentRating: 20.1,
    rmpTags: 38.0,
    rmpDifficulty: 10.5,
    rmpQuality: 13.2,
    clarityScore: 15.0,
    total: 88.2,
    overview: ["Detailed feedback", "Office hours available"],
  },
];

const MOCK_STARRED_COURSES = [
  { id: "cop4331", name: "COP 4331: Processes of Object Oriented Software Development" },
];

export default function Starred() {
  const [tab, setTab] = useState<Tab>("professors");
  const [expandedId, setExpandedId] = useState<string | null>(MOCK_STARRED_PROFS[0]?.id ?? null);

  return (
    <div className="starred-page">
      <Navbar />
      <div className="starred-body">
        <h1 className="starred-heading">View Starred Items</h1>

        {/* Tabs */}
        <div className="starred-tabs">
          <button
            className={`starred-tab ${tab === "professors" ? "active" : ""}`}
            onClick={() => setTab("professors")}
          >Professors</button>
          <button
            className={`starred-tab ${tab === "courses" ? "active" : ""}`}
            onClick={() => setTab("courses")}
          >Courses</button>
        </div>

        {/* Content */}
        <div className="starred-list">
          {tab === "professors" ? (
            MOCK_STARRED_PROFS.map(prof => (
              <div key={prof.id}>
                {expandedId === prof.id ? (
                  <div className="starred-card expanded">
                    <div className="starred-card-inner">
                      <div className="starred-card-header">
                        <span className="starred-card-title">Score Breakdown</span>
                        <span className="starred-star active">★</span>
                      </div>
                      <div className="starred-card-content">
                        <div className="starred-prof-info">
                          <div className="starred-avatar" />
                          <span className="starred-prof-name">{prof.name}</span>
                        </div>
                        <div className="starred-scores">
                          {[
                            { label: "Sentiment Rating:", val: prof.sentimentRating },
                            { label: "RMP Tags:", val: prof.rmpTags },
                            { label: "RMP Difficulty Score:", val: prof.rmpDifficulty },
                            { label: "RMP Quality Score:", val: prof.rmpQuality },
                            { label: "Clarity Score:", val: prof.clarityScore },
                          ].map(({ label, val }) => (
                            <div key={label} className="score-breakdown-row">
                              <span className="breakdown-label">{label}</span>
                              <span className="breakdown-val">{val}</span>
                            </div>
                          ))}
                          <div className="score-breakdown-divider" />
                          <div className="score-breakdown-total">
                            <span>Total:</span>
                            <span className="total-circle">{prof.total}</span>
                          </div>
                        </div>
                      </div>
                      <div className="starred-overview">
                        <p className="overview-title">Overview</p>
                        <ul className="overview-list">
                          {prof.overview.map((item, i) => (
                            <li key={i}>• {item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="starred-card collapsed" onClick={() => setExpandedId(prof.id)}>
                    <div className="collapsed-left">
                      <div className="collapsed-avatar" />
                      <span className="collapsed-name">{prof.name}</span>
                    </div>
                    <span className="collapsed-score">{prof.total}</span>
                  </div>
                )}
              </div>
            ))
          ) : (
            MOCK_STARRED_COURSES.map(course => (
              <div key={course.id} className="starred-course-card">
                <span>{course.name}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
