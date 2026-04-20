import "dotenv/config";
import express from "express";
import cors from "cors";
import analyzeRoutes from "./routes/analyze.route.js";
import { connectDB } from "./config/db.js";


const app = express();

app.use(cors());

// Routes
app.use("/api/proxy", analyzeRoutes);

// Start server
const PORT = 3000;
app.get("/",function(req,res){
    res.json({message:"node server is working" })
})
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  connectDB();
});
























// import express from "express";
// import multer from "multer";
// import axios from "axios";
// import FormData from "form-data";
// import cors from "cors";

// const app = express();
// app.use(cors());

// // Use memory storage (no disk writes)
// const storage = multer.memoryStorage();

// const upload = multer({storage:storage});

// // const uploadField=[{name:'jd_pdf',maxCount:1},{name:"resumes",maxCount:10}]

// // Route: Upload JD + Resumes
// app.post(
//   "/api/proxy/analyze",
//   upload.fields([
//     { name: "jd_pdf", maxCount: 1 },
//     { name: "resumes", maxCount: 10 },
//   ]),
//   async (req, res) => {
//     try {
//       // Validate JD
//       if (!req.files?.jd || req.files.jd.length === 0) {
//         return res.status(400).json({ error: "JD file is required" });
//       }

//       const jdFile = req.files.jd[0];
//       const resumeFiles = req.files.resumes || [];

//       // Validate file types
//       if (jdFile.mimetype !== "application/pdf") {
//         return res.status(400).json({ error: "JD must be a PDF" });
//       }

//       if (resumeFiles.length > 10) {
//         return res
//           .status(400)
//           .json({ error: "Maximum 10 resumes allowed" });
//       }

//       // Create FormData for FastAPI
//       const formData = new FormData();

//       // Append JD
//       formData.append("jd_pdf", jdFile.buffer, {
//         filename: jdFile.originalname,
//         contentType: jdFile.mimetype,
//       });

//       // Append resumes
//       for (const file of resumeFiles) {
//         if (file.mimetype !== "application/pdf") {
//           return res
//             .status(400)
//             .json({ error: "All resumes must be PDFs" });
//         }

//         formData.append("resumes", file.buffer, {
//           filename: file.originalname,
//           contentType: file.mimetype,
//         });
//       }

//       // Send to FastAPI
//       const python_response = await axios.post(
//         "http://127.0.0.1:8000/analyze-bulk",
//         formData,
//         {
//           headers: formData.getHeaders(),
//         //   maxContentLength: Infinity,
//         //   maxBodyLength: Infinity,
//         //   timeout: 60000,
//         }
//       );

//       // Return response to frontend
//       return res.json(python_response.data);
//     } catch (error) {
//       console.error("Error:", error.message);

//       if (error.response) {
//         return res
//           .status(error.response.status)
//           .json(error.response.data);
//       }

//       return res.status(500).json({
//         error: "Internal server error",
//       });
//     }
//   }
// );

// // Start server
// const PORT = 3000;
// app.listen(PORT, () => {
//   console.log(`Server running on http://localhost:${PORT}`);
// });