const jwt = require('jsonwebtoken');
const authMiddleware = require('../middleware/auth');

describe('Auth Middleware', () => {
  let res, next;

  beforeEach(() => {
    res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    next = jest.fn();
  });

  it('returns 401 when no Authorization header', () => {
    const req = { headers: {} };
    authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ msg: 'No token, authorization denied' });
    expect(next).not.toHaveBeenCalled();
  });

  it('returns 401 when Authorization header is not Bearer', () => {
    const req = { headers: { authorization: 'Token someinvalidformat' } };
    authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ msg: 'No token, authorization denied' });
    expect(next).not.toHaveBeenCalled();
  });

  it('returns 401 for invalid Bearer token', () => {
    const req = { headers: { authorization: 'Bearer invalidtoken' } };
    authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ msg: 'Token is not valid' });
    expect(next).not.toHaveBeenCalled();
  });

  it('calls next() and sets req.user for valid Bearer token', () => {
    const payload = { id: '507f1f77bcf86cd799439011' };
    const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' });
    const req = { headers: { authorization: `Bearer ${token}` } };

    authMiddleware(req, res, next);

    expect(next).toHaveBeenCalledTimes(1);
    expect(req.user).toBeDefined();
    expect(req.user.id).toBe(payload.id);
    expect(res.status).not.toHaveBeenCalled();
  });
});
