const { randomUUID } = require('crypto');
const { TRANSACTION_TYPES } = require('../models/transactionTypes');

class TransactionService {
  constructor() {
    this._transactions = [];
  }

  createTransaction({ type, amount, description = null }) {
    const transaction = {
      id: randomUUID(),
      type,
      amount,
      description,
      createdAt: new Date().toISOString(),
    };

    this._transactions.push(transaction);
    return transaction;
  }

  listTransactions() {
    return [...this._transactions];
  }

  getBalance() {
    const balance = this._transactions.reduce((total, transaction) => {
      if (transaction.type === TRANSACTION_TYPES.CREDIT) {
        return total + transaction.amount;
      }
      return total - transaction.amount;
    }, 0);

    return {
      balance,
      transactionCount: this._transactions.length,
    };
  }

  clear() {
    this._transactions = [];
  }
}

const transactionService = new TransactionService();

module.exports = {
  TransactionService,
  transactionService,
};
