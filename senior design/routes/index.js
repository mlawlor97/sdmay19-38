var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');

/* GET home page. */
router.get('/', function (req, res, next) {
    ApplicationModel.find({
        "app_name" : { "$regex": req.query.keyword, "$options": "i" }
    }).lean().then( doc =>{
        if(doc.length == 0){
            res.status(302).json({'error': req.query.keyword + ' is available'})
        }
        getVersions(doc).then( applications => {
		res.json(applications);
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
		if( i == applications.length-1){
			resolve(applications);
		}
            }).catch(err => {
                console.log(err);
            })
        }
    })
}

module.exports = router;
