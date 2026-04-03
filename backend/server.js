const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();

// middleware
app.use(cors());
app.use(express.json());

app.use("/api/auth", require("./routes/auth"));

// test routes
app.get("/", (req, res) => {
  res.send("API is running...");
});

app.get("/ping", (req, res) => {
  res.send("pong");
});

const PORT = process.env.PORT || 5001;

// connects to mongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.log(err));

// starts backend server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});