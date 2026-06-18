const createApp = require('./app');

const PORT = process.env.PORT || 3001;
const app = createApp();

app.listen(PORT, () => {
  console.log(`Transaction API listening on http://127.0.0.1:${PORT}`);
});
