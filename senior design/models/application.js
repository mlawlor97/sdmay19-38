let mongoose = require('mongoose');
let Schema = mongoose.Schema;

let MetadataSchema = new Schema ({
    name: String,
    developer: String,
    package: String,
    category: String,
    description: String,
    rating: Number,
    tags: [String]
});

let ApplicationSchema = new Schema ({
    name: String,
    store: String,
    metadata : MetadataSchema
});

module.exports = mongoose.model('Application', ApplicationSchema);