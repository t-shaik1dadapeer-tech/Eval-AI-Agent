#!/usr/bin/env node

const {
  convertCurrency,
  formatSuccess,
  formatError,
} = require('./client');

const SUPPORTED = ['USD', 'INR', 'EUR'];

function printUsage() {
  console.error('Usage: node src/cli.js <amount> <from_currency> <to_currency>');
  console.error('Example: node src/cli.js 100 USD INR');
}

function validateArgs(args) {
  if (args.length !== 3) {
    return { valid: false, error: 'Expected exactly 3 arguments: amount from_currency to_currency' };
  }

  const [amountRaw, fromCurrency, toCurrency] = args;
  const amount = Number(amountRaw);

  if (Number.isNaN(amount) || amount <= 0) {
    return { valid: false, error: 'amount must be a number greater than 0' };
  }

  const from = fromCurrency.toUpperCase();
  const to = toCurrency.toUpperCase();

  if (!SUPPORTED.includes(from)) {
    return { valid: false, error: `unsupported from_currency: ${fromCurrency}` };
  }
  if (!SUPPORTED.includes(to)) {
    return { valid: false, error: `unsupported to_currency: ${toCurrency}` };
  }

  return { valid: true, amount, fromCurrency: from, toCurrency: to };
}

async function main() {
  const validation = validateArgs(process.argv.slice(2));
  if (!validation.valid) {
    printUsage();
    console.error(formatError(validation.error));
    process.exit(1);
  }

  const { amount, fromCurrency, toCurrency } = validation;

  try {
    const result = await convertCurrency(amount, fromCurrency, toCurrency);

    if (result.status === 200) {
      console.log(
        formatSuccess(
          result.data.amount,
          result.data.from_currency,
          result.data.to_currency,
          result.data.converted_amount,
        ),
      );
      process.exit(0);
    }

    const detail = result.data?.detail;
    const message = typeof detail === 'string'
      ? detail
      : JSON.stringify(detail || 'Conversion request failed');
    console.error(formatError(message));
    process.exit(1);
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      console.error(formatError('Currency conversion service is unavailable'));
      process.exit(2);
    }
    console.error(formatError(error.message || 'Unexpected error'));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { validateArgs, main };
