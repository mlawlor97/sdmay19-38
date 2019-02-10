var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');

/* GET home page. */
router.get('/', function(req, res, next) {
  ApplicationModel.find({
        name: req.body.name
      })
      .then(doc => {
        res.json(doc)
      })
      .catch(err => {
        console.log(err)
      });
});

module.exports = router;
