let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let ObjectId = mongoose.Schema.Types.ObjectId;

let ReportSchema = new Schema ({
    versions: [ObjectId],
    sha : {
        sha1 : String,
        sha256 : String,
        md5 : String
    },
    report : {}
}, { versionKey: false });

module.exports = mongoose.model('Report', ReportSchema, 'Reports');
