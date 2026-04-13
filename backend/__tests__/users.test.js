const request = require('supertest');
const jwt = require('jsonwebtoken');
const app = require('./testApp');
const User = require('../models/User');
const Professor = require('../models/Professor');

async function createVerifiedUser(email = 'user@example.com') {
  const bcrypt = require('bcryptjs');
  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash('password123', salt);

  const user = await User.create({
    name: 'Test User',
    email,
    password: hashedPassword,
    isVerified: true,
  });

  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
  return { user, token };
}

describe('Users Routes', () => {
  let professor;

  beforeEach(async () => {
    professor = await Professor.create({
      firstName: 'Jane',
      lastName: 'Doe',
      overallScore: 4.2,
      lastTimeTaught: 'Spring 2024',
      courses: ['COP3502'],
    });
  });

  describe('GET /api/users/starred', () => {
    it('returns 401 without auth token', async () => {
      const res = await request(app).get('/api/users/starred');
      expect(res.status).toBe(401);
      expect(res.body.msg).toBe('No token, authorization denied');
    });

    it('returns empty array initially for authenticated user', async () => {
      const { token } = await createVerifiedUser();

      const res = await request(app)
        .get('/api/users/starred')
        .set('Authorization', `Bearer ${token}`);

      expect(res.status).toBe(200);
      expect(res.body).toEqual([]);
    });
  });

  describe('POST /api/users/starred/:professorId', () => {
    it('stars a professor and it appears in GET /starred', async () => {
      const { token } = await createVerifiedUser('star@example.com');

      const starRes = await request(app)
        .post(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      expect(starRes.status).toBe(200);

      const getRes = await request(app)
        .get('/api/users/starred')
        .set('Authorization', `Bearer ${token}`);

      expect(getRes.status).toBe(200);
      expect(getRes.body.length).toBe(1);
      expect(getRes.body[0]._id.toString()).toBe(professor._id.toString());
    });

    it('returns 400 if professor already starred', async () => {
      const { token } = await createVerifiedUser('already@example.com');

      await request(app)
        .post(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      const res = await request(app)
        .post(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('Professor already starred');
    });
  });

  describe('DELETE /api/users/starred/:professorId', () => {
    it('removes a starred professor', async () => {
      const { token } = await createVerifiedUser('delete@example.com');

      await request(app)
        .post(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      const deleteRes = await request(app)
        .delete(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      expect(deleteRes.status).toBe(200);

      const getRes = await request(app)
        .get('/api/users/starred')
        .set('Authorization', `Bearer ${token}`);

      expect(getRes.body).toEqual([]);
    });

    it('is idempotent — deleting non-starred professor still succeeds', async () => {
      const { token } = await createVerifiedUser('idempotent@example.com');

      const res = await request(app)
        .delete(`/api/users/starred/${professor._id}`)
        .set('Authorization', `Bearer ${token}`);

      expect(res.status).toBe(200);
    });
  });
});
