/**
 * Unit tests for file validation utilities
 */

import {
  isValidFileType,
  getFileExtension,
  isValidFileSize,
  ALLOWED_MIME_TYPES,
  ALLOWED_EXTENSIONS,
  MAX_FILE_SIZE,
} from "../../src/utils/fileValidation.js";
import { describe, it, expect } from "@jest/globals";

describe("File Validation Utilities", () => {
  describe("isValidFileType", () => {
    it("should return true for valid CSV MIME type", () => {
      expect(isValidFileType("text/csv", "test.csv")).toBe(true);
    });

    it("should return true for valid XLSX MIME type", () => {
      expect(
        isValidFileType(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "test.xlsx"
        )
      ).toBe(true);
    });

    it("should return true for valid XLS MIME type", () => {
      expect(isValidFileType("application/vnd.ms-excel", "test.xls")).toBe(
        true
      );
    });

    it("should return true for valid file extension even with wrong MIME type", () => {
      expect(isValidFileType("application/octet-stream", "test.csv")).toBe(
        true
      );
    });

    it("should return false for invalid MIME type and extension", () => {
      expect(isValidFileType("text/plain", "test.txt")).toBe(false);
    });

    it("should return true for valid MIME type even with invalid extension", () => {
      expect(isValidFileType("text/csv", "test.txt")).toBe(true);
    });

    it("should handle uppercase extensions", () => {
      expect(isValidFileType("text/csv", "test.CSV")).toBe(true);
      expect(
        isValidFileType(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "test.XLSX"
        )
      ).toBe(true);
    });

    it("should handle files with no extension", () => {
      expect(isValidFileType("text/csv", "testfile")).toBe(true);
    });

    it("should handle empty strings", () => {
      expect(isValidFileType("", "")).toBe(false);
      expect(isValidFileType("text/csv", "")).toBe(true);
      expect(isValidFileType("", "test.csv")).toBe(true);
    });
  });

  describe("getFileExtension", () => {
    it("should return correct extension for CSV file", () => {
      expect(getFileExtension("test.csv")).toBe(".csv");
    });

    it("should return correct extension for XLSX file", () => {
      expect(getFileExtension("test.xlsx")).toBe(".xlsx");
    });

    it("should return correct extension for XLS file", () => {
      expect(getFileExtension("test.xls")).toBe(".xls");
    });

    it("should handle uppercase extensions", () => {
      expect(getFileExtension("test.CSV")).toBe(".csv");
      expect(getFileExtension("test.XLSX")).toBe(".xlsx");
      expect(getFileExtension("test.XLS")).toBe(".xls");
    });

    it("should handle files with multiple dots", () => {
      expect(getFileExtension("test.backup.csv")).toBe(".csv");
      expect(getFileExtension("my.file.xlsx")).toBe(".xlsx");
    });

    it("should return empty string for files with no extension", () => {
      expect(getFileExtension("testfile")).toBe("");
      expect(getFileExtension("test.")).toBe("");
    });

    it("should handle empty filename", () => {
      expect(getFileExtension("")).toBe("");
    });

    it("should handle filenames starting with dot", () => {
      expect(getFileExtension(".hidden.csv")).toBe(".csv");
    });
  });

  describe("isValidFileSize", () => {
    it("should return true for files under the limit", () => {
      expect(isValidFileSize(1024)).toBe(true); // 1KB
      expect(isValidFileSize(5 * 1024 * 1024)).toBe(true); // 5MB
      expect(isValidFileSize(MAX_FILE_SIZE)).toBe(true); // Exactly at limit
    });

    it("should return false for files over the limit", () => {
      expect(isValidFileSize(MAX_FILE_SIZE + 1)).toBe(false); // 1 byte over
      expect(isValidFileSize(11 * 1024 * 1024)).toBe(false); // 11MB
      expect(isValidFileSize(100 * 1024 * 1024)).toBe(false); // 100MB
    });

    it("should handle zero size files", () => {
      expect(isValidFileSize(0)).toBe(true);
    });

    it("should handle negative sizes", () => {
      expect(isValidFileSize(-1)).toBe(false);
      expect(isValidFileSize(-1000)).toBe(false);
    });
  });

  describe("Constants", () => {
    it("should have correct allowed MIME types", () => {
      expect(ALLOWED_MIME_TYPES).toContain("text/csv");
      expect(ALLOWED_MIME_TYPES).toContain("application/vnd.ms-excel");
      expect(ALLOWED_MIME_TYPES).toContain(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      );
      expect(ALLOWED_MIME_TYPES).toHaveLength(3);
    });

    it("should have correct allowed extensions", () => {
      expect(ALLOWED_EXTENSIONS).toContain(".csv");
      expect(ALLOWED_EXTENSIONS).toContain(".xlsx");
      expect(ALLOWED_EXTENSIONS).toContain(".xls");
      expect(ALLOWED_EXTENSIONS).toHaveLength(3);
    });

    it("should have correct max file size", () => {
      expect(MAX_FILE_SIZE).toBe(10 * 1024 * 1024); // 10MB
    });
  });
});
