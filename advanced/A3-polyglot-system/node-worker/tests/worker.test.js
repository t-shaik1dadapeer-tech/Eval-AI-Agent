import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { processQueueOnce } from "../src/processor.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const systemRoot = path.resolve(__dirname, "..", "..");

function createTempQueueEnv() {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "a3-worker-"));
  const queueFile = path.join(tempDir, "transactions.json");
  const processedFile = path.join(tempDir, "processed_transactions.json");
  fs.writeFileSync(queueFile, "[]\n", "utf8");
  fs.writeFileSync(processedFile, "[]\n", "utf8");

  const previous = {
    FRAUD_SYSTEM_ROOT: process.env.FRAUD_SYSTEM_ROOT,
    TRANSACTIONS_QUEUE_FILE: process.env.TRANSACTIONS_QUEUE_FILE,
    PROCESSED_TRANSACTIONS_FILE: process.env.PROCESSED_TRANSACTIONS_FILE,
    RUST_ENGINE_BIN: process.env.RUST_ENGINE_BIN,
  };

  process.env.FRAUD_SYSTEM_ROOT = systemRoot;
  process.env.TRANSACTIONS_QUEUE_FILE = queueFile;
  process.env.PROCESSED_TRANSACTIONS_FILE = processedFile;

  return { tempDir, queueFile, processedFile, previous };
}

function restoreEnv(previous) {
  for (const [key, value] of Object.entries(previous)) {
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
}

describe("queue processing", () => {
  test("processes pending transactions and writes processed output", () => {
    const { tempDir, queueFile, processedFile, previous } = createTempQueueEnv();

    try {
      const enginePath = path.join(
        systemRoot,
        "rust-engine",
        "target",
        "release",
        process.platform === "win32" ? "fraud-engine.exe" : "fraud-engine",
      );
      if (!fs.existsSync(enginePath)) {
        throw new Error(
          `rust engine not built; run: cd rust-engine && cargo build --release`,
        );
      }
      process.env.RUST_ENGINE_BIN = enginePath;

      fs.writeFileSync(
        queueFile,
        JSON.stringify(
          [
            {
              transaction_id: "txn-001",
              user_id: "user-123",
              amount: 15000,
              merchant: "electronics",
              country: "IN",
              status: "pending",
            },
          ],
          null,
          2,
        ) + "\n",
        "utf8",
      );

      const summary = processQueueOnce({ logger: { info() {}, warn() {}, error() {} } });

      expect(summary.processedCount).toBe(1);
      expect(summary.results[0]).toMatchObject({
        transaction_id: "txn-001",
        risk_score: 82,
        risk_level: "HIGH",
      });

      const processed = JSON.parse(fs.readFileSync(processedFile, "utf8"));
      expect(processed).toHaveLength(1);
      expect(processed[0].risk_level).toBe("HIGH");

      const remainingQueue = JSON.parse(fs.readFileSync(queueFile, "utf8"));
      expect(remainingQueue).toHaveLength(0);
    } finally {
      restoreEnv(previous);
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });
});

describe("invalid transaction handling", () => {
  test("skips malformed transactions without crashing", () => {
    const { tempDir, queueFile, processedFile, previous } = createTempQueueEnv();

    try {
      fs.writeFileSync(
        queueFile,
        JSON.stringify(
          [
            {
              transaction_id: "bad-txn",
              user_id: "",
              amount: -10,
              merchant: "",
              country: "IN",
              status: "pending",
            },
            {
              transaction_id: "good-txn",
              user_id: "user-1",
              amount: 500,
              merchant: "grocery",
              country: "IN",
              status: "pending",
            },
          ],
          null,
          2,
        ) + "\n",
        "utf8",
      );

      const enginePath = path.join(
        systemRoot,
        "rust-engine",
        "target",
        "release",
        process.platform === "win32" ? "fraud-engine.exe" : "fraud-engine",
      );
      process.env.RUST_ENGINE_BIN = enginePath;

      const summary = processQueueOnce({ logger: { info() {}, warn() {}, error() {} } });

      expect(summary.malformedCount).toBe(1);
      expect(summary.processedCount).toBe(1);
      expect(summary.results[0].transaction_id).toBe("good-txn");
      expect(summary.results[0].risk_level).toBe("LOW");

      const processed = JSON.parse(fs.readFileSync(processedFile, "utf8"));
      expect(processed).toHaveLength(1);
    } finally {
      restoreEnv(previous);
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
