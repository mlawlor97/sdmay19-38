function generateVersionOptions(objectArray) {
  const versions = []
  const versionObj = {}
  versionObj['label'] = 'Versions'
  const options = objectArray.map(obj => {
    return { value: obj['version'], label: obj['version'], group: 'Versions' }
  })

  versionObj['options'] = options
  versions.push(versionObj)

  return versions
}

export default generateVersionOptions
