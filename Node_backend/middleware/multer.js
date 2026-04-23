import multer from "multer";

// Memory storage
const storage = multer.memoryStorage();

export const upload = multer({storage:
  storage,

});

// Field config (reusable)
export const uploadFields = upload.fields([
  { name: "jd_pdf", maxCount: 1 },
  { name: "resumes", maxCount: 10 },
  
]);