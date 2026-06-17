const express = require('express');
const transactionRoutes = require('./routes/transactionRoutes');
const {
  notFoundHandler,
  errorHandler,
} = require('./middleware/errorHandler');

function createApp() {
  const app = express();

  app.use(express.json());

  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  app.use(transactionRoutes);
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}

module.exports = createApp;
