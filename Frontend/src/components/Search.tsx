import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./Search.css";

type SearchType = "professor" | "course";
// Keep FilterType flexible for future expansion
type FilterType = "name" | "course";

export default function Search() {
  const navigate = useNavigate();
  const [searchType, setSearchType] = useState<SearchType>("professor");
  const [filter, setFilter] = useState<FilterType>("name");
  const [query, setQuery] = useState("");

  const isProfessor = searchType === "professor";

  const handleTypeChange = (type: SearchType) => {
    setSearchType(type);
    setFilter("name"); // Reset filter to default when switching categories
    setQuery("");      // Clear search to prevent irrelevant results
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/search-results?type=${searchType}&filter=${filter}&q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="search-page">
      <Navbar />

      <div className="search-body">
        <h1 className="search-heading">
          {isProfessor ? "Search for UCF professors" : "Search for UCF courses"}
        </h1>

        {/* Radio filters now controlling the Search Type */}
        <div className="search-filters">
          <label className="radio-label">
            <input
              type="radio"
              name="searchType"
              checked={searchType === "professor"}
              onChange={() => handleTypeChange("professor")}
            />
            Professors
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="searchType"
              checked={searchType === "course"}
              onChange={() => handleTypeChange("course")}
            />
            Courses
          </label>
        </div>

        {/* Search input */}
        <form onSubmit={handleSearch}>
          <input
            className="search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              isProfessor
                ? "Enter professor name..."
                : "Enter course name or code..."
            }
          />
        </form>
      </div>
    </div>
  );
}