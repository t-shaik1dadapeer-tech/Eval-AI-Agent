const http = require('http');
const https = require('https');

const DEFAULT_BASE = process.env.B5_API_BASE || 'http://127.0.0.1:3001';

function request(method, path, body = null, baseUrl = DEFAULT_BASE) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`);
    const payload = body ? JSON.stringify(body) : null;
    const lib = url.protocol === 'https:' ? https : http;

    const req = lib.request(
      {
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: `${url.pathname}${url.search}`,
        method,
        headers: {
          Accept: 'application/json',
          ...(payload ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) } : {}),
        },
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          let parsed = data;
          try {
            parsed = data ? JSON.parse(data) : null;
          } catch {
            // keep raw string
          }
          resolve({ status: res.statusCode, data: parsed });
        });
      },
    );

    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

async function createTransaction(payload, baseUrl) {
  return request('POST', '/transactions', payload, baseUrl);
}

async function listTransactions(baseUrl) {
  return request('GET', '/transactions', null, baseUrl);
}

async function getTransaction(id, baseUrl) {
  return request('GET', `/transactions/${id}`, null, baseUrl);
}

async function getBalance(baseUrl) {
  return request('GET', '/balance', null, baseUrl);
}

module.exports = {
  DEFAULT_BASE,
  request,
  createTransaction,
  listTransactions,
  getTransaction,
  getBalance,
};
