// const versionOptions = [
//   {
//     label: 'Versions',
//     options: [
//       { value: 'all', label: 'All', group: 'Versions' },
//       { value: '1', label: 'Below 1.0.0', group: 'Versions' },
//       { value: '1_2', label: '1.0.0 - 2.0.0', group: 'Versions' },
//       { value: '2_3', label: '2.0.0 - 3.0.0', group: 'Versions' },
//       { value: '3_4', label: '3.0.0 - 4.0.0', group: 'Versions' },
//       { value: '4_5', label: '4.0.0 - 5.0.0', group: 'Versions' },
//       { value: '5+', label: '5.0.0 +', group: 'Versions' }
//     ]
//   }
// ]

// export default versionOptions

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
