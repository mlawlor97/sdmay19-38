function versionCompare(v1, v2) {
  let v1Array = v1.split('.')
  let v2Array = v2.split('.')

  if (v2Array.length > 3) {
    v2Array.pop()
  }

  for (var i = 0; i < v1Array.length; ++i) {
    if (v2Array.length == i) {
      return 1
    }

    if (v1Array[i] == v2Array[i]) {
      continue
    } else if (v1Array[i] > v2Array[i]) {
      return 1
    } else {
      return -1
    }
  }
}

export default versionCompare
