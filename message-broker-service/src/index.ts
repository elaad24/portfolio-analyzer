/**
 * Message Broker Service Entry Point
 * 
 * Redis Streams-based message broker for portfolio analyzer microservices
 */

import { MessageProducer } from "./producer/index.js";
import { MessageConsumer } from "./consumer/index.js";
import { JobMessage, StreamMessage, JobStatusEnum, JobStepEnum } from "./types/index.js";
import { closeRedisConnection } from "./utils/redis.js";

// Export classes and types for use in other services
export { MessageProducer } from "./producer/index.js";
export { MessageConsumer } from "./consumer/index.js";
export * from "./types/index.js";

/**
 * Example usage as a standalone service
 */
async function main() {
  const STREAM_KEY = process.env.REDIS_STREAM_KEY || "portfolio:jobs";
  const GROUP_NAME = process.env.CONSUMER_GROUP || "portfolio-workers";
  const CONSUMER_NAME = process.env.CONSUMER_NAME || `consumer-${Date.now()}`;

  // Initialize producer
  const producer = new MessageProducer({
    streamKey: STREAM_KEY,
    maxLength: 10000, // Keep last 10k messages
  });

  // Initialize consumer
  const consumer = new MessageConsumer({
    streamKey: STREAM_KEY,
    groupName: GROUP_NAME,
    consumerName: CONSUMER_NAME,
    blockTime: 1000,
    count: 10,
  });

  try {
    // Connect both
    await producer.connect();
    await consumer.connect();

    console.log("🚀 Message Broker Service started");
    console.log(`📡 Stream: ${STREAM_KEY}`);
    console.log(`👥 Consumer Group: ${GROUP_NAME}`);
    console.log(`🤖 Consumer Name: ${CONSUMER_NAME}`);

    // Example: Start consuming messages
    // Uncomment to run as a consumer service
    /*
    await consumer.start(async (streamMessage: StreamMessage) => {
      console.log(`📥 Received message:`, streamMessage.message);
      
      // Process message here
      // After processing, acknowledge it
      await consumer.ack(streamMessage.id);
    }, false); // Set to true for auto-ack
    */

    // Example: Publish a test message
    // Uncomment to test publishing
    /*
    const testMessage: JobMessage = {
      jobId: `job-${Date.now()}`,
      directory: "/uploads",
      files: ["file1.csv", "file2.xlsx"],
      step: JobStepEnum.FILE_UPLOADED,
      status: JobStatusEnum.PENDING,
      timestamp: Date.now(),
    };

    await producer.publish(testMessage);
    */

  } catch (error) {
    console.error("Fatal error:", error);
    process.exit(1);
  }

  // Graceful shutdown
  process.on("SIGINT", async () => {
    console.log("\n🛑 Shutting down...");
    await closeRedisConnection();
    process.exit(0);
  });

  process.on("SIGTERM", async () => {
    console.log("\n🛑 Shutting down...");
    await closeRedisConnection();
    process.exit(0);
  });
}

// Run if executed directly
if (import.meta.main) {
  main();
}

