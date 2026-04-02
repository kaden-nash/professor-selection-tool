// represents a registered user
const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name:     { type: String, required: true },
  email:    { type: String, required: true, unique: true },
  password: { type: String, required: true },
  savedProfessors: [{ type: mongoose.Schema.Types.ObjectId, ref: "Professor" }],
  savedCourses:    [{ type: mongoose.Schema.Types.ObjectId, ref: "Course" }]
}, { timestamps: true });

module.exports = mongoose.model("User", userSchema);