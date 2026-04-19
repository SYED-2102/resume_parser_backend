import multer from "multer";

// Memory storage
const storage = multer.memoryStorage();

export const upload = multer({storage:
  storage,
//   limits: {
//     fileSize: 10 * 1024 * 1024, // 10MB
//   },
});

// Field config (reusable)
export const uploadFields = upload.fields([
  { name: "jd_pdf", maxCount: 1 },
  { name: "resumes", maxCount: 10 },
  
]);