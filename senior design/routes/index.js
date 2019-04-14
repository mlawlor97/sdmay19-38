var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');
let ReportModel = require('../models/report');
const {ObjectId} = require('mongodb');

router.get('/stats', function (req, res, next) {
    let response = {};
    let done = 0;
    ApplicationModel.collection.stats().then( doc => {
       response.applications = doc.count;
       done += 1;
        if(done === 3){
            res.json(response)
        }
    });
    VersionModel.collection.stats().then(doc => {
        response.versions = doc.count;
        done += 1;
        if(done === 3){
            res.json(response)
        }
    });
    ApplicationModel.aggregate([
        {"$group" : { "_id" : "$store_id", "count" : {"$sum" : 1}}}
    ]).then(doc => {
        response.stores = doc;
        done += 1;
        if(done === 3){
            res.json(response)
        }
    })
});


router.get('/applications', function (req, res, next) {
    appName = (req.query.appName != null) ? req.query.appName : "";
    packageName = (req.query.packageName != null) ? req.query.packageName : "";
    ApplicationModel.find({
        "app_name" : { "$regex": appName, "$options": "i" },
        "metadata.package" : { "$regex": packageName, "$options": "i" }
    }).lean().limit(50).then( doc =>{
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
        {"$match": {"_id" : ObjectId(req.params.id)} },
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
                    "localField": "versions._id",
                    "foreignField": "versions",
                    "as": "versions.report"
                }
        },
        {"$group" : {
                "_id":"$_id",
                "store_id" : {"$first" : "$store_id" },
                "app_name" : {"$first" : "$app_name" },
                "app_url" : {"$first" : "$app_url" },
                "metadata" : {"$first" : "$metadata" },
                "versions" : {"$push" : "$versions" }
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

        ApplicationModel.findOne({
            "metadata.package" : { "$regex": packageName, "$options": "i" },
            "store_id" : { "$regex": appStore, "$options": "i" }
        }).lean().limit(50).then( doc => {
            if(doc.length === 0){
                appDoc = {'error': 'This application is not available'};
            }
            appDoc = doc;
            VersionModel.find({
                app_id: ObjectId(appDoc._id),
                version: { "$regex": appVersion, "$options": "i" }
            }, {"apk_location":0}).lean().then(vDoc => {
                if(vDoc.length === 0){
                    versionDoc = {'error': 'This application is not available'};
                }
                versionDoc = vDoc;
                appDoc.version = versionDoc;
                response.push(appDoc);
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


router.post('/report', function(req, res, next) {
    let reportReq  = req.body.report;
    let sha = req.body.sha; // TODO: CHANGE THIS QUERY
    VersionModel.find({
        "app_name" : sha
    }).then( doc => {
        let versionIds = doc.map(version => version._id);
        let report = new ReportModel({
            'versions' : versionIds,
            'report' : reportReq
        });

        report.save().then( doc => {
            res.json({'response' : 'Successfully added report document'});
        }).catch( err => {
            console.log(err);
        });
    }).catch( err => {
        console.log(err);
    });
});

module.exports = router;
