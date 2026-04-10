const express = require("express");
const router = express.Router();
const Professor = require("../models/Professor");

router.get("/search", async (req, res) => {
  try {
    const { filter, q } = req.query;

    if (!q || !q.trim()) {
      return res.status(400).json({ msg: "Query is required" });
    }

    const searchTerm = q.trim();

    // course filter logic
    if (filter === "course") {
      const professors = await Professor.find({
        // Added ^ so 'COP' doesn't match 'EEL3123' just because they both have a 'C'
        courses: { $regex: `^${searchTerm}`, $options: "i" }
      }).sort({ overallScore: -1 });

      return res.json(professors);
    }

    // name search logic
    const parts = searchTerm.split(/\s+/); // Splits by any whitespace
    let query = {};

    if (parts.length === 1) {
      // Single word: Match either first OR last name starting with that letter
      query = {
        $or: [
          { firstName: { $regex: `^${parts[0]}`, $options: "i" } },
          { lastName:  { $regex: `^${parts[0]}`, $options: "i" } },
        ]
      };
    } else {
      // Multiple words: Assume First Name starts with part[0] AND Last Name starts with the last part
      query = {
        firstName: { $regex: `^${parts[0]}`, $options: "i" },
        lastName:  { $regex: `^${parts[parts.length - 1]}`, $options: "i" },
      };
    }

    const professors = await Professor.find(query).sort({ overallScore: -1 });
    res.json(professors);

  } catch (err) {
    console.error("SEARCH ERROR:", err.message);
    res.status(500).json({ msg: "Server error" });
  }
});

module.exports = router;