import { Router, Request, Response } from "express";

const router = Router();

// Basic route
router.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Hello from Bun + Express + TypeScript!",
    timestamp: new Date().toISOString(),
  });
});

// Health check route
router.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "OK",
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

export default router;
