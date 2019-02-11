var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');

/* GET home page. */
router.get('/', function (req, res, next) {
    ApplicationModel.find({
        app_name: req.query.keyword
    }).then(doc => {
        doc.forEach(function (application) {
            VersionModel.find({
                app_id: application._id
            }).then(vDoc => {
                application.versions = vDoc;
            }).catch(err => {
                console.log(err);
            })
        });
        res.json(doc)
    }).catch(err => {
        console.log(err)
    });
});

module.exports = router;
