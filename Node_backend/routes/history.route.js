import express from "express";
import Analysis from "../models/analysis.model.js";

const router = express.Router();

router.get("/", async (req, res) => {
  const data = await Analysis.find().sort({ createdAt: -1 });
  res.json({ analyses: data });
});

router.get("/:id", async (req, res) => {
  const data = await Analysis.findById(req.params.id);
  res.json(data);
});

router.delete("/:id", async (req, res) => {
  await Analysis.findByIdAndDelete(req.params.id);
  res.json({ success: true });
});

export default router;