const createApp = require('../src/app');
const { transactionService } = require('../src/services/transactionService');

const app = createApp();

beforeEach(() => {
  transactionService.clear();
});

afterEach(() => {
  transactionService.clear();
});

describe('Transaction API', () => {
  test('create transaction', async () => {
    const response = await require('supertest')(app)
      .post('/transactions')
      .send({ type: 'credit', amount: 100, description: 'Salary' })
      .expect(201);

    expect(response.body.type).toBe('credit');
    expect(response.body.amount).toBe(100);
    expect(response.body.description).toBe('Salary');
    expect(response.body.id).toBeDefined();
    expect(response.body.createdAt).toBeDefined();
  });

  test('fetch transactions', async () => {
    const request = require('supertest')(app);

    await request.post('/transactions').send({ type: 'credit', amount: 50 });
    await request.post('/transactions').send({ type: 'debit', amount: 20 });

    const response = await request.get('/transactions').expect(200);

    expect(response.body).toHaveLength(2);
    expect(response.body[0].amount).toBe(50);
    expect(response.body[1].type).toBe('debit');
  });

  test('calculate balance', async () => {
    const request = require('supertest')(app);

    await request.post('/transactions').send({ type: 'credit', amount: 100 });
    await request.post('/transactions').send({ type: 'debit', amount: 30 });

    const response = await request.get('/balance').expect(200);

    expect(response.body.balance).toBe(70);
    expect(response.body.transactionCount).toBe(2);
  });

  test('invalid payload validation', async () => {
    const request = require('supertest')(app);

    const negativeAmount = await request
      .post('/transactions')
      .send({ type: 'credit', amount: -10 })
      .expect(400);
    expect(negativeAmount.body.error).toBe('Validation failed');

    const invalidType = await request
      .post('/transactions')
      .send({ type: 'invalid', amount: 10 })
      .expect(400);
    expect(invalidType.body.details).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ field: 'type' }),
      ]),
    );

    const missingFields = await request.post('/transactions').send({}).expect(400);
    expect(missingFields.body.details.length).toBeGreaterThan(0);
  });

  test('debit balance scenario', async () => {
    const request = require('supertest')(app);

    await request.post('/transactions').send({ type: 'credit', amount: 200 });
    await request.post('/transactions').send({ type: 'debit', amount: 75.5 });
    await request.post('/transactions').send({ type: 'debit', amount: 24.5 });

    const response = await request.get('/balance').expect(200);

    expect(response.body.balance).toBe(100);
    expect(response.body.transactionCount).toBe(3);
  });
});
