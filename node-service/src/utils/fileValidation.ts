/**
 * File validation utilities for handling CSV and Excel file uploads
 */

import multer from "multer";

// Allowed file types for portfolio analysis
export const ALLOWED_MIME_TYPES = [
  "text/csv",
  "application/vnd.ms-excel", // .xls
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
] as const;

export const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"] as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

/**
 * Validates if a file type is allowed for upload
 * @param mimetype - The MIME type of the file
 * @param filename - The original filename
 * @returns true if the file type is allowed, false otherwise
 */
export function isValidFileType(mimetype: string, filename: string): boolean {
  // Check MIME type
  const hasValidMimeType = ALLOWED_MIME_TYPES.includes(mimetype as any);

  // Check file extension
  const fileExtension = getFileExtension(filename);
  const hasValidExtension = ALLOWED_EXTENSIONS.includes(fileExtension as any);

  // File is valid if EITHER MIME type OR extension is valid
  return hasValidMimeType || hasValidExtension;
}

/**
 * Gets the file extension from a filename
 * @param filename - The original filename
 * @returns The file extension in lowercase
 */
export function getFileExtension(filename: string): string {
  const lastDotIndex = filename.lastIndexOf(".");
  if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
    return ""; // No extension or filename ends with dot
  }
  return filename.toLowerCase().substring(lastDotIndex);
}

/**
 * Validates file size
 * @param size - File size in bytes
 * @returns true if file size is within limits, false otherwise
 */
export function isValidFileSize(size: number): boolean {
  return size >= 0 && size <= MAX_FILE_SIZE;
}

/**
 * Creates a multer file filter function for CSV and Excel files
 * @returns A multer file filter callback function
 */
export function createFileFilter() {
  return (req: any, file: Express.Multer.File, cb: any) => {
    // Always accept files and let our validation logic handle rejection
    // This prevents multer from throwing 500 errors
    cb(null, true);
  };
}

/**
 * Creates multer configuration for file uploads
 * @returns Multer configuration object
 */
export function createMulterConfig() {
  return {
    storage: multer.memoryStorage(), // Store files in memory for processing
    fileFilter: createFileFilter(),
    limits: {
      fileSize: MAX_FILE_SIZE * 2, // Allow larger files through so our validation can handle them
    },
  };
}
