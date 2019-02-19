import React, { Component } from 'react'
import './CSS/App.css'

import SearchBar from './components/SearchBar'
import Table from './components/Table'
import DropDownOrganizer from './components/DropDownOrganizer'
import defaultColumns from './tableColumns/defaultColumns'
import clickedColumns from './tableColumns/clickedColumns'

const axios = require('axios')

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
      click: false,
      error: false
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
              url: element['app_url']
            }

            if (element.versions) {
              dataObj['Version'] = element.versions[0].version
            }

            dataArray.push(dataObj)
          })
          this.setState({ click: false })
          this.setState({ tableData: dataArray })
          this.setState({ response: res.data })
          this.setState({ error: false })
        })
        .catch(err => {
          this.setState({ error: true })
          this.setState({ tableData: [] })
          this.setState({ response: [] })
          this.setState({ click: false })
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
              url: element['app_url']
            }

            if (element.versions) {
              dataObj['Version'] = element.versions[0].version
            }

            dataArray.push(dataObj)
          })
          this.setState({ click: false })
          this.setState({ tableData: dataArray })
          this.setState({ response: res.data })
          this.setState({ error: false })
        })
        .catch(err => {
          this.setState({ error: true })
          this.setState({ tableData: [] })
          this.setState({ response: [] })
          this.setState({ click: false })
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
                  url: element['app_url']
                }

                if (element.versions) {
                  dataObj['Version'] = element.versions[0].version
                }

                dataArray.push(dataObj)
              })

              this.setState({ tableData: dataArray })
            } else {
              if (rowInfo) {
                const found = []
                this.state.response.forEach((element, i) => {
                  if (element.app_name === rowInfo.original.app_name) {
                    found.push(this.state.response[i])
                  }
                })
                const dataArray = []
                if (found[0].versions) {
                  if (found[0].versions[0].report) {
                    const app_package_name =
                      found[0].versions[0].report.app_package_name
                    const version = found[0].versions[0].version

                    const fileSystemArray = []
                    const networkArray = []
                    if (
                      found[0].versions[0].report.app_evidence[1].file_system
                        .length
                    ) {
                      found[0].versions[0].report.app_evidence[1].file_system.forEach(
                        element => {
                          const fileSystemObj = {
                            path: element.path,
                            evidence_types: element.evidence_types
                          }

                          fileSystemArray.push(fileSystemObj)
                        }
                      )
                    }

                    if (
                      found[0].versions[0].report.app_evidence[2].network.length
                    ) {
                      found[0].versions[0].report.app_evidence[2].network.forEach(
                        element => {
                          const networkObj = {
                            path: element.path,
                            evidence_types: element.evidence_types
                          }

                          networkArray.push(networkObj)
                        }
                      )
                    }

                    fileSystemArray.forEach((e, i) => {
                      const dataObj = {
                        app_package_name: app_package_name,
                        version: version
                      }
                      if (fileSystemArray[i]) {
                        dataObj['f_path'] = fileSystemArray[i].path
                        dataObj['f_evidence_types'] = fileSystemArray[
                          i
                        ].evidence_types.toString()
                      }

                      if (networkArray[i]) {
                        dataObj['n_path'] = fileSystemArray[i].path
                        dataObj['n_evidence_types'] = fileSystemArray[
                          i
                        ].evidence_types.toString()
                      }

                      dataArray.push(dataObj)
                    })
                  }
                }

                this.setState({ tableData: dataArray })
              } else {
                this.setState({ tableData: [] })
              }
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

    let errorScreen
    if (this.state.error) {
      errorScreen = (
        <div className="query">
          <form>
            <label>Keyword Not Found</label>
          </form>
        </div>
      )
    } else {
      errorScreen = <div />
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
          <div className="cell">{screen}</div>
          {errorScreen}
        </header>
      </div>
    )
  }
}

export default App
