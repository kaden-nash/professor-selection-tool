import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./components/Landing";
import Login from "./components/Login";
import Register from "./components/Register";
import Verify from "./components/Verify";
import Search from "./components/Search";
import SearchResults from "./components/SearchResults";
import Starred from "./components/Starred";
import Settings from "./components/Settings";
import HowItWorks from "./components/HowItWorks";
import ForgotPassword from "./components/ForgotPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/landing" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/search" element={<Search />} />
        <Route path="/search-results" element={<SearchResults />} />
        <Route path="/starred" element={<Starred />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/about" element={<HowItWorks />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
