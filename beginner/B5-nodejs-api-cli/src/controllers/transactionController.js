const { transactionService } = require('../services/transactionService');

function createTransaction(req, res) {
  const transaction = transactionService.createTransaction(req.body);
  res.status(201).json(transaction);
}

function getTransactions(req, res) {
  const transactions = transactionService.listTransactions();
  res.status(200).json(transactions);
}

function getTransactionById(req, res) {
  const transaction = transactionService.getTransactionById(req.params.id);
  if (!transaction) {
    res.status(404).json({ error: 'Transaction not found' });
    return;
  }
  res.status(200).json(transaction);
}

function getBalance(req, res) {
  const balance = transactionService.getBalance();
  res.status(200).json(balance);
}

module.exports = {
  createTransaction,
  getTransactions,
  getTransactionById,
  getBalance,
};
