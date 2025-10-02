/**
 * Unit tests for file upload endpoint
 */

import request from "supertest";
import express from "express";
import path from "path";
import fs from "fs";
import fileHandlerRouter from "../../src/routes/file-handler.js";
import {
  createMockCSVBuffer,
  createMockXLSXBuffer,
  createMockTextBuffer,
  createLargeFileBuffer,
  createMockFile,
} from "../helpers/mockFiles.js";

import { describe, it, expect, beforeEach, afterEach } from "@jest/globals";

// Create test app
const app = express();
app.use(express.json());
app.use("/api/files", fileHandlerRouter);

describe("File Upload Endpoint", () => {
  const testUploadsDir = path.join(process.cwd(), "uploads");

  beforeEach(() => {
    // Ensure uploads directory exists
    if (!fs.existsSync(testUploadsDir)) {
      fs.mkdirSync(testUploadsDir, { recursive: true });
    }
  });

  afterEach(() => {
    // Clean up uploaded files after each test
    if (fs.existsSync(testUploadsDir)) {
      const files = fs.readdirSync(testUploadsDir);
      files.forEach((file) => {
        fs.unlinkSync(path.join(testUploadsDir, file));
      });
    }
  });

  describe("POST /api/files/upload", () => {
    describe("Successful uploads", () => {
      it("should upload a single CSV file successfully", async () => {
        const csvBuffer = createMockCSVBuffer();
        const mockFile = createMockFile("test.csv", "text/csv", csvBuffer);

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test.csv",
            contentType: "text/csv",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 1 files",
          successCount: 1,
          errorCount: 0,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "test.csv",
              mimetype: "text/csv",
              extension: ".csv",
              size: csvBuffer.length,
              savedName: expect.any(String),
              path: expect.any(String),
            }),
          ]),
        });
      });

      it("should upload a single XLSX file successfully", async () => {
        const xlsxBuffer = createMockXLSXBuffer();
        const mockFile = createMockFile(
          "test.xlsx",
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          xlsxBuffer
        );

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", xlsxBuffer, {
            filename: "test.xlsx",
            contentType:
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 1 files",
          successCount: 1,
          errorCount: 0,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "test.xlsx",
              mimetype:
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              extension: ".xlsx",
              size: xlsxBuffer.length,
            }),
          ]),
        });
      });

      it("should upload multiple files successfully", async () => {
        const csvBuffer = createMockCSVBuffer();
        const xlsxBuffer = createMockXLSXBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test1.csv",
            contentType: "text/csv",
          })
          .attach("files", xlsxBuffer, {
            filename: "test2.xlsx",
            contentType:
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 2 files",
          successCount: 2,
          errorCount: 0,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "test1.csv",
              extension: ".csv",
            }),
            expect.objectContaining({
              originalName: "test2.xlsx",
              extension: ".xlsx",
            }),
          ]),
        });
      });
    });

    describe("Validation errors", () => {
      it("should reject files with invalid MIME types and extensions", async () => {
        const textBuffer = createMockTextBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", textBuffer, {
            filename: "test.txt",
            contentType: "text/plain",
          })
          .expect(200); // Note: multer doesn't reject, our validation does

        expect(response.body).toMatchObject({
          message: "Processed 1 files",
          successCount: 0,
          errorCount: 1,
          errors: expect.arrayContaining([
            expect.objectContaining({
              filename: "test.txt",
              error: "Invalid file type. Only CSV and XLSX files are allowed.",
            }),
          ]),
        });
      });

      it("should reject files that are too large", async () => {
        const largeBuffer = createLargeFileBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", largeBuffer, {
            filename: "large.csv",
            contentType: "text/csv",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 1 files",
          successCount: 0,
          errorCount: 1,
          errors: expect.arrayContaining([
            expect.objectContaining({
              filename: "large.csv",
              error: "File too large. Must be less than 10MB.",
            }),
          ]),
        });
      });

      it("should handle mixed valid and invalid files", async () => {
        const csvBuffer = createMockCSVBuffer();
        const textBuffer = createMockTextBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "valid.csv",
            contentType: "text/csv",
          })
          .attach("files", textBuffer, {
            filename: "invalid.txt",
            contentType: "text/plain",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 2 files",
          successCount: 1,
          errorCount: 1,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "valid.csv",
              extension: ".csv",
            }),
          ]),
          errors: expect.arrayContaining([
            expect.objectContaining({
              filename: "invalid.txt",
              error: "Invalid file type. Only CSV and XLSX files are allowed.",
            }),
          ]),
        });
      });
    });

    describe("Edge cases", () => {
      it("should return error when no files are uploaded", async () => {
        const response = await request(app)
          .post("/api/files/upload")
          .expect(400);

        expect(response.body).toMatchObject({
          error: "No files uploaded",
          message: "Please select at least one file to upload",
        });
      });

      it("should handle files with uppercase extensions", async () => {
        const csvBuffer = createMockCSVBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test.CSV",
            contentType: "text/csv",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          successCount: 1,
          errorCount: 0,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "test.CSV",
              extension: ".csv", // Should be normalized to lowercase
            }),
          ]),
        });
      });

      it("should accept files with valid MIME type even without extension", async () => {
        const csvBuffer = createMockCSVBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "testfile",
            contentType: "text/csv",
          })
          .expect(200);

        expect(response.body).toMatchObject({
          message: "Processed 1 files",
          successCount: 1,
          errorCount: 0,
          uploadedFiles: expect.arrayContaining([
            expect.objectContaining({
              originalName: "testfile",
              mimetype: "text/csv",
              extension: "",
            }),
          ]),
        });
      });
    });

    describe("File system operations", () => {
      it("should actually save files to disk", async () => {
        const csvBuffer = createMockCSVBuffer();

        const response = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test.csv",
            contentType: "text/csv",
          })
          .expect(200);

        const savedFile = response.body.uploadedFiles[0];
        expect(savedFile).toHaveProperty("path");

        // Check if file actually exists on disk
        expect(fs.existsSync(savedFile.path)).toBe(true);

        // Check if file content matches
        const savedContent = fs.readFileSync(savedFile.path);
        expect(savedContent).toEqual(csvBuffer);
      });

      it("should generate unique filenames for each upload", async () => {
        const csvBuffer = createMockCSVBuffer();

        const response1 = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test.csv",
            contentType: "text/csv",
          })
          .expect(200);

        const response2 = await request(app)
          .post("/api/files/upload")
          .attach("files", csvBuffer, {
            filename: "test.csv",
            contentType: "text/csv",
          })
          .expect(200);

        const savedName1 = response1.body.uploadedFiles[0].savedName;
        const savedName2 = response2.body.uploadedFiles[0].savedName;

        expect(savedName1).not.toBe(savedName2);
        expect(savedName1).toMatch(/^[a-f0-9-]+-test\.csv$/);
        expect(savedName2).toMatch(/^[a-f0-9-]+-test\.csv$/);
      });
    });
  });
});
