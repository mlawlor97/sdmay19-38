var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');

/* GET home page. */
router.get('/', function(req, res, next) {
  console.log(req.query.keyword);
	ApplicationModel.find({
        app_name: req.query.keyword
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
