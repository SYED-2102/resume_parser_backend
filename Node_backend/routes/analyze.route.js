import express from "express";
import { analyzeResumes } from "../controllers/analyze.controller.js";
import { uploadFields } from "../middleware/multer.js";

const router = express.Router();

router.post("/analyze", uploadFields, analyzeResumes);

export default router;