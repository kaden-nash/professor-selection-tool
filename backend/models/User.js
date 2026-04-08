const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  isVerified: { type: Boolean, default: false },
  verificationToken: { type: String },
  verificationTokenExpiry: { type: Date },
  resetToken: { type: String },
  resetTokenExpiry: { type: Date },
  savedProfessors: [{ type: mongoose.Schema.Types.ObjectId, ref: "Professor" }],
  savedCourses: [{ type: mongoose.Schema.Types.ObjectId, ref: "Course" }],
  role: { type: String, enum: ["student", "admin"], default: "student" }
}, { timestamps: true });

module.exports = mongoose.model("User", userSchema);
