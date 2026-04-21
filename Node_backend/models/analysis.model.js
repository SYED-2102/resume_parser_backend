import mongoose from "mongoose";

const candidateSchema = new mongoose.Schema({
  filename: String,
  status: String,
  dossier: Object,
  analytics: Object,
  premium_insights: Object,
});

const analysisSchema = new mongoose.Schema({
  batch_info: Object,
  gpa_cutoff_applied: Number,
  ranked_candidates: [candidateSchema],
  rejected_candidates: [Object],
  errors_logs: [Object],
}, { timestamps: true });

export default mongoose.model("Analysis", analysisSchema);