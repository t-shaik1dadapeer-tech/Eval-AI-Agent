import {
  appendProcessedResults,
  dequeuePendingTransactions,
  markQueueRemaining,
} from "./queue.js";
import { scoreTransaction } from "./rustClient.js";

export function processQueueOnce({ logger = console } = {}) {
  const { pending, remaining } = dequeuePendingTransactions();
  const processedResults = [];
  const malformed = [];

  for (const transaction of pending) {
    if (!isValidTransaction(transaction)) {
      malformed.push(transaction);
      logger.warn(
        `skipping malformed transaction: ${transaction.transaction_id ?? "unknown"}`,
      );
      continue;
    }

    try {
      const score = scoreTransaction(transaction);
      const result = {
        transaction_id: transaction.transaction_id,
        user_id: transaction.user_id,
        amount: transaction.amount,
        merchant: transaction.merchant,
        country: transaction.country,
        risk_score: score.risk_score,
        risk_level: score.risk_level,
        processed_at: new Date().toISOString(),
      };
      processedResults.push(result);
      logger.info(
        `processed ${transaction.transaction_id}: score=${score.risk_score} level=${score.risk_level}`,
      );
    } catch (error) {
      malformed.push(transaction);
      logger.error(
        `failed to score ${transaction.transaction_id}: ${error.message}`,
      );
    }
  }

  if (processedResults.length > 0) {
    appendProcessedResults(processedResults);
  }

  const failedIds = new Set(malformed.map((item) => item.transaction_id));
  const cleanedRemaining = remaining.filter(
    (item) => !failedIds.has(item.transaction_id),
  );
  markQueueRemaining(cleanedRemaining);

  return {
    processedCount: processedResults.length,
    malformedCount: malformed.length,
    results: processedResults,
  };
}

function isValidTransaction(transaction) {
  return (
    transaction &&
    typeof transaction.transaction_id === "string" &&
    transaction.transaction_id.length > 0 &&
    typeof transaction.user_id === "string" &&
    transaction.user_id.length > 0 &&
    typeof transaction.merchant === "string" &&
    transaction.merchant.length > 0 &&
    typeof transaction.country === "string" &&
    transaction.country.length === 2 &&
    typeof transaction.amount === "number" &&
    transaction.amount > 0
  );
}
