/**
 * Jest test setup file
 */

// Create a test uploads directory
import fs from "fs";
import path from "path";
import { afterEach, afterAll } from "@jest/globals";

const testUploadsDir = path.join(process.cwd(), "test-uploads");

// Ensure test uploads directory exists
if (!fs.existsSync(testUploadsDir)) {
  fs.mkdirSync(testUploadsDir, { recursive: true });
}

// Clean up test files after each test
afterEach(() => {
  if (fs.existsSync(testUploadsDir)) {
    const files = fs.readdirSync(testUploadsDir);
    files.forEach((file) => {
      fs.unlinkSync(path.join(testUploadsDir, file));
    });
  }
});

// Clean up test directory after all tests
afterAll(() => {
  if (fs.existsSync(testUploadsDir)) {
    fs.rmSync(testUploadsDir, { recursive: true, force: true });
  }
});
