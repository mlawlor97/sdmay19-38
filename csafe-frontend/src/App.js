import React, { Component } from 'react'
//import './CSS/App.css'

import SearchBar from './components/SearchBar'
import Table from './components/Table'
import DropDownOrganizer from './components/DropDownOrganizer'

import versioncompare from './components/versionCompare'

const axios = require('axios')
const semver = require('semver')
const defaultColumns = [
  {
    Header: 'Store',
    accessor: 'store_id'
  },
  {
    Header: 'App Name',
    accessor: 'app_name'
  },
  {
    Header: 'Developer',
    accessor: 'Developer'
  },
  {
    Header: 'Package',
    accessor: 'Package'
  },
  {
    Header: 'Category',
    accessor: 'Category'
  },
  {
    Header: 'Version',
    accessor: 'version'
  }
]

const clickedColumns = [
  {
    Header: 'Store',
    accessor: 'store_id'
  },
  {
    Header: 'App Name',
    accessor: 'app_name'
  },
  {
    Header: 'Version',
    accessor: 'version'
  },
  {
    Header: 'File Type',
    accessor: 'Apk_Type' //Apk Type
  },
  {
    Header: 'File Size',
    accessor: 'File_Size' //File Size
  },
  {
    Header: 'Publish Date',
    accessor: 'Publish_Date' //Publish Date
  },
  {
    Header: 'Signature',
    accessor: 'Signature'
  },
  {
    Header: 'SHA',
    accessor: 'SHA'
  }
]

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      categoryFilter: null,
      versionFilter: null,
      dateFilter: null,
      tableData: [],
      response: null,
      click: false
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleCategoryChange = this.handleCategoryChange.bind(this)
    this.handleVersionChange = this.handleVersionChange.bind(this)
    this.handleDateChange = this.handleDateChange.bind(this)
    this.versionCompare = this.versionCompare.bind(this)
  }

  versionCompare(v1, v2, options) {
    var lexicographical = options && options.lexicographical,
      zeroExtend = options && options.zeroExtend,
      v1parts = v1.split('.'),
      v2parts = v2.split('.')

    function isValidPart(x) {
      return (lexicographical ? /^\d+[A-Za-z]*$/ : /^\d+$/).test(x)
    }

    if (!v1parts.every(isValidPart) || !v2parts.every(isValidPart)) {
      return NaN
    }

    if (zeroExtend) {
      while (v1parts.length < v2parts.length) v1parts.push('0')
      while (v2parts.length < v1parts.length) v2parts.push('0')
    }

    if (!lexicographical) {
      v1parts = v1parts.map(Number)
      v2parts = v2parts.map(Number)
    }

    for (var i = 0; i < v1parts.length; ++i) {
      if (v2parts.length == i) {
        return 1
      }

      if (v1parts[i] == v2parts[i]) {
        continue
      } else if (v1parts[i] > v2parts[i]) {
        return 1
      } else {
        return -1
      }
    }

    if (v1parts.length != v2parts.length) {
      return -1
    }

    return 0
  }

  onKeywordChange(event) {
    this.setState({ keyword: event.target.value })
  }

  handleCategoryChange(selectedOption) {
    this.setState({ categoryFilter: selectedOption })
  }

  handleVersionChange(selectedOption) {
    this.setState({ versionFilter: selectedOption })
  }

  handleDateChange(selectedOption) {
    this.setState({ dateFilter: selectedOption })
  }

  onSubmit(event) {
    event.preventDefault()
    if (this.state.keyword && this.state.versionFilter) {
      //"SOOOOOO GROSS" - Matt
      // Turn into function and import
      const dataArray = []
      this.state.versionFilter.forEach(filter => {
        this.state.response.forEach(element => {
          element.versions.forEach(version => {
            if (filter.value === '1') {
              const compare = versioncompare('1.0.0', version.version)
              if (compare) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                dataArray.push(dataObj)
              }
            }

            if (filter.value === '1_2') {
              const lessThan = versioncompare('2.0.1', version.version)
              const greaterThan = versioncompare('1.0.0', version.version)
              if (lessThan && !greaterThan) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                dataArray.push(dataObj)
              }
            }

            if (filter.value === '2_3') {
              const lessThan = versioncompare('3.0.1', version.version)
              const greaterThan = versioncompare('2.0.0', version.version)
              if (lessThan && !greaterThan) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                dataArray.push(dataObj)
              }
            }

            if (filter.value === '3_4') {
              const lessThan = versioncompare('4.0.1', version.version)
              const greaterThan = versioncompare('3.0.0', version.version)
              if (lessThan && !greaterThan) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                dataArray.push(dataObj)
              }
            }

            if (filter.value === '4_5') {
              const lessThan = versioncompare('5.0.1', version.version)
              const greaterThan = versioncompare('4.0.0', version.version)
              if (lessThan && !greaterThan) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                dataArray.push(dataObj)
              }
            }

            if (filter.value === '5+') {
              const compare = versioncompare('5.0.1', version.version)
              if (compare) {
                // add to data
                const dataObj = {
                  store_id: version['store_id'],
                  app_name: element['app_name'],
                  version: version['version'],
                  Apk_Type: version.metadata['Apk Type'],
                  File_Size: version.metadata['File Size'],
                  Publish_Date: version.metadata['Publish Date'],
                  Signature: version.metadata['Signature'],
                  SHA: version.metadata['SHA']
                }

                console.log(dataObj)

                dataArray.push(dataObj)
              }
            }
          })
        })
      })

      this.setState({ tableData: dataArray })
    } else {
      axios
        .get('http://sdmay19-18-windows.ece.iastate.edu:3000/', {
          params: {
            keyword: this.state.keyword
          }
        })
        .then(res => {
          const dataArray = []
          res.data.forEach(element => {
            element.versions.forEach(version => {
              const dataObj = {
                store_id: element['store_id'],
                app_name: element['app_name'],
                Developer: element.metadata['Developer'],
                Package: element.metadata['Package'],
                Category: element.metadata['Category'],
                version: version['version']
                // Apk_Type: version.metadata['Apk Type'],
                // File_Size: version.metadata['File Size'],
                // Publish_Date: version.metadata['Publish Date'],
                // Signature: version.metadata['Signature'],
                // SHA: version.metadata['SHA']
              }

              dataArray.push(dataObj)
            })
          })
          this.setState({ click: false })
          this.setState({ tableData: dataArray })
          this.setState({ response: res.data })
        })
    }
  }

  render() {
    const onRowClick = (state, rowInfo, column, instance) => {
      return {
        onClick: e => {
          // console.log('A Td Element was clicked!')
          // console.log('it produced this event:', e)
          // console.log('It was in this column:', column)
          //console.log('It was in this row:', rowInfo)
          // console.log('It was in this table instance:', instance)

          // Does not target specific app at the moment
          // Needs to be implemented later!!!
          if (this.state.response) {
            if (this.state.click) {
              const dataArray = []
              this.state.response.forEach(element => {
                element.versions.forEach(version => {
                  const dataObj = {
                    store_id: element['store_id'],
                    app_name: element['app_name'],
                    Developer: element.metadata['Developer'],
                    Package: element.metadata['Package'],
                    Category: element.metadata['Category'],
                    version: version['version']
                  }

                  dataArray.push(dataObj)
                })
              })

              this.setState({ tableData: dataArray })
            } else {
              const dataArray = []
              this.state.response.forEach(element => {
                element.versions.forEach(version => {
                  const dataObj = {
                    store_id: version['store_id'],
                    app_name: element['app_name'],
                    version: version['version'],
                    Apk_Type: version.metadata['Apk Type'],
                    File_Size: version.metadata['File Size'],
                    Publish_Date: version.metadata['Publish Date'],
                    Signature: version.metadata['Signature'],
                    SHA: version.metadata['SHA']
                  }

                  dataArray.push(dataObj)
                })
              })

              this.setState({ tableData: dataArray })
            }
          }

          this.setState({ click: !this.state.click })
        }
      }
    }

    let screen
    if (this.state.click) {
      screen = (
        <Table
          data={this.state.tableData}
          columns={clickedColumns}
          getTdProps={onRowClick}
        />
      )
    } else {
      screen = (
        <Table
          data={this.state.tableData}
          columns={defaultColumns}
          getTdProps={onRowClick}
        />
      )
    }

    return (
      <div className="App">
        <header className="App-header">
          <SearchBar
            onSubmit={this.onSubmit}
            value={this.state.keyword}
            onChange={this.onKeywordChange}
          />
          <DropDownOrganizer
            categoryValue={this.state.categoryFilter}
            versionValue={this.state.versionFilter}
            dateValue={this.state.dateFilter}
            onCategoryChange={this.handleCategoryChange}
            onVersionChange={this.handleVersionChange}
            onDateChange={this.handleDateChange}
          />
          {screen}
        </header>
      </div>
    )
  }
}

export default App
