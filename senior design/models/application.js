let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let MetadataSchema = new Schema ({
    name: String,
    developer: String,
    package: String,
    category: String,
    description: String,
    rating: Number,
    Tags: [String]
});

let ApplicationSchema = new Schema ({
    app_name: String,
    store_id: String,
    metadata : MetadataSchema
});

module.exports = mongoose.model('Application', ApplicationSchema, 'Applications');
