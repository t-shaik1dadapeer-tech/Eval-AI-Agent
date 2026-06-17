import pg from "pg";

const { Client } = pg;

const DATABASE_URL =
  process.env.DATABASE_URL ||
  "postgresql://d2user:d2pass@localhost:5432/transactions";
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS || 2000);

async function waitForDatabase(maxAttempts = 30) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const client = new Client({ connectionString: DATABASE_URL });
    try {
      await client.connect();
      await client.query("SELECT 1");
      await client.end();
      console.log("worker connected to database");
      return;
    } catch (error) {
      await client.end().catch(() => {});
      console.log(`waiting for database (attempt ${attempt}/${maxAttempts})`);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
  throw new Error("database not ready");
}

async function processPendingTransactions() {
  const client = new Client({ connectionString: DATABASE_URL });
  await client.connect();

  try {
    const pending = await client.query(
      `SELECT id, transaction_id, amount, status
       FROM transactions
       WHERE status = 'PENDING'
       ORDER BY id ASC`,
    );

    for (const row of pending.rows) {
      console.log(`Processing transaction ${row.transaction_id}`);
      await client.query(
        `UPDATE transactions SET status = 'PROCESSED' WHERE id = $1`,
        [row.id],
      );
      console.log(`Updated status to PROCESSED for ${row.transaction_id}`);
    }
  } finally {
    await client.end();
  }
}

async function run() {
  await waitForDatabase();
  console.log(`worker started; polling every ${POLL_INTERVAL_MS}ms`);

  setInterval(() => {
    processPendingTransactions().catch((error) => {
      console.error(`worker error: ${error.message}`);
    });
  }, POLL_INTERVAL_MS);
}

run().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
