const mongoose = require("mongoose");

const professorSchema = new mongoose.Schema({
  pid:             { type: String, required: true},
  firstName:       { type: String, required: true },
  lastName:        { type: String, required: true },
  isPolarizing:    { type: Boolean, default: false },
  lastTimeTaught:  { type: String, required: true },
  difficultyScore: { type: Number, default: 0 },
  qualityScore:    { type: Number, default: 0 },
  retakeScore:     { type: Number, default: 0 },
  overallScore:    { type: Number, default: 0 },
  rmpTags:         { type: [String], default: [] },
  courses:         { type: [String], default: [] }, // e.g. ["COP4331", "COP3502"]
  archetype: {
    type: String,
    enum: ["The Unicorn", "The Mastermind", "The NPC", "The Saboteur"]
  },
}, { timestamps: true });

// Index for fast course lookups
professorSchema.index({ courses: 1 });
professorSchema.index({ overallScore: -1 });

module.exports = mongoose.model("Professor", professorSchema);
