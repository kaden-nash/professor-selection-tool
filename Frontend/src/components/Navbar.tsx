import { useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const links = [
    { label: "Leaderboard", path: "/leaderboard" },
    { label: "Search", path: "/search" },
    { label: "Starred", path: "/starred" },
    { label: "Settings", path: "/settings" },
  ];

  return (
    <nav className="app-nav">
      <button className="app-nav-logo" onClick={() => navigate("/search")}>
        KnightRate
      </button>
      <div className="app-nav-links">
        {links.map(link => (
          <button
            key={link.path}
            className={`app-nav-link ${location.pathname === link.path ? "active" : ""}`}
            onClick={() => navigate(link.path)}
          >
            {link.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
