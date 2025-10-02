/**
 * Helper functions for creating mock files in tests
 */

import fs from "fs";
import path from "path";

export interface MockFile {
  fieldname: string;
  originalname: string;
  encoding: string;
  mimetype: string;
  buffer: Buffer;
  size: number;
}

/**
 * Creates a mock CSV file buffer
 */
export function createMockCSVBuffer(): Buffer {
  const csvContent = `Name,Age,City
John Doe,30,New York
Jane Smith,25,Los Angeles
Bob Johnson,35,Chicago`;
  return Buffer.from(csvContent, "utf-8");
}

/**
 * Creates a mock XLSX file buffer (simplified)
 */
export function createMockXLSXBuffer(): Buffer {
  // This is a minimal XLSX file structure - in real tests you might want to use a library
  const xlsxContent = "PK\x03\x04\x14\x00\x00\x00\x08\x00"; // Minimal XLSX header
  return Buffer.from(xlsxContent, "binary");
}

/**
 * Creates a mock text file buffer (invalid type)
 */
export function createMockTextBuffer(): Buffer {
  const textContent = "This is a plain text file that should be rejected";
  return Buffer.from(textContent, "utf-8");
}

/**
 * Creates a mock file object for testing
 */
export function createMockFile(
  originalname: string,
  mimetype: string,
  buffer: Buffer,
  fieldname: string = "files"
): MockFile {
  return {
    fieldname,
    originalname,
    encoding: "7bit",
    mimetype,
    buffer,
    size: buffer.length,
  };
}

/**
 * Creates a large file buffer (over 10MB)
 */
export function createLargeFileBuffer(): Buffer {
  const size = 11 * 1024 * 1024; // 11MB
  return Buffer.alloc(size, "A");
}

/**
 * Creates a temporary file for testing
 */
export function createTempFile(filename: string, content: string): string {
  const tempDir = path.join(process.cwd(), "test-uploads");
  const filePath = path.join(tempDir, filename);

  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  fs.writeFileSync(filePath, content);
  return filePath;
}
