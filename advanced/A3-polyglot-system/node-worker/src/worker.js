import { processQueueOnce } from "./processor.js";

const POLL_INTERVAL_MS = Number(process.env.WORKER_POLL_MS || 2000);
const runOnce = process.argv.includes("--once");

async function runLoop() {
  if (runOnce) {
    const summary = processQueueOnce();
    console.log(
      JSON.stringify({
        mode: "once",
        processed: summary.processedCount,
        malformed: summary.malformedCount,
      }),
    );
    return;
  }

  console.log(`worker started; polling every ${POLL_INTERVAL_MS}ms`);
  setInterval(() => {
    processQueueOnce();
  }, POLL_INTERVAL_MS);
}

runLoop().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
