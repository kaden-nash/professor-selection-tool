import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./SearchResults.css";
import { searchProfessors } from "../services/api";
import unicornImg from "../assets/unicorn.png";
import mastermindImg from "../assets/brain.png";
import saboteurImg from "../assets/bomb.png";
import npcImg from "../assets/bot.png";
import { starProfessor, unstarProfessor } from "../services/api";

interface Professor {
  _id: string;
  firstName: string;
  lastName: string;
  overallScore: number;
  archetype: string;
  retakeScore: number;
  qualityScore: number;
  difficultyScore: number;
  lastTimeTaught: string;
  isPolarizing: boolean;
  rmpTags: string[];
}

const UCF_AVG = 34.2;

const TAG_COLORS: Record<string, string> = {
  "Fair Grader":  "#7c3aed",
  "Extra Credit": "#0ea5e9",
  "Tough Grader": "#dc2626",
  "Helpful":      "#16a34a",
};

const ARCHETYPE_DESC: Record<string, string> = {
  "The Unicorn":    "GPA savior, top tier teaching, zero stress.",
  "The Mastermind": "Challenging but rewarding. High quality instruction.",
  "The NPC":        "Gets the job done. Nothing more, nothing less.",
  "The Saboteur":   "Proceed with caution. High risk, high stress.",
};

const ARCHETYPE_IMG: Record<string, string> = {
  "The Unicorn":    unicornImg,
  "The Mastermind": mastermindImg,
  "The NPC":        npcImg,
  "The Saboteur":   saboteurImg,
};

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const filter       = searchParams.get("filter") || "name";
  const initialQuery = searchParams.get("q")      || "";

  const [query, setQuery]               = useState(initialQuery);
  const [activeFilter, setActiveFilter] = useState(filter);
  const [professors, setProfessors]     = useState<Professor[]>([]);
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState("");
  const [expandedId, setExpandedId]     = useState<string | null>(null);
  const [starred, setStarred]           = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!initialQuery.trim()) return;

    const fetchResults = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await searchProfessors(filter, initialQuery);
        setProfessors(data);
        if (data.length > 0) setExpandedId(data[0]._id);
      } catch (err: any) {
        setError(err.response?.data?.msg || "Failed to fetch results.");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [filter, initialQuery]);

  const toggleStar = async (id: string) => {
  try {
    if (starred.has(id)) {
      await unstarProfessor(id);
      setStarred(prev => { const next = new Set(prev); next.delete(id); return next; });
    } else {
      await starProfessor(id);
      setStarred(prev => new Set(prev).add(id));
    }
  } catch (err) {
    console.error("Star toggle failed:", err);
  }
};

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/search-results?filter=${activeFilter}&q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="results-page">
      <Navbar />

      <div className="results-body">
        <h1 className="results-heading">Results for: {initialQuery}</h1>

        <div className="results-filters">
          <label className="radio-label">
            <input type="radio" value="name" checked={activeFilter === "name"}
              onChange={() => setActiveFilter("name")} />
            Name
          </label>
          <label className="radio-label">
            <input type="radio" value="course" checked={activeFilter === "course"}
              onChange={() => setActiveFilter("course")} />
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

        {loading && <p className="results-status">Searching...</p>}
        {error   && <p className="results-status error">{error}</p>}
        {!loading && !error && professors.length === 0 && initialQuery && (
          <p className="results-status">No professors found for "{initialQuery}".</p>
        )}

        <div className="results-list">
          {professors.map(prof => {
            const fullName = `${prof.firstName} ${prof.lastName}`;
            const isExpanded = expandedId === prof._id;
            const archetypeImg = ARCHETYPE_IMG[prof.archetype];

            return (
              <div key={prof._id}>
                {isExpanded ? (
                  <div className="prof-card expanded">
                    <div className="prof-card-top">

                      {/* Left col — archetype */}
                      <div className="prof-archetype-col">
                        <span className="archetype-label">{prof.archetype}</span>
                        <div className="archetype-icon">
                          <img
                            src={archetypeImg}
                            alt={prof.archetype}
                            style={{ width: "60px", height: "60px", objectFit: "contain" }}
                          />
                        </div>
                        <p className="archetype-desc">{ARCHETYPE_DESC[prof.archetype]}</p>
                        <p className="prof-meta"><strong>Last Time Taught:</strong> {prof.lastTimeTaught}</p>
                        <p className="prof-meta"><strong>Controversial →</strong> {prof.isPolarizing ? "Yes" : "No"}</p>
                      </div>

                      {/* Right col — scores */}
                      <div className="prof-scores-col">
                        <div className="prof-name-row">
                          <span className="prof-name">{fullName}</span>
                          <button
                            className={`star-btn ${starred.has(prof._id) ? "starred" : ""}`}
                            onClick={() => toggleStar(prof._id)}
                          >★</button>
                        </div>

                        <div className="legend-row">
                          <span className="legend-dot ucf" />
                          <span className="legend-text">UCF Average</span>
                          <span className="legend-dot prof" />
                          <span className="legend-text">{fullName}</span>
                        </div>

                        {[
                          { label: "Retake Score:",     val: prof.retakeScore },
                          { label: "Quality Score:",    val: prof.qualityScore },
                          { label: "Difficulty Score:", val: prof.difficultyScore },
                          { label: "Overall Score:",    val: prof.overallScore },
                        ].map(({ label, val }) => (
                          <div key={label} className="score-row">
                            <span className="score-row-label">{label}</span>
                            <div className="score-track">
                              <div className="score-line" />
                              <div className="ucf-bar" style={{ left: `${UCF_AVG}%` }} />
                              <div className="prof-bar" style={{ left: `${val}%` }} />
                            </div>
                            <div className="score-vals">
                              <span className="score-val-ucf">{UCF_AVG}</span>
                              <span className="score-val-prof">{val}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="prof-tags">
                      {prof.rmpTags.map((tag, i) => (
                        <span key={i} className="tag" style={{ background: TAG_COLORS[tag] || "#555" }}>
                          {tag}
                        </span>
                      ))}
                    </div>

                    <button className="collapse-btn" onClick={() => setExpandedId(null)}>
                      ▲ Collapse
                    </button>
                  </div>
                ) : (
                  <div className="prof-card collapsed" onClick={() => setExpandedId(prof._id)}>
                    <div className="collapsed-left">
                      <div className="collapsed-avatar" />
                      <span className="collapsed-name">{fullName}</span>
                    </div>
                    <span className="collapsed-score">{prof.overallScore}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}