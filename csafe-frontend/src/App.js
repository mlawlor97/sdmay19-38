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
