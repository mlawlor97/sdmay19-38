var express = require('express');
var router = express.Router();
let ApplicationModel = require('../models/application');
let VersionModel = require('../models/version');

router.get('/', function (req, res, next) {
    ApplicationModel.find({
        "app_name" : { "$regex": req.query.appName, "$options": "i" },
        "metadata.package" : { "$regex": req.query.packageName, "$options": "i" }
    }).lean().limit(20).then( doc =>{
        if(doc.length == 0){
            res.status(302).json({'error': 'This application is not available'})
        }
        res.json(doc);
    }).catch( err => {
        console.log(err);
    })
});

router



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
