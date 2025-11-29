/**
 * Redis Streams Producer
 *
 * Publishes job messages to Redis Streams for processing by workers
 */

import { getRedisClient } from "../utils/redis.js";
import { JobMessage, ProducerOptions } from "../types/index.js";

export class MessageProducer {
  private redis: ReturnType<typeof getRedisClient>;
  private streamKey: string;
  private maxLength?: number;

  constructor(options: ProducerOptions) {
    this.redis = getRedisClient();
    this.streamKey = options.streamKey;
    this.maxLength = options.maxLength;
  }

  /**
   * Connect to Redis
   */
  async connect(): Promise<void> {
    if (this.redis.status !== "ready") {
      await this.redis.connect();
    }
  }

  /**
   * Publish a job message to the stream
   *
   * @param message - The job message to publish
   * @returns The message ID assigned by Redis
   */
  async publish(message: JobMessage): Promise<string> {
    try {
      // Convert message to Redis stream format
      const streamData: Record<string, string> = {
        jobId: message.jobId,
        directory: message.directory,
        files: JSON.stringify(message.files),
        step: message.step,
        status: message.status,
        timestamp: message.timestamp.toString(),
      };

      // Add optional fields if present
      if (message.error) {
        streamData.error = message.error;
      }
      if (message.metadata) {
        streamData.metadata = JSON.stringify(message.metadata);
      }

      // Publish to stream
      // Build arguments array for xadd command
      const args: (string | number)[] = [this.streamKey, "*"];

      // Add MAXLEN if specified (keeps stream size manageable)
      if (this.maxLength) {
        args.push("MAXLEN", "~", this.maxLength);
      }

      // Add all field-value pairs
      for (const [key, value] of Object.entries(streamData)) {
        args.push(key, value);
      }

      // Use apply to handle dynamic arguments
      const messageId = await (this.redis.xadd as any).apply(this.redis, args);

      console.log(
        `📤 Published message ${messageId} for job ${message.jobId} (step: ${message.step})`
      );

      return messageId as string;
    } catch (error) {
      console.error("Error publishing message:", error);
      throw error;
    }
  }

  /**
   * Publish multiple messages in batch
   */
  async publishBatch(messages: JobMessage[]): Promise<string[]> {
    const pipeline = this.redis.pipeline();
    const messageIds: string[] = [];

    for (const message of messages) {
      const streamData: Record<string, string> = {
        jobId: message.jobId,
        directory: message.directory,
        files: JSON.stringify(message.files),
        step: message.step,
        status: message.status,
        timestamp: message.timestamp.toString(),
      };

      if (message.error) {
        streamData.error = message.error;
      }
      if (message.metadata) {
        streamData.metadata = JSON.stringify(message.metadata);
      }

      const args: (string | number)[] = [this.streamKey, "*"];
      if (this.maxLength) {
        args.push("MAXLEN", "~", this.maxLength);
      }
      // Add all field-value pairs
      for (const [key, value] of Object.entries(streamData)) {
        args.push(key, value);
      }

      // Use apply to handle dynamic arguments in pipeline
      (pipeline.xadd as any).apply(pipeline, args);
    }

    const results = await pipeline.exec();

    if (results) {
      for (const [error, result] of results) {
        if (error) {
          throw error;
        }
        messageIds.push(result as string);
      }
    }

    console.log(`📤 Published ${messageIds.length} messages in batch`);
    return messageIds;
  }

  /**
   * Get stream information
   */
  async getStreamInfo(): Promise<any> {
    return await this.redis.xinfo("STREAM", this.streamKey);
  }

  /**
   * Get stream length
   */
  async getStreamLength(): Promise<number> {
    return await this.redis.xlen(this.streamKey);
  }
}
