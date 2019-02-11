var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');

/* GET home page. */
router.get('/', function(req, res, next) {
  ApplicationModel.find({
        app_name: 'PUBG MOBILE'
      })
      .then(doc => {
          console.log(doc);
        res.json(doc)
      })
      .catch(err => {
        console.log(err)
      });
});

module.exports = router;
