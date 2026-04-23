const mongoose = require("mongoose");
const Professor = require("../models/Professor");

/**
 * Maps and syncs raw scraped data into the clean Professor collection.
 */
const syncProfessors = async () => {
  try {
    // 1. Reference the raw collection your teammate imported
    const rawCollection = mongoose.connection.db.collection("rawProfessorData");
    const rawData = await rawCollection.find().toArray();

    if (!rawData.length) {
      console.log("⚠️ No raw data found. Make sure the 'raw_professors' collection is populated.");
      return;
    }

    const validIds = rawData.map((raw) => raw.id);
    console.log(`Processing ${rawData.length} professors...`);

    // 2. Map the raw JSON fields to clean Schema keys
    const ops = rawData.map((raw) => {
      const transformed = {
        pid:             raw.id,
        firstName:       raw.firstName,
        lastName:        raw.lastName,
        isPolarizing:    raw.scores?.isPolarizing ?? false,
        lastTimeTaught:  raw.scores?.timeLastTaught || "Unknown",
        difficultyScore: raw.scores?.difficulty || 0,
        qualityScore:    raw.scores?.quality || 0,
        retakeScore:     raw.scores?.wouldTakeAgainScore || 0,
        overallScore:    raw.scores?.overall || 0,
        rmpTags:         raw.scores?.topThreeTags || [],
        courses:         raw.courses_taught || [],
        archetype:       raw.scores?.archetype 
      };

      // 3. "bulkWrite" operation
      // This looks for a professor by name; if found, it updates; if not, it inserts (upsert)
      return {
        updateOne: {
          filter: { pid: transformed.pid },
          update: { $set: transformed },
          upsert: true,
        },
      };
    });

    // 4. Execute all operations in one database trip
    const result = await Professor.bulkWrite(ops);
    const purgeResult = await Professor.deleteMany({ pid: { $nin: validIds } });

    console.log("-----------------------------------------");
    console.log(`SYNC COMPLETE`);
    console.log(`📊 Matched:  ${result.matchedCount}`);
    console.log(`✨ New/Upserted: ${result.upsertedCount}`);
    console.log(`💀 Purged: ${purgeResult.deletedCount}`);
    console.log("-----------------------------------------");

  } catch (err) {
    console.error("Sync Error:", err);
  }
};

module.exports = { syncProfessors };