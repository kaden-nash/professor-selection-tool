// handles everything related to logged in user
// (saved profs and courses)
// JWT required for all routes here

const express = require("express");
const router = express.Router();
const User = require("../models/User");
const jwt = require("jsonwebtoken");

// middleware to verify JWT token
function authMiddleware(req, res, next) {
  const token = req.header("Authorization")?.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ msg: "No token, authorization denied" });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ msg: "Token is not valid" });
  }
}

// GET /api/users/me/saved  —  get saved professors and courses
router.get("/me/saved", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user.id)
      .populate("savedProfessors", "firstName lastName title calculatedScores linkedinUrl")
      .populate("savedCourses", "courseCode courseName department");

    if (!user) {
      return res.status(404).json({ msg: "User not found" });
    }

    res.json({
      savedProfessors: user.savedProfessors,
      savedCourses:    user.savedCourses
    });

  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// PATCH /api/users/me/saved  —  toggle save/unsave a professor or course
router.patch("/me/saved", authMiddleware, async (req, res) => {
  try {
    const { type, id } = req.body; // type: "professor" or "course"

    if (!type || !id) {
      return res.status(400).json({ msg: "type and id are required" });
    }

    const user = await User.findById(req.user.id);

    if (type === "professor") {
      const alreadySaved = user.savedProfessors.some(
        (savedId) => savedId.toString() === id
      );
      if (!alreadySaved) {
        user.savedProfessors.push(id);  // save
      } else {
        user.savedProfessors = user.savedProfessors.filter(
          (savedId) => savedId.toString() !== id
        );  // unsave
      }
    } else if (type === "course") {
      const alreadySaved = user.savedCourses.some(
        (savedId) => savedId.toString() === id
      );
      if (!alreadySaved) {
        user.savedCourses.push(id);  // save
      } else {
        user.savedCourses = user.savedCourses.filter(
          (savedId) => savedId.toString() !== id
        );  // unsave
      }
    } else {
      return res.status(400).json({ msg: 'type must be "professor" or "course"' });
    }

    await user.save();
    res.json({
      savedProfessors: user.savedProfessors,
      savedCourses:    user.savedCourses
    });

  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

module.exports = router;