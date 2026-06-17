const axios = require('axios');
const {
  convertCurrency,
  formatSuccess,
  formatError,
  getBaseUrl,
} = require('../src/client');
const { validateArgs } = require('../src/cli');

jest.mock('axios');

describe('CLI client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('successful conversion formatting', async () => {
    axios.post.mockResolvedValue({
      status: 200,
      data: {
        amount: 100,
        from_currency: 'USD',
        to_currency: 'INR',
        converted_amount: 8300,
      },
    });

    const result = await convertCurrency(100, 'USD', 'INR');
    expect(result.status).toBe(200);
    expect(formatSuccess(100, 'USD', 'INR', 8300)).toBe(
      'Converting 100 USD -> INR\nConverted Amount: 8300',
    );
  });

  test('validation failure for invalid amount', () => {
    const result = validateArgs(['-5', 'USD', 'INR']);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('greater than 0');
  });

  test('API unavailable scenario', async () => {
    axios.post.mockRejectedValue({ code: 'ECONNREFUSED', message: 'connect refused' });

    await expect(convertCurrency(100, 'USD', 'INR')).rejects.toMatchObject({
      code: 'ECONNREFUSED',
    });
    expect(formatError('Currency conversion service is unavailable')).toBe(
      'Error: Currency conversion service is unavailable',
    );
  });

  test('validation failure for unsupported currency', () => {
    const result = validateArgs(['100', 'USD', 'GBP']);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('unsupported to_currency');
  });

  test('uses default API base URL', () => {
    delete process.env.CONVERTER_API_URL;
    expect(getBaseUrl()).toBe('http://127.0.0.1:8000');
  });
});
