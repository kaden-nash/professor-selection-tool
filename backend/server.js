const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();
const { syncProfessors } = require('./utils/syncData');

const app = express();

// middleware
const corsOptions = {
  origin: process.env.FRONTEND_URL || '*',
  credentials: true,
};
app.use(cors(corsOptions));
app.use(express.json());

app.use("/api/auth", require("./routes/auth"));
app.use("/api/professors", require("./routes/professors"));
app.use("/api/users", require("./routes/users"));
app.use("/api/stats", require("./routes/stats"));


// test route
app.get("/", (req, res) => {
  res.send("API is running...");
});

const PORT = process.env.PORT || 5001;

// connects to mongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.log(err));

// to run the syncData script
mongoose.connection.once('open', async () => {
    await syncProfessors(); 
});

// starts backend server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});



