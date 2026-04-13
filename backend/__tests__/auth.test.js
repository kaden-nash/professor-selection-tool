const request = require('supertest');
const app = require('./testApp');
const User = require('../models/User');
const sendEmail = require('../utils/sendEmail');

describe('Auth Routes', () => {
  describe('POST /api/auth/register', () => {
    it('registers a new user successfully', async () => {
      const res = await request(app)
        .post('/api/auth/register')
        .send({ name: 'Test User', email: 'test@example.com', password: 'password123' });

      expect(res.status).toBe(200);
      expect(res.body.msg).toMatch(/Registration successful/i);
    });

    it('returns 400 for duplicate email', async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Test User', email: 'dup@example.com', password: 'password123' });

      const res = await request(app)
        .post('/api/auth/register')
        .send({ name: 'Test User 2', email: 'dup@example.com', password: 'password456' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('User already exists');
    });

    it('calls sendEmail after registration', async () => {
      sendEmail.mockClear();

      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Email Test', email: 'emailtest@example.com', password: 'password123' });

      expect(sendEmail).toHaveBeenCalledTimes(1);
      expect(sendEmail).toHaveBeenCalledWith(
        expect.objectContaining({ to: 'emailtest@example.com' })
      );
    });

    it('creates user in database with isVerified=false', async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'DB Test', email: 'dbtest@example.com', password: 'password123' });

      const user = await User.findOne({ email: 'dbtest@example.com' });
      expect(user).not.toBeNull();
      expect(user.isVerified).toBe(false);
      expect(user.verificationToken).toBeTruthy();
    });
  });

  describe('GET /api/auth/verify', () => {
    let verificationToken;

    beforeEach(async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Verify User', email: 'verify@example.com', password: 'password123' });

      const user = await User.findOne({ email: 'verify@example.com' });
      verificationToken = user.verificationToken;
    });

    it('verifies a user with valid token', async () => {
      const res = await request(app)
        .get(`/api/auth/verify?token=${verificationToken}`);

      expect(res.status).toBe(200);
      expect(res.body.msg).toMatch(/verified/i);

      const user = await User.findOne({ email: 'verify@example.com' });
      expect(user.isVerified).toBe(true);
    });

    it('returns 400 for invalid token', async () => {
      const res = await request(app)
        .get('/api/auth/verify?token=invalidtoken123');

      expect(res.status).toBe(400);
      expect(res.body.msg).toMatch(/Invalid/i);
    });

    it('returns 400 for expired token', async () => {
      const user = await User.findOne({ email: 'verify@example.com' });
      user.verificationTokenExpiry = new Date(Date.now() - 1000); // expired 1 second ago
      await user.save();

      const res = await request(app)
        .get(`/api/auth/verify?token=${verificationToken}`);

      expect(res.status).toBe(400);
      expect(res.body.msg).toMatch(/expired/i);
    });
  });

  describe('POST /api/auth/login', () => {
    beforeEach(async () => {
      // Create a verified user for login tests
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Login User', email: 'login@example.com', password: 'password123' });

      const user = await User.findOne({ email: 'login@example.com' });
      user.isVerified = true;
      await user.save();
    });

    it('returns JWT token on successful login', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'login@example.com', password: 'password123' });

      expect(res.status).toBe(200);
      expect(res.body.token).toBeTruthy();
    });

    it('blocks unverified user from logging in', async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Unverified', email: 'unverified@example.com', password: 'password123' });

      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'unverified@example.com', password: 'password123' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toMatch(/verify/i);
    });

    it('returns 400 for wrong password', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'login@example.com', password: 'wrongpassword' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('Invalid credentials');
    });

    it('returns 400 for nonexistent user', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'nobody@example.com', password: 'password123' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toBe('Invalid credentials');
    });
  });

  describe('POST /api/auth/forgot-password', () => {
    beforeEach(async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'FP User', email: 'fpuser@example.com', password: 'password123' });
    });

    it('returns success for known email', async () => {
      sendEmail.mockClear();

      const res = await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'fpuser@example.com' });

      expect(res.status).toBe(200);
      expect(res.body.msg).toBe('If that email exists, a reset link has been sent.');
      expect(sendEmail).toHaveBeenCalledTimes(1);
    });

    it('returns same success message for unknown email (no enumeration)', async () => {
      sendEmail.mockClear();

      const res = await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'unknown@example.com' });

      expect(res.status).toBe(200);
      expect(res.body.msg).toBe('If that email exists, a reset link has been sent.');
      expect(sendEmail).not.toHaveBeenCalled();
    });
  });

  describe('POST /api/auth/reset-password', () => {
    let resetToken;

    beforeEach(async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ name: 'Reset User', email: 'reset@example.com', password: 'oldpassword' });

      await request(app)
        .post('/api/auth/forgot-password')
        .send({ email: 'reset@example.com' });

      const user = await User.findOne({ email: 'reset@example.com' });
      resetToken = user.resetToken;
    });

    it('resets password with valid token', async () => {
      const res = await request(app)
        .post('/api/auth/reset-password')
        .send({ token: resetToken, password: 'newpassword123' });

      expect(res.status).toBe(200);
      expect(res.body.msg).toMatch(/reset/i);
    });

    it('returns 400 for invalid token', async () => {
      const res = await request(app)
        .post('/api/auth/reset-password')
        .send({ token: 'invalidtoken', password: 'newpassword123' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toMatch(/Invalid/i);
    });

    it('returns 400 for expired token', async () => {
      const user = await User.findOne({ email: 'reset@example.com' });
      user.resetTokenExpiry = new Date(Date.now() - 1000);
      await user.save();

      const res = await request(app)
        .post('/api/auth/reset-password')
        .send({ token: resetToken, password: 'newpassword123' });

      expect(res.status).toBe(400);
      expect(res.body.msg).toMatch(/Invalid/i);
    });
  });

  describe('Full flow: register → verify → login', () => {
    it('completes the full auth flow end-to-end', async () => {
      // 1. Register
      const registerRes = await request(app)
        .post('/api/auth/register')
        .send({ name: 'Full Flow', email: 'fullflow@example.com', password: 'password123' });

      expect(registerRes.status).toBe(200);

      // 2. Get the verification token
      const user = await User.findOne({ email: 'fullflow@example.com' });
      const token = user.verificationToken;

      // 3. Verify email
      const verifyRes = await request(app)
        .get(`/api/auth/verify?token=${token}`);

      expect(verifyRes.status).toBe(200);

      // 4. Login
      const loginRes = await request(app)
        .post('/api/auth/login')
        .send({ email: 'fullflow@example.com', password: 'password123' });

      expect(loginRes.status).toBe(200);
      expect(loginRes.body.token).toBeTruthy();
    });
  });
});
