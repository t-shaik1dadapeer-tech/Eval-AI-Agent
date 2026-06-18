const express = require('express');
const transactionRoutes = require('./routes/transactionRoutes');
const {
  notFoundHandler,
  errorHandler,
} = require('./middleware/errorHandler');

function createApp() {
  const app = express();

  app.use(express.json());

  app.get('/', (req, res) => {
    res.status(200).json({
      service: 'b5-nodejs-api-cli',
      message: 'Transaction API — use /health, /transactions, /balance',
      endpoints: ['/health', '/transactions', '/balance'],
      note: 'Grafana dashboards (D6) run at http://localhost:3000 when docker compose is up',
    });
  });

  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  app.use(transactionRoutes);
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}

module.exports = createApp;
