const express = require('express');
const {
  createTransaction,
  getTransactions,
  getBalance,
} = require('../controllers/transactionController');
const { validateCreateTransaction } = require('../middleware/validateTransaction');

const router = express.Router();

router.post('/transactions', validateCreateTransaction, createTransaction);
router.get('/transactions', getTransactions);
router.get('/balance', getBalance);

module.exports = router;
