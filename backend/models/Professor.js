// represents a professor
const mongoose = require("mongoose");

const professorSchema = new mongoose.Schema({
  firstName: { type: String, required: true },
  lastName:  { type: String, required: true },
  department: { type: String, required: true },
  numRatings: { type: Number, default: 0 },
  avgDifficulty: { type: Number, default: 0 },
  avgRating: { type: Number, default: 0 },
  wouldTakeAgainPercent: { type: Number, default: 0 },
  allReviewsScraped: { type: Boolean, default: false },
  reviews: [
	{
		attendanceMandatory: { type: Boolean, default: null },
		clarityRating: { type: Number, default: 0 },
		class: { type: String, default: "unknown" },
		comment: { type: String, default: "No Comments" },
		date: { type: Date, default: null},
		difficultyRating: { type: Number, default: 0 },
		grade: { type: String, enum: ["A", "B", "C", "D", "E", "F", "S", "U"] },
		helpfulRating: { type: Number, default: 0 },
		isForCredit: { type: Boolean, default: null },
		isForOnlineClass: { type: Boolean, default: null },
		ratingTags: [{ type: String }],
		teacherNote: { type: Boolean, default: null },
		textbookUse: { type: Number, default: 0 },
		thumbs: [],
		thumbsDownTotal: { type: Number, default: 0 },
		thumbsUpTotal: { type: Number, default: 0 },
		wouldTakeAgain: { type: Boolean, default: null }
	}
  ],
  role: {
    type: String,
    enum: ["Lecturer", "Research Professor", "Associate Lecturer", "Adjunct"]
  },
  fieldOfStudy: { type: String },
  dateJoinedUcf: { type: Date, default: null },
  levelOfEducation: { type: String, default: "unknown" },
  graduatedFrom: { type: String, default: "unknown" },
  isEmeritus: {type: Boolean, default: false },
  courses_taught: [{ type: mongoose.Schema.Types.ObjectId, ref: "Course" }],
  scores: {
    difficultyScore: { type: Number, default: 0 },
	qualityScore: { type: Number, default: 0 },
	wouldTakeAgainPercent: { type: Number, default: 0 },
	archetype: { type: String, enum: ["The Unicorn", "The Mastermind", "The NPC", "The Saboteur"] }
  }
}, { timestamps: true });

module.exports = mongoose.model("Professor", professorSchema);