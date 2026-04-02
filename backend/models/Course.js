// represents a UCF course
const mongoose = require("mongoose");

const courseSchema = new mongoose.Schema({
  courseCode: { type: String, required: true, unique: true }, // e.g. "COP3502"
  courseName: { type: String, required: true },
  department: { type: String }
}, { timestamps: true });

module.exports = mongoose.model("Course", courseSchema);