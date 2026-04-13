const mongoose = require('mongoose');

jest.mock('../utils/sendEmail', () => jest.fn().mockResolvedValue(true));

beforeAll(async () => {
  await mongoose.connect(process.env.MONGO_URI);
});

afterEach(async () => {
  const collections = mongoose.connection.collections;
  for (const key in collections) {
    await collections[key].deleteMany({});
  }
});

afterAll(async () => {
  await mongoose.disconnect();
});
