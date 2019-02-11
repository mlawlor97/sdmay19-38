let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let MetadataSchema = new Schema ({
    apk_type: String,
    file_size: String,
    requirements: String,
    publish_date: String,
    patch_notes: String,
    signature: String,
    sha: String
});

let ObjectId = mongoose.Schema.Types.ObjectId;

let VersionSchema = new Schema ({
    app_id: ObjectId,
    store_id: String,
    version: String,
    metadata : MetadataSchema
});

module.exports = mongoose.model('Version', VersionSchema, 'Versions');
