import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function getSystemRoot() {
  return process.env.FRAUD_SYSTEM_ROOT
    ? path.resolve(process.env.FRAUD_SYSTEM_ROOT)
    : path.resolve(__dirname, "..");
}

export function getQueuePath() {
  return process.env.TRANSACTIONS_QUEUE_FILE
    ? path.resolve(process.env.TRANSACTIONS_QUEUE_FILE)
    : path.join(getSystemRoot(), "shared", "data", "transactions.json");
}

export function getProcessedPath() {
  return process.env.PROCESSED_TRANSACTIONS_FILE
    ? path.resolve(process.env.PROCESSED_TRANSACTIONS_FILE)
    : path.join(getSystemRoot(), "shared", "data", "processed_transactions.json");
}

function ensureFile(filePath, defaultContent) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, defaultContent, "utf8");
  }
}

export function readJsonArray(filePath) {
  ensureFile(filePath, "[]\n");
  const raw = fs.readFileSync(filePath, "utf8").trim() || "[]";
  const data = JSON.parse(raw);
  if (!Array.isArray(data)) {
    throw new Error(`${filePath} must contain a JSON array`);
  }
  return data;
}

export function writeJsonArray(filePath, data) {
  ensureFile(filePath, "[]\n");
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

export function readQueue() {
  return readJsonArray(getQueuePath());
}

export function writeQueue(transactions) {
  writeJsonArray(getQueuePath(), transactions);
}

export function readProcessed() {
  return readJsonArray(getProcessedPath());
}

export function writeProcessed(results) {
  writeJsonArray(getProcessedPath(), results);
}

export function dequeuePendingTransactions() {
  const queue = readQueue();
  const pending = queue.filter((item) => item.status === "pending");
  const remaining = queue.filter((item) => item.status !== "pending");
  return { pending, remaining };
}

export function markQueueRemaining(remaining) {
  writeQueue(remaining);
}

export function appendProcessedResults(newResults) {
  const processed = readProcessed();
  writeProcessed([...processed, ...newResults]);
}
