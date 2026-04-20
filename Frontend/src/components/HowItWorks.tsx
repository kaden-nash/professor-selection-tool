import Navbar from "./Navbar";
import "./HowItWorks.css";
import unicornImg from "../assets/unicorn.png";
import mastermindImg from "../assets/brain.png";
import saboteurImg from "../assets/bomb.png";
import npcImg from "../assets/bot.png";

const archetypes = [
  {
    name: "The Unicorn",
    img: unicornImg,
    desc: "High quality professor with low difficulty. GPA Savior.",
  },
  {
    name: "The Mastermind",
    img: mastermindImg,
    desc: "Highly knowledgeable and engaging, but expects a lot from students. Challenging but ultimately rewarding.",
  },
  {
    name: "The Saboteur",
    img: saboteurImg,
    desc: "Poor teaching quality paired with high difficulty. Students often feel set up to fail.",
  },
  {
    name: "The NPC",
    img: npcImg,
    desc: "Average in every metric — not particularly good or bad. You get what you put in.",
  },
];

export default function HowItWorks() {
  return (
    <div className="hiw-page">
      <Navbar />
      <div className="hiw-body">
        <h1 className="hiw-heading">How It Works</h1>
        <p className="hiw-sub">Understanding how KnightRate scores and classifies professors.</p>

        {/* Score types */}
        <div className="hiw-scores">
          {[
            { label: "Retake Score", desc: "How likely students are to take this professor again." },
            { label: "Quality Score", desc: "Overall professor quality graded on personality and effectiveness." },
            { label: "Difficulty Score", desc: "Overall professor difficulty graded on personality and effectiveness." },
          ].map(({ label, desc }) => (
            <div key={label} className="hiw-score-row">
              <span className="hiw-score-label">{label}</span>
              <span className="hiw-score-desc">{desc}</span>
            </div>
          ))}
        </div>

        <div className="hiw-divider" />

        {/* Archetypes grid */}
        <div className="hiw-archetypes-grid">
          {archetypes.map(a => (
            <div key={a.name} className="hiw-archetype">
              <div className="archetype-row">
                <div className="hiw-icon">
                  <img src={a.img} alt={a.name} />
                </div>
                <div className="archetype-text">
                  <h2 className="archetype-name">{a.name}</h2>
                  <p className="archetype-desc">{a.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
