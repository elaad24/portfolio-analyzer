import { Router, Request, Response } from "express";
import multer from "multer";
import {
  createMulterConfig,
  isValidFileType,
  getFileExtension,
  isValidFileSize,
  ALLOWED_EXTENSIONS,
} from "../utils/fileValidation.js";
import fs from "fs";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import {
  UploadedFileInfo,
  FileUploadError,
  FileUploadResponse,
  ErrorResponse,
  isMulterFilesArray,
} from "../types/index.js";

const router = Router();

// Configure multer for file uploads using utility functions
const upload = multer(createMulterConfig());

const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// File upload endpoint - MULTIPLE FILES
router.post(
  "/upload",
  upload.array("files", 10), // Allow up to 10 files
  (req: Request, res: Response) => {
    try {
      // Handle multer files array
      const files = isMulterFilesArray(req.files) ? req.files : [];

      if (files.length === 0) {
        return res.status(400).json({
          error: "No files uploaded",
          message: "Please select at least one file to upload",
          timestamp: new Date().toISOString(),
        });
      }

      const uploadedFiles: UploadedFileInfo[] = [];
      const errors: FileUploadError[] = [];

      // Process each file
      for (const file of files) {
        try {
          // Validate each file
          const fileExtension = getFileExtension(file.originalname);

          if (!isValidFileType(file.mimetype, file.originalname)) {
            errors.push({
              filename: file.originalname,
              error: "Invalid file type. Only CSV and XLSX files are allowed.",
            });
            continue;
          }

          if (!isValidFileSize(file.size)) {
            errors.push({
              filename: file.originalname,
              error: "File too large. Must be less than 10MB.",
            });
            continue;
          }

          // Generate unique filename and save
          const uniqueId = uuidv4();
          const savedFileName = `${uniqueId}-${file.originalname}`;
          const filePath = path.join(uploadDir, savedFileName);

          fs.writeFileSync(filePath, file.buffer);

          uploadedFiles.push({
            originalName: file.originalname,
            savedName: savedFileName,
            size: file.size,
            mimetype: file.mimetype,
            extension: fileExtension,
            path: filePath,
          });
        } catch (fileError) {
          errors.push({
            filename: file.originalname,
            error:
              fileError instanceof Error ? fileError.message : "Unknown error",
          });
        }
      }

      // Return response with results
      res.json({
        message: `Processed ${files.length} files`,
        successCount: uploadedFiles.length,
        errorCount: errors.length,
        uploadedFiles,
        errors: errors.length > 0 ? errors : undefined,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({
        error: "Upload failed",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
        timestamp: new Date().toISOString(),
      });
    }
  }
);

// File download endpoint
router.get("/download/:filename", (req: Request, res: Response) => {
  const { filename } = req.params;
  res.json({
    message: `Download endpoint for file: ${filename}`,
    timestamp: new Date().toISOString(),
  });
});

// List files endpoint
router.get("/list", (req: Request, res: Response) => {
  res.json({
    message: "List files endpoint - coming soon!",
    files: [],
    timestamp: new Date().toISOString(),
  });
});

export default router;
