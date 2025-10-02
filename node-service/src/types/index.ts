/**
 * Type definitions for the portfolio analyzer application
 */

import { Request } from "express";

// File upload related types
export interface UploadedFileInfo {
  originalName: string;
  savedName: string;
  size: number;
  mimetype: string;
  extension: string;
  path: string;
}

export interface FileUploadError {
  filename: string;
  error: string;
}

// Request types extending Express Request
export interface MulterRequest extends Request {
  files?:
    | Express.Multer.File[]
    | { [fieldname: string]: Express.Multer.File[] };
}

// Type guard for multer files
export function isMulterFilesArray(files: any): files is Express.Multer.File[] {
  return Array.isArray(files);
}

// API Response types
export interface FileUploadResponse {
  message: string;
  successCount: number;
  errorCount: number;
  uploadedFiles: UploadedFileInfo[];
  errors?: FileUploadError[];
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  timestamp: string;
}
