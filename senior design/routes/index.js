var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');
const {ObjectId} = require('mongodb');

router.get('/stats', function (req, res, next) {
   ApplicationModel.collection.stats().then( doc => {
       res.json(doc);
   })
});


router.get('/applications', function (req, res, next) {
    appName = (req.query.appName != null) ? req.query.appName : "";
    packageName = (req.query.packageName != null) ? req.query.packageName : "";
    ApplicationModel.find({
        "app_name" : { "$regex": appName, "$options": "i" },
        "metadata.package" : { "$regex": packageName, "$options": "i" }
    }).lean().limit(40).then( doc =>{
        if(doc.length === 0){
            res.status(302).json({'error': 'This application is not available'})
        }
        res.json(doc);
    }).catch( err => {
        console.log(err);
    })
});

router.get('/applications/:id', function (req, res, next) {
    ApplicationModel.aggregate([
        {"$match": {"_id" : req.params.id} },
        {
            "$lookup":
                {
                    "from":"Versions",
                    "localField": "_id",
                    "foreignField": "app_id",
                    "as": "versions"
                }
        },
        {"$unwind" : "$versions"},
        {
            "$lookup":
                {
                    "from":"Reports",
                    "localField": "_id",
                    "foreignField": "app_id",
                    "as": "versions.report"
                }
        },
        {"$group" : {
                "_id":"$_id",
                "store_id" : {"$first" : "store_id" },
                "app_name" : {"$first" : "app_name" },
                "app_url" : {"$first" : "app_url" },
                "metadata" : {"$first" : "$metadata" },
                "versions" : {"$push" : "$versions"}
            }
        },
        {"$project": {"versions.apk_location":0, "reviews_path":0}}
    ]).then(doc => {
        res.json(doc);
    }).catch(err => {
        console.log(err);
    })
});

router.post('/applications', function (req, res, next) {
    let applications = req.body.appData;
    let response = [];

    applications.forEach( application => {
        let appVersion = application.appVersion;
        let packageName = application.packageName;
        let appStore = application.appStore;
        let appDoc = null , versionDoc = null;

        ApplicationModel.find({
            "metadata.package" : { "$regex": packageName, "$options": "i" },
            "store_id" : { "$regex": appStore, "$options": "i" }
        }).lean().limit(50).then( doc => {
            if(doc.length === 0){
                appDoc = {'error': 'This application is not available'};
            }
            appDoc = doc;
            VersionModel.find({
                app_id: appDoc._id,
                version: { "$regex": appVersion, "$options": "i" }
            }, {"apk_location":0}).lean().then(vDoc => {
                if(vDoc.length === 0){
                    versionDoc = {'error': 'This application is not available'};
                }
                versionDoc = vDoc;
                appDoc.version = versionDoc;
                response.concat(appDoc);
                if(response.length === applications.length){
                    res.json(response);
                }
            }).catch(err => {
                console.log(err);
            });
        }).catch( err => {
            console.log(err);
        });
    });
});

module.exports = router;
