const request = require('supertest');
const app = require('./testApp');
const Professor = require('../models/Professor');

describe('Professors Routes', () => {
  beforeEach(async () => {
    await Professor.create([
      {
        firstName: 'Alice',
        lastName: 'Smith',
        overallScore: 4.5,
        lastTimeTaught: 'Spring 2024',
        courses: ['COP3502', 'COP3330'],
      },
      {
        firstName: 'Bob',
        lastName: 'Johnson',
        overallScore: 3.8,
        lastTimeTaught: 'Fall 2023',
        courses: ['MAD2104', 'COP3502'],
      },
      {
        firstName: 'Carol',
        lastName: 'Williams',
        overallScore: 4.9,
        lastTimeTaught: 'Spring 2024',
        courses: ['ECOP3443', 'STA2023'],
      },
      {
        firstName: 'David',
        lastName: 'Smith',
        overallScore: 2.1,
        lastTimeTaught: 'Fall 2022',
        courses: ['COP4600'],
      },
    ]);
  });

  describe('GET /api/professors/search', () => {
    it('returns 400 when q is missing', async () => {
      const res = await request(app).get('/api/professors/search?filter=name');
      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('Query is required');
    });

    it('returns 400 when q is empty string', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=');
      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('Query is required');
    });

    it('name search single word matches by first name', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=Alice');
      expect(res.status).toBe(200);
      expect(res.body.length).toBe(1);
      expect(res.body[0].firstName).toBe('Alice');
    });

    it('name search single word matches by last name', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=Smith');
      expect(res.status).toBe(200);
      expect(res.body.length).toBe(2);
      const lastNames = res.body.map((p) => p.lastName);
      expect(lastNames.every((n) => n === 'Smith')).toBe(true);
    });

    it('name search multi-word matches first + last name', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=Alice%20Smith');
      expect(res.status).toBe(200);
      expect(res.body.length).toBe(1);
      expect(res.body[0].firstName).toBe('Alice');
      expect(res.body[0].lastName).toBe('Smith');
    });

    it('course search matches courses with ^ regex', async () => {
      const res = await request(app).get('/api/professors/search?filter=course&q=COP');
      expect(res.status).toBe(200);
      // Alice (COP3502, COP3330), Bob (COP3502), David (COP4600) — all start with COP
      expect(res.body.length).toBeGreaterThanOrEqual(3);
      // Carol has ECOP3443, should NOT be in results (ECOP does not start with COP)
      const names = res.body.map((p) => p.firstName);
      expect(names).not.toContain('Carol');
    });

    it('COP does NOT match ECOP3443 (regex anchoring)', async () => {
      const res = await request(app).get('/api/professors/search?filter=course&q=COP');
      expect(res.status).toBe(200);
      const names = res.body.map((p) => p.firstName);
      expect(names).not.toContain('Carol');
    });

    it('returns empty array when no results found', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=Zzzznotexists');
      expect(res.status).toBe(200);
      expect(res.body).toEqual([]);
    });

    it('results are sorted by overallScore descending', async () => {
      const res = await request(app).get('/api/professors/search?filter=name&q=Smith');
      expect(res.status).toBe(200);
      expect(res.body.length).toBe(2);
      expect(res.body[0].overallScore).toBeGreaterThanOrEqual(res.body[1].overallScore);
    });

    it('course search for exact course code prefix', async () => {
      const res = await request(app).get('/api/professors/search?filter=course&q=MAD');
      expect(res.status).toBe(200);
      expect(res.body.length).toBe(1);
      expect(res.body[0].firstName).toBe('Bob');
    });
  });
});
