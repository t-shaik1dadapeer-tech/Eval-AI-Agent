import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function getRustEnginePath() {
  if (process.env.RUST_ENGINE_BIN) {
    return path.resolve(process.env.RUST_ENGINE_BIN);
  }

  const systemRoot = process.env.FRAUD_SYSTEM_ROOT
    ? path.resolve(process.env.FRAUD_SYSTEM_ROOT)
    : path.resolve(__dirname, "..");

  return path.join(
    systemRoot,
    "rust-engine",
    "target",
    "release",
    process.platform === "win32" ? "fraud-engine.exe" : "fraud-engine",
  );
}

export function scoreTransaction(transaction) {
  const enginePath = getRustEnginePath();
  const payload = JSON.stringify({
    amount: transaction.amount,
    merchant: transaction.merchant,
    country: transaction.country,
  });

  const result = spawnSync(enginePath, [payload], {
    encoding: "utf8",
    maxBuffer: 1024 * 1024,
  });

  if (result.error) {
    throw new Error(`failed to invoke rust engine: ${result.error.message}`);
  }

  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    throw new Error(stderr || `rust engine exited with code ${result.status}`);
  }

  const stdout = (result.stdout || "").trim();
  try {
    return JSON.parse(stdout);
  } catch (error) {
    throw new Error(`invalid JSON from rust engine: ${stdout}`);
  }
}
