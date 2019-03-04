var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');
const {ObjectId} = require('mongodb');

router.get('/applications', function (req, res, next) {
    appName = (req.query.appName != null) ? req.query.appName : "";
    packageName = (req.query.packageName != null) ? req.query.packageName : "";
    ApplicationModel.find({
        "app_name" : { "$regex": appName, "$options": "i" },
        "metadata.package" : { "$regex": packageName, "$options": "i" }
    }).lean().limit(40).then( doc =>{
        if(doc.length == 0){
            res.status(302).json({'error': 'This application is not available'})
        }
        res.json(doc);
    }).catch( err => {
        console.log(err);
    })
});

router.get('/applications/:id', function (req, res, next) {
    ApplicationModel.aggregate([
        {"$match": {"_id" : ObjectId(req.params.id)} },
        {
            "$lookup":
                {
                    "from":"Versions",
                    "localField": "_id",
                    "foreignField": "app_id",
                    "as": "versions"
                }
        }
    ]).then(doc => {
        res.json(doc);
    }).catch(err => {
        console.log(err);
    })
});

function getVersions(applications) {
    return new Promise(function (resolve, reject){
        let j = 0;
	    for(let i = 0; i < applications.length; i++) {
            VersionModel.find({
                app_id: applications[i]._id
            }).then(vDoc => {
                applications[i].versions = vDoc;
		j = j + 1;
		    
		    if( j == applications.length){
			resolve(applications);
		}
            }).catch(err => {
                console.log(err);
            })
        }
    })
}

module.exports = router;
