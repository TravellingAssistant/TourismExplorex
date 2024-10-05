// server.js
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const User = require('./models/user');

const app = express();
const port = 3000;

mongoose.connect('mongodb://localhost:27017/collection', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', (req, res) => {
  // Serve your HTML signup page here
  res.sendFile(__dirname + '/index.html');
});

app.post('/signup', (req, res) => {
  // Handle the signup form submission here, save user data to MongoDB
  const { firstName, lastName, email, password } = req.body;

  const newUser = new User({ firstName, lastName, email, password });

  newUser.save((err) => {
    if (err) {
      console.error(err);
      res.redirect('/'); // Redirect back to the signup page in case of an error
    } else {
      res.redirect('/login.html'); // Redirect to the login page on success
    }
  });
});
app.get('/login.html', (req, res) => {
  // Serve your login.html page here
  res.sendFile(__dirname + '/login.html');
});

res.redirect('/login.html');

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
