// handles searching prof by name; fetches a 
// single prof's full details by id

const express = require("express");
const router = express.Router();
const Professor = require("../models/Professor");
const Course = require("../models/Course");

// GET /api/professors/search?name=Smith
router.get("/search", async (req, res) => {
  try {
    const { name } = req.query;

    if (!name) {
      return res.status(400).json({ msg: "name query parameter is required" });
    }

    const professors = await Professor.find({
      $or: [
        { firstName: { $regex: name, $options: "i" } },
        { lastName:  { $regex: name, $options: "i" } }
      ]
    })
      .populate("coursesTaught.courseId", "courseCode courseName")
      .sort({ "calculatedScores.composite": -1 });

    if (professors.length === 0) {
      return res.status(404).json({ msg: "No professors found" });
    }

    res.json(professors);

  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// GET /api/professors/:id
router.get("/:id", async (req, res) => {
  try {
    const professor = await Professor.findById(req.params.id)
      .populate("coursesTaught.courseId", "courseCode courseName");

    if (!professor) {
      return res.status(404).json({ msg: "Professor not found" });
    }

    res.json(professor);

  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

module.exports = router;