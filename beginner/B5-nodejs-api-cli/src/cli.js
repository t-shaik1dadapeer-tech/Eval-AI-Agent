#!/usr/bin/env node

const {
  createTransaction,
  listTransactions,
  getTransaction,
  getBalance,
  DEFAULT_BASE,
} = require('./client');

function usage() {
  console.error(`Usage:
  node src/cli.js create <credit|debit> <amount> [description]
  node src/cli.js list
  node src/cli.js get <id>
  node src/cli.js balance

Environment:
  B5_API_BASE  API base URL (default: ${DEFAULT_BASE})`);
}

function fail(message, code = 1) {
  console.error(`Error: ${message}`);
  process.exit(code);
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (!command) {
    usage();
    process.exit(1);
  }

  try {
    if (command === 'create') {
      const [type, amountRaw, ...descParts] = args;
      if (!type || !amountRaw) {
        usage();
        fail('create requires type and amount');
      }
      const amount = Number(amountRaw);
      if (!['credit', 'debit'].includes(type)) fail('type must be credit or debit');
      if (Number.isNaN(amount) || amount <= 0) fail('amount must be a number > 0');
      const res = await createTransaction({
        type,
        amount,
        description: descParts.length ? descParts.join(' ') : null,
      });
      if (res.status !== 201) fail(JSON.stringify(res.data));
      console.log(JSON.stringify(res.data, null, 2));
      return;
    }

    if (command === 'list') {
      const res = await listTransactions();
      if (res.status !== 200) fail(JSON.stringify(res.data));
      console.log(JSON.stringify(res.data, null, 2));
      return;
    }

    if (command === 'get') {
      const [id] = args;
      if (!id) fail('get requires transaction id');
      const res = await getTransaction(id);
      if (res.status === 404) fail('Transaction not found', 2);
      if (res.status !== 200) fail(JSON.stringify(res.data));
      console.log(JSON.stringify(res.data, null, 2));
      return;
    }

    if (command === 'balance') {
      const res = await getBalance();
      if (res.status !== 200) fail(JSON.stringify(res.data));
      console.log(`balance=${res.data.balance} count=${res.data.transactionCount}`);
      return;
    }

    usage();
    fail(`unknown command: ${command}`);
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') {
      fail('Transaction API is unavailable — start with npm start', 2);
    }
    fail(err.message || String(err));
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, usage };
