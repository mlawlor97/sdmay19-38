import React, { Component } from 'react'
import './CSS/App.css'

import SearchBar from './components/SearchBar'
import DropDownOrganizer from './components/DropDownOrganizer'
import ScrollView from './components/ScrollView'
import ScrollElement from './components/ScrollElement'
import keywordOptions from './dropdownOptions/keywordOptions'
import generateVersionOptions from './dropdownOptions/versions'

const axios = require('axios')

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      keywordFilter: 'appName',
      versions: [],
      response: [],
      changeScreen: false,
      newData: [],
      displayVersion: [],
      tempEvidenceData: []
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleKeywordTypeChange = this.handleKeywordTypeChange.bind(this)
    this.onAppClick = this.onAppClick.bind(this)
    this.goBack = this.goBack.bind(this)
    this.handleVersionChange = this.handleVersionChange.bind(this)
  }

  goBack(event) {
    this.setState({ changeScreen: false })
    this.setState({ newData: [] })
    this.setState({ displayVersion: [] })
    this.setState({ versions: [] })
  }

  onKeywordChange(event) {
    this.setState({ keyword: event.target.value })
  }

  handleKeywordTypeChange(selectedOption) {
    this.setState({ keywordFilter: selectedOption.value })
  }

  handleVersionChange(selectedOption) {
    const versionData = this.state.newData.filter(
      obj => obj['version'] === selectedOption.value
    )

    this.setState({ displayVersion: versionData })
  }

  onAppClick(event) {
    const dataArray = []
    this.setState({ changeScreen: true })
    axios
      .get(
        'http://sdmay19-18-windows.ece.iastate.edu:3000/api/v1/applications/' +
          event
      )
      .then(res => {
        const boy = res.data[0]

        const dataObj = {
          store_id: boy['store_id'],
          app_name: boy['app_name'],
          Developer: boy.metadata['developer'],
          Package: boy.metadata['package'],
          Category: boy.metadata['category'],
          url: boy['app_url']
        }

        dataArray.push(dataObj)

        boy.versions.forEach(obj => {
          const dataObj = {
            store_id: obj['store_id'],
            app_name: obj['app_name'],
            version: obj['version'],
            apk_type: obj.metadata['apk_type'],
            file_size: obj.metadata['file_size'],
            requirements: obj.metadata['requirements'],
            publish_date: obj.metadata['publish_date'],
            patch_notes: obj.metadata['patch_notes'],
            signature: obj.metadata['signature'],
            sha1: obj.metadata['sha1']
          }

          dataArray.push(dataObj)
        })

        this.setState({ versions: generateVersionOptions(boy.versions) })
        this.setState({ newData: dataArray })
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
    const beegYosh = {
      app_package_name: 'WIP',
      version: 'WIP',
      file_path: 'WIP',
      file_evidence_types: 'WIP',
      network_path: 'WIP',
      network_evidence_path: 'WIP'
    }
    const stop = []
    stop.push(beegYosh)

    const screen = (
      <header className="App-header">
        <div className="menu">
          <h1 id="header">Forensic Android App Database</h1>
          <SearchBar
            onSubmit={this.onSubmit}
            value={this.state.keyword}
            onChange={this.onKeywordChange}
          />
          <DropDownOrganizer
            onKeywordChange={this.handleKeywordTypeChange}
            options={keywordOptions}
            defaultValue={keywordOptions[0].options[0]}
          />
        </div>
        <ScrollView ref={scroller => (this._scroller = scroller)}>
          <div className="scroller">
            {this.state.response.map(
              ({
                app_name,
                Developer,
                Package,
                Category,
                url,
                app_id,
                store_id
              }) => {
                return (
                  <ScrollElement name={app_name}>
                    <div
                      className="item"
                      onClick={() => this.onAppClick(app_id)}
                    >
                      <ul>
                        <b>{'App Name'}</b>
                        {': ' + app_name}
                      </ul>
                      <ul>
                        <b>{'Developer'}</b>
                        {': ' + Developer}
                      </ul>
                      <ul>
                        <b>{'Package'}</b>
                        {': ' + Package}
                      </ul>
                      <ul>
                        <b>{'Store'}</b>
                        {': ' + store_id}{' '}
                      </ul>
                      <ul>
                        <b>{'Category'}</b>
                        {': ' + Category}
                      </ul>
                      <ul>
                        <b>{'URL: '}</b>
                        <a href={url}>{url}</a>
                      </ul>
                    </div>
                  </ScrollElement>
                )
              }
            )}
          </div>
        </ScrollView>
      </header>
    )

    const infoScreen = (
      <header className="App-header">
        <div className="menu">
          <h1 id="header">Forensic Android App Database</h1>
          <button onClick={this.goBack}>Go Back</button>
          <DropDownOrganizer
            onKeywordChange={this.handleVersionChange}
            options={this.state.versions}
            defaultValue={this.state.versions[0]}
          />
        </div>
        <div>
          <ScrollView ref={scroller => (this._scroller = scroller)}>
            <div id="left">
              {this.state.displayVersion.map(obj => {
                return (
                  <ScrollElement name={obj.app_name}>
                    <div className="item">
                      {Object.keys(obj).map(key => {
                        return (
                          <ul>
                            <b>{key}</b> {': ' + obj[key]}
                          </ul>
                        )
                      })}
                    </div>
                  </ScrollElement>
                )
              })}
            </div>
          </ScrollView>
          <ScrollView ref={scroller => (this._scroller = scroller)}>
            <div id="right">
              {stop.map(obj => {
                return (
                  <ScrollElement name={obj.app_name}>
                    <div className="item">
                      {Object.keys(obj).map(key => {
                        return <ul>{key + ': ' + obj[key]}</ul>
                      })}
                    </div>
                  </ScrollElement>
                )
              })}
            </div>
          </ScrollView>
        </div>
      </header>
    )

    return (
      <div className="App">{this.state.changeScreen ? infoScreen : screen}</div>
    )
  }
}

export default App
