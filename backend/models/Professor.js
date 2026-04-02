// represents a professor
const mongoose = require("mongoose");

const professorSchema = new mongoose.Schema({
  firstName: { type: String, required: true },
  lastName:  { type: String, required: true },
  title: {
    type: String,
    enum: ["Lecturer", "Research Professor", "Adjunct"]
  },
  educationLevel: { type: String },
  linkedinUrl:    { type: String },
  calculatedScores: {
    composite:    { type: Number, default: 0 },
    quality:      { type: Number, default: 0 },
    reliability:  { type: Number, default: 0 },
    englishSkill: { type: Number, default: 0 }
  },
  coursesTaught: [
    {
      courseId:        { type: mongoose.Schema.Types.ObjectId, ref: "Course" },
      semestersTaught: { type: Number, default: 0 }
    }
  ]
}, { timestamps: true });

module.exports = mongoose.model("Professor", professorSchema);