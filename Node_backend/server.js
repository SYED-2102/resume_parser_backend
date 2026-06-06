import "dotenv/config";
import express from "express";
import cors from "cors";
import analyzeRoutes from "./routes/analyze.route.js";
import { connectDB } from "./config/db.js";

import historyRoutes from "./routes/history.route.js";


const app = express();

app.use(cors());

// Routes
app.use("/api/proxy", analyzeRoutes);
app.use("/api/history", historyRoutes);

// Start server
const PORT = 3000;
app.get("/",function(req,res){
    res.json({message:"node server is working" })
})
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  connectDB();
});