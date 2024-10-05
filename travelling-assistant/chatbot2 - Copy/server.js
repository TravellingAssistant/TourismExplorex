
const express = require('express');
const mongoose = require('mongoose');
const expressSession = require('express-session');
const bodyParser = require('body-parser');
const User = require('./models/user');

const app = express();
const port = 3000;

mongoose.connect('mongodb://localhost:27017/collection', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

app.use(bodyParser.urlencoded({ extended: false }));

app.use(
  expressSession({
    secret: 'your-secret-key', // Change this to a strong, unique secret
    resave: false,
    saveUninitialized: true,
  })
);

app.get('/', (req, res) => {
  // Serve your HTML login page here
  res.sendFile(__dirname + '/login.html');
});
app.post('/login', (req, res) => {
  const { email, password } = req.body;

  User.findOne({ email, password }, (err, user) => {
    if (err || !user) {
      console.error('Authentication failed.');
      res.redirect('/'); // Redirect to login page on failure
    } else {
      // Store user information in the session
      req.session.user = user;
      res.redirect('/dashboard.html'); // Redirect to the dashboard on success
    }
  });
});
app.get('/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
