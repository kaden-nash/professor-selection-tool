const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const path = require("path");
require("dotenv").config();

const app = express();

// middleware
app.use(cors());
app.use(express.json());

app.use("/api/auth", require("./routes/auth"));

// serve react frontend
app.use(express.static(path.join(__dirname, "../Frontend/dist")));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "../Frontend/dist", "index.html"));
});

// test route
app.get("/", (req, res) => {
  res.send("API is running...");
});

const PORT = process.env.PORT || 5001;

// connects to mongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.log(err));

// starts backend server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});



