import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./Search.css";

type SearchType = "professor" | "course";
type FilterType = "name" | "course";

export default function Search() {
  const navigate = useNavigate();
  const [searchType, setSearchType] = useState<SearchType>("professor");
  const [filter, setFilter] = useState<FilterType>("name");
  const [query, setQuery] = useState("");

  const isProfessor = searchType === "professor";

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/search-results?type=${searchType}&filter=${filter}&q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="search-page">
      <Navbar />

      <div className="search-body">
        {/* Toggle professor / course */}
        <div className="search-type-toggle">
          <button
            className={`type-btn ${isProfessor ? "active" : ""}`}
            onClick={() => { setSearchType("professor"); setFilter("name"); setQuery(""); }}
          >
            Professors
          </button>
          <button
            className={`type-btn ${!isProfessor ? "active" : ""}`}
            onClick={() => { setSearchType("course"); setFilter("name"); setQuery(""); }}
          >
            Courses
          </button>
        </div>

        <h1 className="search-heading">
          {isProfessor ? "Search for UCF professors" : "Search for UCF courses"}
        </h1>

        {/* Radio filter */}
        <div className="search-filters">
          <label className="radio-label">
            <input
              type="radio"
              value="name"
              checked={filter === "name"}
              onChange={() => setFilter("name")}
            />
            Name
          </label>
          <label className="radio-label">
            <input
              type="radio"
              value="course"
              checked={filter === "course"}
              onChange={() => setFilter("course")}
            />
            Course
          </label>
        </div>

        {/* Search input */}
        <form onSubmit={handleSearch}>
          <input
            className="search-input"
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder={
              filter === "name"
                ? "Enter name here"
                : "Enter course name or code here"
            }
          />
        </form>
      </div>
    </div>
  );
}
