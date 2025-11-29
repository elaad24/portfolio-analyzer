/**
 * Redis Streams Consumer
 *
 * Consumes job messages from Redis Streams using consumer groups
 * Supports multiple consumers for load balancing
 */

import { getRedisClient } from "../utils/redis.js";
import {
  JobMessage,
  ConsumerOptions,
  StreamMessage,
  JobStatusEnum,
  JobStepEnum,
} from "../types/index.js";

export class MessageConsumer {
  private redis: ReturnType<typeof getRedisClient>;
  private streamKey: string;
  private groupName: string;
  private consumerName: string;
  private blockTime: number;
  private count: number;

  constructor(options: ConsumerOptions) {
    this.redis = getRedisClient();
    this.streamKey = options.streamKey;
    this.groupName = options.groupName;
    this.consumerName = options.consumerName;
    this.blockTime = options.blockTime || 1000; // Default 1 second
    this.count = options.count || 10; // Default 10 messages
  }

  /**
   * Connect to Redis and create consumer group if it doesn't exist
   */
  async connect(): Promise<void> {
    if (this.redis.status !== "ready") {
      await this.redis.connect();
    }

    // Create consumer group if it doesn't exist
    try {
      await this.redis.xgroup(
        "CREATE",
        this.streamKey,
        this.groupName,
        "0",
        "MKSTREAM"
      );
      console.log(`✅ Consumer group '${this.groupName}' created`);
    } catch (error: any) {
      // Group already exists - this is fine
      if (error.message?.includes("BUSYGROUP")) {
        console.log(`ℹ️  Consumer group '${this.groupName}' already exists`);
      } else {
        throw error;
      }
    }
  }

  /**
   * Read messages from the stream
   *
   * @param callback - Function to process each message
   * @param autoAck - Automatically acknowledge messages after processing (default: false)
   */
  async consume(
    callback: (message: StreamMessage) => Promise<void> | void,
    autoAck: boolean = false
  ): Promise<void> {
    try {
      // Read messages from the stream using XREADGROUP
      const results = await this.redis.xreadgroup(
        "GROUP",
        this.groupName,
        this.consumerName,
        "COUNT",
        this.count,
        "BLOCK",
        this.blockTime,
        "STREAMS",
        this.streamKey,
        ">" // Read new messages
      );

      if (!results || results.length === 0) {
        return; // No messages available
      }

      // Type assertion: xreadgroup returns [[streamKey, [[messageId, [fields...]], ...]]]
      const result = results[0] as [string, Array<[string, string[]]>];
      const [, messages] = result;

      if (!messages || messages.length === 0) {
        return;
      }

      for (const [messageId, fields] of messages) {
        try {
          // Parse message from Redis format
          const message = this.parseMessage(fields);

          const streamMessage: StreamMessage = {
            id: messageId as string,
            message,
          };

          // Process message
          await callback(streamMessage);

          // Acknowledge message if autoAck is enabled
          if (autoAck) {
            await this.ack(messageId as string);
          }
        } catch (error) {
          console.error(`Error processing message ${messageId}:`, error);
          // Message will remain in pending list for retry
        }
      }
    } catch (error) {
      console.error("Error consuming messages:", error);
      throw error;
    }
  }

  /**
   * Start consuming messages in a loop
   *
   * @param callback - Function to process each message
   * @param autoAck - Automatically acknowledge messages
   */
  async start(
    callback: (message: StreamMessage) => Promise<void> | void,
    autoAck: boolean = false
  ): Promise<void> {
    console.log(
      `🔄 Consumer '${this.consumerName}' started (group: ${this.groupName})`
    );

    while (true) {
      try {
        await this.consume(callback, autoAck);
      } catch (error) {
        console.error("Error in consumer loop:", error);
        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
  }

  /**
   * Acknowledge a processed message
   */
  async ack(messageId: string): Promise<void> {
    await this.redis.xack(this.streamKey, this.groupName, messageId);
    console.log(`✅ Acknowledged message ${messageId}`);
  }

  /**
   * Get pending messages for this consumer
   */
  async getPendingMessages(): Promise<
    Array<{ id: string; message: JobMessage }>
  > {
    const pending = await this.redis.xpending(
      this.streamKey,
      this.groupName,
      "-",
      "+",
      this.count,
      this.consumerName
    );

    if (!pending || !Array.isArray(pending) || pending.length === 0) {
      return [];
    }

    // Type assertion: xpending returns Array<[messageId, consumerName, idleTime, deliveryCount]>
    const pendingEntries = pending as Array<[string, string, number, number]>;

    const messages: Array<{ id: string; message: JobMessage }> = [];

    for (const [messageId] of pendingEntries) {
      const messageData = await this.redis.xrange(
        this.streamKey,
        messageId,
        messageId
      );
      if (messageData && Array.isArray(messageData) && messageData.length > 0) {
        // xrange returns Array<[messageId, [fields...]]>
        const entry = messageData[0] as [string, string[]];
        const [, fields] = entry;
        const message = this.parseMessage(fields);
        messages.push({ id: messageId, message });
      }
    }

    return messages;
  }

  /**
   * Claim pending messages that have been idle for too long
   */
  async claimPendingMessages(minIdleTime: number = 60000): Promise<void> {
    const pending = await this.redis.xpending(
      this.streamKey,
      this.groupName,
      "-",
      "+",
      this.count
    );

    if (!pending || !Array.isArray(pending) || pending.length === 0) {
      return;
    }

    // Type assertion: xpending returns Array<[messageId, consumerName, idleTime, deliveryCount]>
    const pendingEntries = pending as Array<[string, string, number, number]>;
    const messageIds = pendingEntries.map(([id]) => id);

    if (messageIds.length === 0) {
      return;
    }

    // Use apply to handle dynamic arguments for xclaim
    const claimed = await (this.redis.xclaim as any).apply(this.redis, [
      this.streamKey,
      this.groupName,
      this.consumerName,
      minIdleTime,
      ...messageIds,
    ]);

    if (claimed && Array.isArray(claimed) && claimed.length > 0) {
      console.log(`🔄 Claimed ${claimed.length} pending messages`);
    }
  }

  /**
   * Parse Redis stream fields into JobMessage
   */
  private parseMessage(fields: string[]): JobMessage {
    const data: Record<string, string> = {};

    // Convert array of [key, value, key, value, ...] to object
    for (let i = 0; i < fields.length; i += 2) {
      data[fields[i]] = fields[i + 1];
    }

    return {
      jobId: data.jobId,
      directory: data.directory,
      files: JSON.parse(data.files || "[]"),
      step: data.step as JobStepEnum,
      status: data.status as JobStatusEnum,
      timestamp: parseInt(data.timestamp, 10),
      error: data.error,
      metadata: data.metadata ? JSON.parse(data.metadata) : undefined,
    };
  }
}
