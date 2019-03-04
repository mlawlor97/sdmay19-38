import React, { Component } from 'react'
import './CSS/App.css'

import SearchBar from './components/SearchBar'
import DropDownOrganizer from './components/DropDownOrganizer'
import ScrollView from './components/ScrollView'
import ScrollElement from './components/ScrollElement'

const axios = require('axios')

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      keywordFilter: 'appName',
      response: []
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleKeywordTypeChange = this.handleKeywordTypeChange.bind(this)
    this.onAppClick = this.onAppClick.bind(this)
  }

  onKeywordChange(event) {
    this.setState({ keyword: event.target.value })
  }

  handleKeywordTypeChange(selectedOption) {
    this.setState({ keywordFilter: selectedOption.value })
  }

  onAppClick(event) {
    console.log(event)
    axios
      .get(
        'http://sdmay19-18-windows.ece.iastate.edu:3000/api/v1/applications/' //app_id
      )
      .then(res => {
        //something
      })
      .catch(err => {
        //something else
      })
  }

  onSubmit(event) {
    event.preventDefault()
    if (this.state.keywordFilter === 'appName') {
      axios
        .get(
          'http://sdmay19-18-windows.ece.iastate.edu:3000/api/v1/applications',
          {
            params: {
              appName: this.state.keyword
            }
          }
        )
        .then(res => {
          const dataArray = []
          res.data.forEach(element => {
            const dataObj = {
              app_id: element['_id'],
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
          this.setState({ response: dataArray })
        })
        .catch(err => {
          this.setState({ response: [] })
        })
    } else if (this.state.keywordFilter === 'packageName') {
      axios
        .get(
          'http://sdmay19-18-windows.ece.iastate.edu:3000/api/v1/applications',
          {
            params: {
              packageName: this.state.keyword
            }
          }
        )
        .then(res => {
          const dataArray = []
          res.data.forEach(element => {
            const dataObj = {
              app_id: element['_id'],
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
          this.setState({ response: dataArray })
        })
        .catch(err => {
          this.setState({ response: [] })
        })
    }
  }

  render() {
    const screen = (
      <header className="App-header">
        <SearchBar
          onSubmit={this.onSubmit}
          value={this.state.keyword}
          onChange={this.onKeywordChange}
        />
        <DropDownOrganizer onKeywordChange={this.handleKeywordTypeChange} />
        <ScrollView ref={scroller => (this._scroller = scroller)}>
          <div className="scroller">
            {this.state.response.map(
              ({ app_name, Developer, Package, Category, url, app_id }) => {
                return (
                  <ScrollElement name={app_name}>
                    <div
                      className="item"
                      onClick={() => this.onAppClick(app_id)}
                    >
                      <ul>{'App Name: ' + app_name}</ul>
                      <ul>{'Developer: ' + Developer}</ul>
                      <ul>{'Package: ' + Package}</ul>
                      <ul>{'Category: ' + Category}</ul>
                      <ul>{'URL: ' + url}</ul>
                    </div>
                  </ScrollElement>
                )
              }
            )}
          </div>
        </ScrollView>
      </header>
    )

    return <div className="App">{screen}</div>
  }
}

export default App
