// app.js
const express = require('express');
const app = express();
const port = 3000;

// Run static file
app.use(express.static('public'));

// Middleware to log requests
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Start the server
app.listen(port, () => {
  console.log(`Express app listening at http://localhost:${port}`);
});

