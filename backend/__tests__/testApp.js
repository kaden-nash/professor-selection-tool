const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/auth', require('../routes/auth'));
app.use('/api/professors', require('../routes/professors'));
app.use('/api/users', require('../routes/users'));
app.use('/api/stats', require('../routes/stats'));

module.exports = app;
