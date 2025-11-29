/**
 * Message schema for portfolio analyzer job processing
 */

export enum JobStatusEnum {
  PENDING = "pending",
  PROCESSING = "processing",
  DONE = "done",
  ERROR = "error",
}
export type JobStatus = JobStatusEnum;

export enum JobStepEnum {
  FILE_UPLOADED = "file_uploaded",
  PARSING = "parsing",
  PARSING_COMPLETE = "parsing_complete",
  AI_ANALYSIS = "ai_analysis",
  AI_ANALYSIS_COMPLETE = "ai_analysis_complete",
  COMPLETED = "completed",
}

export type JobStep = JobStepEnum;

export interface JobMessage {
  jobId: string;
  directory: string;
  files: Array<string>;
  step: JobStep;
  status: JobStatus;
  timestamp: number;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface StreamMessage {
  id: string;
  message: JobMessage;
}

export interface ConsumerOptions {
  streamKey: string;
  groupName: string;
  consumerName: string;
  blockTime?: number; // milliseconds to block waiting for messages
  count?: number; // max number of messages to read at once
}

export interface ProducerOptions {
  streamKey: string;
  maxLength?: number; // Optional: limit stream length (for memory management)
}
