// entry point to backend
// connects to mongoDB, registers all routes, starts server

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();

// middleware
app.use(cors());
app.use(express.json());

app.use("/api/auth", require("./routes/auth"));
app.use("/api/professors", require("./routes/professors"));
app.use("/api/courses",    require("./routes/courses"));
app.use("/api/users",      require("./routes/users"));

// test route
app.get("/", (req, res) => {
  res.send("API is running...");
});

const PORT = process.env.PORT || 5001;

console.log(process.env.MONGO_URI);

// connects to mongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.log(err));

// starts backend server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});



