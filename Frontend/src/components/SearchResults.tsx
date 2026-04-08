import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./SearchResults.css";

// Unicorn icon SVG inline
const UnicornIcon = () => (
  <div className="archetype-icon">
    <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" width="48" height="48">
      <path d="M32 8 C20 8 12 18 12 30 C12 42 20 50 32 50 C44 50 52 42 52 30 C52 18 44 8 32 8Z" stroke="white" strokeWidth="2" fill="none"/>
      <path d="M32 8 L36 2" stroke="white" strokeWidth="2"/>
      <path d="M28 14 C26 10 30 6 34 8" stroke="white" strokeWidth="1.5" fill="none"/>
    </svg>
  </div>
);

interface Professor {
  id: string;
  name: string;
  score: number;
  archetype: string;
  archetypeDesc: string;
  retake: number;
  quality: number;
  difficulty: number;
  overall: number;
  lastTaught: string;
  polarizing: boolean;
  tags: string[];
  overview: string[];
  photo?: string;
}

// Mock data — replace with real API calls
const MOCK_PROFESSORS: Professor[] = [
  {
    id: "1",
    name: "Andrew Steinberg",
    score: 92.7,
    archetype: "The Unicorn",
    archetypeDesc: "GPA savior, top tier teaching, zero stress.",
    retake: 67.3,
    quality: 70.2,
    difficulty: 92.7,
    overall: 92.7,
    lastTaught: "Fall 25'",
    polarizing: true,
    tags: ["Fair Grader", "Extra Credit", "Fair Grader"],
    overview: ["Fair grader", "Accessible outside of class", "Extra credit", "Polarizing → Yes"],
  },
  {
    id: "2",
    name: "Aashish Yadavally",
    score: 88.2,
    archetype: "The Mastermind",
    archetypeDesc: "Challenging but rewarding. High quality instruction.",
    retake: 55.0,
    quality: 68.0,
    difficulty: 80.0,
    overall: 88.2,
    lastTaught: "Spring 25'",
    polarizing: false,
    tags: ["Tough Grader", "Helpful"],
    overview: ["Detailed feedback", "Office hours available"],
  },
  {
    id: "3",
    name: "Paul Gazillo",
    score: 80.7,
    archetype: "The Mastermind",
    archetypeDesc: "Deep knowledge, expects hard work.",
    retake: 50.0,
    quality: 60.0,
    difficulty: 75.0,
    overall: 80.7,
    lastTaught: "Fall 24'",
    polarizing: false,
    tags: ["Tough Grader"],
    overview: ["Research focused", "Clear expectations"],
  },
];

const MOCK_COURSES = [
  { id: "cop4331", name: "COP 4331: Processes of Object Oriented Software Development" },
  { id: "cop3502", name: "COP 3502: Computer Science I" },
  { id: "cop3503", name: "COP 3503: Computer Science II" },
];

const UCF_AVG = 34.2;

const TAG_COLORS: Record<string, string> = {
  "Fair Grader": "#7c3aed",
  "Extra Credit": "#0ea5e9",
  "Tough Grader": "#dc2626",
  "Helpful": "#16a34a",
};

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const type = searchParams.get("type") || "professor";
  const filter = searchParams.get("filter") || "name";
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [activeFilter, setActiveFilter] = useState(filter);
  const [expandedId, setExpandedId] = useState<string | null>(MOCK_PROFESSORS[0]?.id ?? null);
  const [starred, setStarred] = useState<Set<string>>(new Set());

  const isProfessor = type === "professor";

  const toggleStar = (id: string) => {
    setStarred(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search-results?type=${type}&filter=${activeFilter}&q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="results-page">
      <Navbar />

      <div className="results-body">
        <h1 className="results-heading">
          {isProfessor ? `Results for: ${initialQuery}` : "Search for UCF courses"}
        </h1>

        {/* Radio + search bar */}
        <div className="results-filters">
          <label className="radio-label">
            <input type="radio" value="name" checked={activeFilter === "name"} onChange={() => setActiveFilter("name")} />
            Name
          </label>
          <label className="radio-label">
            <input type="radio" value="course" checked={activeFilter === "course"} onChange={() => setActiveFilter("course")} />
            Course
          </label>
        </div>
        <form onSubmit={handleSearch}>
          <input
            className="results-search-input"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder={activeFilter === "name" ? "Enter name here" : "Enter course name or code here"}
          />
        </form>

        {/* Results */}
        <div className="results-list">
          {isProfessor ? (
            MOCK_PROFESSORS.map(prof => (
              <div key={prof.id}>
                {expandedId === prof.id ? (
                  /* Expanded card */
                  <div className="prof-card expanded">
                    <div className="prof-card-top">
                      <div className="prof-archetype-col">
                        <span className="archetype-label">{prof.archetype}</span>
                        <UnicornIcon />
                        <p className="archetype-desc">{prof.archetypeDesc}</p>
                        <p className="prof-meta"><strong>Last Time Taught:</strong> {prof.lastTaught}</p>
                        <p className="prof-meta"><strong>Polarizing →</strong> {prof.polarizing ? "Yes" : "No"}</p>
                      </div>
                      <div className="prof-scores-col">
                        <div className="prof-name-row">
                          <span className="prof-name">{prof.name}</span>
                          <button
                            className={`star-btn ${starred.has(prof.id) ? "starred" : ""}`}
                            onClick={() => toggleStar(prof.id)}
                          >★</button>
                        </div>
                        <div className="legend-row">
                          <span className="legend-dot ucf" />
                          <span className="legend-text">UCF Average</span>
                          <span className="legend-dot prof" />
                          <span className="legend-text">{prof.name}</span>
                        </div>
                        {[
                          { label: "Retake Score:", val: prof.retake },
                          { label: "Quality Score:", val: prof.quality },
                          { label: "Difficulty Score:", val: prof.difficulty },
                          { label: "Overall Score:", val: prof.overall },
                        ].map(({ label, val }) => (
                          <div key={label} className="score-row">
                            <span className="score-row-label">{label}</span>
                            <div className="score-track">
                              <div className="score-bar ucf-bar" style={{ width: `${(UCF_AVG / 100) * 100}%` }} />
                              <div className="score-bar prof-bar" style={{ width: `${(val / 100) * 100}%` }} />
                            </div>
                            <span className="score-vals">{UCF_AVG} — {val}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="prof-tags">
                      {prof.tags.map((tag, i) => (
                        <span key={i} className="tag" style={{ background: TAG_COLORS[tag] || "#555" }}>{tag}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  /* Collapsed card */
                  <div className="prof-card collapsed" onClick={() => setExpandedId(prof.id)}>
                    <div className="collapsed-left">
                      <div className="collapsed-avatar" />
                      <span className="collapsed-name">{prof.name}</span>
                    </div>
                    <span className="collapsed-score">{prof.score}</span>
                  </div>
                )}
              </div>
            ))
          ) : (
            MOCK_COURSES.filter(c =>
              c.name.toLowerCase().includes(initialQuery.toLowerCase()) ||
              c.id.toLowerCase().includes(initialQuery.toLowerCase())
            ).map(course => (
              <div key={course.id} className="course-result">
                <span className="course-name">{course.name}</span>
                <UnicornIcon />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
