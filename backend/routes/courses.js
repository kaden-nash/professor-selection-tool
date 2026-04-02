// handles searching by course code or name
// then returns top professors

const express = require("express");
const router = express.Router();
const Course = require("../models/Course");
const Professor = require("../models/Professor");

// GET /api/courses/search?q=COP3502  or  ?q=Intro to Programming
router.get("/search", async (req, res) => {
  try {
    const { q } = req.query;

    if (!q) {
      return res.status(400).json({ msg: "q query parameter is required" });
    }

    // search by course code OR course name
    const courses = await Course.find({
      $or: [
        { courseCode: { $regex: q, $options: "i" } },
        { courseName: { $regex: q, $options: "i" } }
      ]
    });

    if (courses.length === 0) {
      return res.status(404).json({ msg: "No courses found" });
    }

    // for each course, find top professors sorted by composite score
    const results = await Promise.all(
      courses.map(async (course) => {
        const professors = await Professor.find({
          "coursesTaught.courseId": course._id
        })
          .sort({ "calculatedScores.composite": -1 })
          .select("firstName lastName title calculatedScores linkedinUrl");

        return {
          course,
          topProfessors: professors
        };
      })
    );

    res.json(results);

  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

module.exports = router;