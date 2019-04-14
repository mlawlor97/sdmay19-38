let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let ObjectId = mongoose.Schema.Types.ObjectId;

let ReportSchema = new Schema ({
    versions: [ObjectId],
    report : {}
});

module.exports = mongoose.model('Version', ReportSchema, 'Versions');