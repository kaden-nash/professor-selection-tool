const request = require('supertest');
const mongoose = require('mongoose');
const app = require('./testApp');

describe('Stats Routes', () => {
  describe('GET /api/stats/global', () => {
    it('returns 404 when no stats document exists', async () => {
      const res = await request(app).get('/api/stats/global');
      expect(res.status).toBe(404);
      expect(res.body.msg).toBe('Global stats not found');
    });

    it('returns correct stats fields when document exists', async () => {
      // Route reads: avg_would_take_again, avg_quality, avg_difficulty, avg_overall
      await mongoose.connection.db.collection('rawGlobalStatistics').insertOne({
        avg_would_take_again: 3.7,
        avg_quality: 4.1,
        avg_difficulty: 2.9,
        avg_overall: 3.8,
      });

      const res = await request(app).get('/api/stats/global');
      expect(res.status).toBe(200);
      expect(res.body.retakeAvg).toBe(3.7);
      expect(res.body.qualityAvg).toBe(4.1);
      expect(res.body.difficultyAvg).toBe(2.9);
      expect(res.body.overallAvg).toBe(3.8);
    });
  });
});
