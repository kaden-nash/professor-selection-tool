// seed file to initially populate db for api testing
const mongoose = require("mongoose");
const dotenv = require("dotenv");
dotenv.config();

const Course = require("./models/Course");
const Professor = require("./models/Professor");

const courses = [
  { courseCode: "COP3502", courseName: "Computer Science I", department: "Computer Science" },
  { courseCode: "COP3503", courseName: "Computer Science II", department: "Computer Science" },
  { courseCode: "MAC2311", courseName: "Calculus I", department: "Mathematics" },
];

const professors = [
  {
    firstName: "John",
    lastName: "Smith",
    title: "Lecturer",
    educationLevel: "PhD",
    linkedinUrl: "https://linkedin.com/in/johnsmith",
    calculatedScores: { composite: 4.5, quality: 4.7, reliability: 4.3, englishSkill: 4.6 },
  },
  {
    firstName: "Jane",
    lastName: "Doe",
    title: "Research Professor",
    educationLevel: "PhD",
    linkedinUrl: "https://linkedin.com/in/janedoe",
    calculatedScores: { composite: 3.8, quality: 3.9, reliability: 4.0, englishSkill: 3.5 },
  },
  {
    firstName: "Bob",
    lastName: "Jones",
    title: "Adjunct",
    educationLevel: "Masters",
    linkedinUrl: "https://linkedin.com/in/bobjones",
    calculatedScores: { composite: 3.2, quality: 3.0, reliability: 3.5, englishSkill: 3.2 },
  },
];

async function seed() {
  await mongoose.connect(process.env.MONGO_URI);
  console.log("MongoDB connected");

  // clear existing data
  await Course.deleteMany({});
  await Professor.deleteMany({});
  console.log("Cleared existing data");

  // insert courses
  const insertedCourses = await Course.insertMany(courses);
  console.log("Courses seeded");

  // assign professors to courses
  professors[0].coursesTaught = [
    { courseId: insertedCourses[0]._id, semestersTaught: 6 }, // John teaches COP3502
    { courseId: insertedCourses[2]._id, semestersTaught: 2 }, // John teaches MAC2311
  ];
  professors[1].coursesTaught = [
    { courseId: insertedCourses[0]._id, semestersTaught: 3 }, // Jane teaches COP3502
    { courseId: insertedCourses[1]._id, semestersTaught: 4 }, // Jane teaches COP3503
  ];
  professors[2].coursesTaught = [
    { courseId: insertedCourses[1]._id, semestersTaught: 1 }, // Bob teaches COP3503
  ];

  await Professor.insertMany(professors);
  console.log("Professors seeded");

  console.log("Seeding complete!");
  process.exit(0);
}

seed().catch(err => {
  console.error(err);
  process.exit(1);
});