const axios = require('axios');

const DEFAULT_BASE_URL = 'http://127.0.0.1:8000';

function getBaseUrl() {
  return process.env.CONVERTER_API_URL || DEFAULT_BASE_URL;
}

async function convertCurrency(amount, fromCurrency, toCurrency, options = {}) {
  const baseUrl = options.baseUrl || getBaseUrl();
  const url = `${baseUrl}/convert`;

  const response = await axios.post(
    url,
    {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
    },
    {
      headers: { 'Content-Type': 'application/json' },
      validateStatus: () => true,
    },
  );

  return {
    status: response.status,
    data: response.data,
  };
}

function formatSuccess(amount, fromCurrency, toCurrency, convertedAmount) {
  return [
    `Converting ${amount} ${fromCurrency} -> ${toCurrency}`,
    `Converted Amount: ${convertedAmount}`,
  ].join('\n');
}

function formatError(message) {
  return `Error: ${message}`;
}

module.exports = {
  convertCurrency,
  formatSuccess,
  formatError,
  getBaseUrl,
};
