import Navbar from "./Navbar";
import "./HowItWorks.css";

const archetypes = [
  {
    name: "The Unicorn",
    desc: "The rarest professor — high scores across the board, easy grader, and beloved by students. GPA savior, top tier teaching, zero stress.",
  },
  {
    name: "The Mastermind",
    desc: "Highly knowledgeable and engaging, but expects a lot from students. Challenging but ultimately rewarding.",
  },
  {
    name: "The Sabetuer",
    desc: "Poor teaching quality paired with harsh grading. Students often feel set up to fail. Proceed with caution.",
  },
  {
    name: "The NPC",
    desc: "Average in every metric — not particularly good or bad. You get what you put in.",
  },
];

const UnicornIcon = () => (
  <div className="hiw-icon">
    <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40">
      <path d="M32 10 C22 10 14 18 14 30 C14 42 22 50 32 50 C42 50 50 42 50 30 C50 18 42 10 32 10Z" stroke="black" strokeWidth="2" fill="none"/>
      <path d="M32 10 L36 4" stroke="black" strokeWidth="2"/>
      <path d="M28 16 C26 12 30 8 34 10" stroke="black" strokeWidth="1.5" fill="none"/>
    </svg>
  </div>
);

export default function HowItWorks() {
  return (
    <div className="hiw-page">
      <Navbar />
      <div className="hiw-body">
        <h1 className="hiw-heading">How It Works</h1>
        <p className="hiw-sub">Understanding how KnightRate scores and classifies your professors.</p>

        {/* Score types */}
        <div className="hiw-scores">
          {[
            { label: "Retake Score:", desc: "How likely students are to take this professor again based on RMP and survey data." },
            { label: "Quality Score:", desc: "Overall teaching quality derived from RateMyProfessor ratings and SPI survey responses." },
            { label: "Difficulty Score:", desc: "How demanding the professor's coursework is relative to the UCF average." },
          ].map(({ label, desc }) => (
            <div key={label} className="hiw-score-row">
              <span className="hiw-score-label">{label}</span>
              <span className="hiw-score-desc">{desc}</span>
            </div>
          ))}
        </div>

        <div className="hiw-divider" />

        {/* Archetypes */}
        {archetypes.map(a => (
          <div key={a.name} className="hiw-archetype">
            <h2 className="archetype-name">{a.name}</h2>
            <div className="archetype-row">
              <UnicornIcon />
              <p className="archetype-desc">{a.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
