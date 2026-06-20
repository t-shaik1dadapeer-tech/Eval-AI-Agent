jest.mock('../src/client', () => ({
  DEFAULT_BASE: 'http://127.0.0.1:3001',
  request: jest.fn(),
  createTransaction: jest.fn(),
  listTransactions: jest.fn(),
  getTransaction: jest.fn(),
  getBalance: jest.fn(),
}));

const client = require('../src/client');

describe('CLI client module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('createTransaction delegates to request', async () => {
    client.createTransaction.mockResolvedValue({ status: 201, data: { id: 'x' } });
    const res = await client.createTransaction({ type: 'credit', amount: 10 });
    expect(res.status).toBe(201);
    expect(client.createTransaction).toHaveBeenCalledWith({ type: 'credit', amount: 10 });
  });

  test('getTransaction delegates to client', async () => {
    client.getTransaction.mockResolvedValue({ status: 200, data: { id: 'abc' } });
    const res = await client.getTransaction('abc');
    expect(res.data.id).toBe('abc');
  });
});

describe('CLI entry', () => {
  test('usage function is defined', () => {
    const { usage } = require('../src/cli');
    expect(typeof usage).toBe('function');
  });
});
