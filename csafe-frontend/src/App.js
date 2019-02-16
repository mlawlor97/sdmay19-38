import React, { Component } from 'react'
//import './CSS/App.css'

import SearchBar from './components/SearchBar'
import Table from './components/Table'
import DropDownOrganizer from './components/DropDownOrganizer'

const axios = require('axios')
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
    Header: 'URL',
    accessor: 'url'
  },
  {
    Header: 'Download',
    accessor: 'download'
  }
]

const clickedColumns = [
  {
    Header: 'App Package Name',
    accessor: 'app_package_name'
  },
  {
    Header: 'Version',
    accessor: 'version'
  },
  {
    Header: 'Finish Timestamp',
    accessor: 'finish_timestamp'
  },
  {
    Header: 'File Path',
    accessor: 'path'
  },
  {
    Header: 'Evidence Types',
    accessor: 'evidence_types'
  }
]

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      categoryFilter: null,
      versionFilter: null,
      keywordFilter: 'appName',
      dateFilter: null,
      tableData: [],
      response: null,
      click: false
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleCategoryChange = this.handleCategoryChange.bind(this)
    this.handleVersionChange = this.handleVersionChange.bind(this)
    this.handleKeywordTypeChange = this.handleKeywordTypeChange.bind(this)
    this.handleDateChange = this.handleDateChange.bind(this)
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

  handleKeywordTypeChange(selectedOption) {
    this.setState({ keywordFilter: selectedOption.value })
  }

  onSubmit(event) {
    event.preventDefault()
    if (this.state.keywordFilter === 'appName') {
      axios
        .get('http://sdmay19-18-windows.ece.iastate.edu:3000/appName/', {
          params: {
            keyword: this.state.keyword
          }
        })
        .then(res => {
          const dataArray = []
          res.data.forEach(element => {
            const dataObj = {
              store_id: element['store_id'],
              app_name: element['app_name'],
              Developer: element.metadata['developer'],
              Package: element.metadata['package'],
              Category: element.metadata['category'],
              url: element['app_url'],
              download: 'Download Here'
            }

            dataArray.push(dataObj)
          })
          this.setState({ click: false })
          this.setState({ tableData: dataArray })
          this.setState({ response: res.data })
        })
        .catch(err => {
          console.log(err)
          this.setState({ tableData: [] })
        })
    } else if (this.state.keywordFilter === 'packageName') {
      axios
        .get('http://sdmay19-18-windows.ece.iastate.edu:3000/packageName/', {
          params: {
            keyword: this.state.keyword
          }
        })
        .then(res => {
          const dataArray = []
          res.data.forEach(element => {
            const dataObj = {
              store_id: element['store_id'],
              app_name: element['app_name'],
              Developer: element.metadata['developer'],
              Package: element.metadata['package'],
              Category: element.metadata['category'],
              url: element['app_url'],
              download: 'Download Here'
            }

            dataArray.push(dataObj)
          })
          this.setState({ click: false })
          this.setState({ tableData: dataArray })
          this.setState({ response: res.data })
        })
        .catch(err => {
          console.log(err)
          this.setState({ tableData: [] })
        })
    }
  }

  render() {
    const onRowClick = (state, rowInfo, column, instance) => {
      return {
        onClick: e => {
          if (this.state.response) {
            if (this.state.click) {
              const dataArray = []
              this.state.response.forEach(element => {
                const dataObj = {
                  store_id: element['store_id'],
                  app_name: element['app_name'],
                  Developer: element.metadata['developer'],
                  Package: element.metadata['package'],
                  Category: element.metadata['category'],
                  url: element['app_url'],
                  download: 'Download Here'
                }

                dataArray.push(dataObj)
              })

              this.setState({ tableData: dataArray })
            } else {
              const found = []
              this.state.response.forEach((element, i) => {
                if (element.app_name === rowInfo.original.app_name) {
                  found.push(this.state.response[i])
                }
              })
              const dataArray = []
              if (found[0].versions[0].report) {
                found[0].versions[0].report.app_evidence[1].file_system.forEach(
                  element => {
                    const dataObj = {
                      app_package_name:
                        found[0].versions[0].report.app_package_name,
                      version: found[0].versions[0].report.version,
                      finish_timestamp:
                        found[0].versions[0].report.finish_timestamp,
                      path: element.path,
                      evidence_types: element.evidence_types[0]
                    }

                    dataArray.push(dataObj)
                  }
                )
              }
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
            // categoryValue={this.state.categoryFilter}
            // versionValue={this.state.versionFilter}
            // dateValue={this.state.dateFilter}
            // onCategoryChange={this.handleCategoryChange}
            // onVersionChange={this.handleVersionChange}
            // onDateChange={this.handleDateChange}
            onKeywordChange={this.handleKeywordTypeChange}
          />
          {screen}
        </header>
      </div>
    )
  }
}

export default App
