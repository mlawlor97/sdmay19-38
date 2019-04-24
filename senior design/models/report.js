let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let ObjectId = mongoose.Schema.Types.ObjectId;

let ReportSchema = new Schema ({
    versions: [ObjectId],
    sha : {},
    report : {}
}, { versionKey: false });

module.exports = mongoose.model('Report', ReportSchema, 'Reports');
