var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');

/* GET home page. */
router.get('/', function (req, res, next) {
    ApplicationModel.find({
        app_name: req.query.keyword
    }).lean().exec( function(err, doc){
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
    });
});

module.exports = router;
