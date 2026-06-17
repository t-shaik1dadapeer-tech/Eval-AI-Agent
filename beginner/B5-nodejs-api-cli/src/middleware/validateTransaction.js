const { VALID_TYPES } = require('../models/transactionTypes');

function validateCreateTransaction(req, res, next) {
  const { type, amount, description } = req.body;
  const errors = [];

  if (type === undefined || type === null || type === '') {
    errors.push({ field: 'type', message: 'type is required' });
  } else if (!VALID_TYPES.includes(type)) {
    errors.push({ field: 'type', message: 'type must be credit or debit' });
  }

  if (amount === undefined || amount === null || amount === '') {
    errors.push({ field: 'amount', message: 'amount is required' });
  } else if (typeof amount !== 'number' || Number.isNaN(amount)) {
    errors.push({ field: 'amount', message: 'amount must be a number' });
  } else if (amount <= 0) {
    errors.push({ field: 'amount', message: 'amount must be greater than 0' });
  }

  if (description !== undefined && description !== null && typeof description !== 'string') {
    errors.push({ field: 'description', message: 'description must be a string' });
  }

  if (errors.length > 0) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors,
    });
  }

  req.body = {
    type,
    amount,
    description:
      typeof description === 'string' && description.trim() !== ''
        ? description.trim()
        : null,
  };

  return next();
}

module.exports = {
  validateCreateTransaction,
};
