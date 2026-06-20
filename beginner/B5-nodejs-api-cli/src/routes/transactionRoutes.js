const express = require('express');
const {
  createTransaction,
  getTransactions,
  getTransactionById,
  getBalance,
} = require('../controllers/transactionController');
const { validateCreateTransaction } = require('../middleware/validateTransaction');

const router = express.Router();

router.post('/transactions', validateCreateTransaction, createTransaction);
router.get('/transactions', getTransactions);
router.get('/transactions/:id', getTransactionById);
router.get('/balance', getBalance);

module.exports = router;
