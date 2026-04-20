import axios from "axios";
import FormData from "form-data";
import Analysis from "../models/analysis.model.js";

export const analyzeResumes = async (req, res) => {
  try {
    console.log("🔥 Request reached controller");
    // ❗ FIX: field name must match "jd_pdf"
    if (!req.files?.jd_pdf || req.files.jd_pdf.length === 0) {
      return res.status(400).json({ error: "JD file is required" });
    }

    const jdFile = req.files.jd_pdf[0];
    const resumeFiles = req.files.resumes || [];

    console.log("📦 JD file:", req.files?.jd_pdf?.length);
    console.log("📦 Resume files:", req.files?.resumes?.length);

    // Validate JD
    if (jdFile.mimetype !== "application/pdf") {
      return res.status(400).json({ error: "JD must be a PDF" });
    }

    if (resumeFiles.length > 10) {
      return res.status(400).json({
        error: "Maximum 10 resumes allowed",
      });
    }

    // Build FormData
    const formData = new FormData();

    formData.append("jd_pdf", jdFile.buffer, {
      filename: jdFile.originalname,
      contentType: jdFile.mimetype,
    });

    for (const file of resumeFiles) {
      if (file.mimetype !== "application/pdf") {
        return res.status(400).json({
          error: "All resumes must be PDFs",
        });
      }

      formData.append("resumes", file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });
    }

    console.log("📤 Sending to Python...");
    // Call FastAPI
    const response = await axios.post(
      "http://127.0.0.1:8000/analyze-bulk",
      formData,
      {
        headers: formData.getHeaders(),
        // maxContentLength: Infinity,
        // maxBodyLength: Infinity,
        // timeout: 60000,
      },
    );
    console.log("📥 Python response received");
    console.log("📊 Response keys:", Object.keys(response.data));
    console.log("📥 Response from Python received");
    console.log("📤 Sending response back to frontend");

    const saved = await Analysis.create(response.data);

    console.log("💾 Saved to MongoDB:", saved._id);

    return res.json(response.data);
  } catch (error) {
    console.error("Controller Error:", error.message);

    if (error.response) {
      return res.status(error.response.status).json(error.response.data);
    }

    return res.status(500).json({
      error: "Internal server error",
    });
  }
};
