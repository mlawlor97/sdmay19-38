var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');

/* GET home page. */
router.get('/', function (req, res, next) {
    ApplicationModel.find({
        app_name: req.query.keyword
    }).lean().then( doc =>{
        getVersions(doc).then( applications => {
            res.json(applications)
        });
    }).catch( err => {
        console.log(err);
    })
});

function getVersions(applications) {
    return new Promise(function (resolve, reject){
        for(let i = 0; i < applications.length; i++) {
            VersionModel.find({
                app_id: applications[i]._id
            }).then(vDoc => {
                applications[i].versions = vDoc;
            }).catch(err => {
                console.log(err);
            })
        }
        resolve(applications)
    })
}

module.exports = router;
