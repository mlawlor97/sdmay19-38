import React, { Component } from 'react'
import { BrowserRouter as Router, Link, Route } from 'react-router-dom'
import './CSS/App.css'

import SearchBar from './components/SearchBar'
import DropDown from './components/DropDown'
import ScrollView from './components/ScrollView'
import ScrollElement from './components/ScrollElement'
import keywordOptions from './dropdownOptions/keywordOptions'
import generateVersionOptions from './dropdownOptions/versions'
import ReactFileReader from 'react-file-reader'

const axios = require('axios')

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      keywordFilter: 'appName',
      versions: [],
      response: [],
      newData: [],
      displayVersion: [],
      evidenceData: [],
      refresh: true,
      stats: '',
      responseVersions: []
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleKeywordTypeChange = this.handleKeywordTypeChange.bind(this)
    this.onAppClick = this.onAppClick.bind(this)
    this.handleVersionChange = this.handleVersionChange.bind(this)
    this.handleFiles = this.handleFiles.bind(this)
    this.grabStats = this.grabStats.bind(this)
    this.downloadAPK = this.downloadAPK.bind(this)
  }

  downloadAPK() {
    let captainFalcon = ''
    this.state.responseVersions.forEach(version => {
      if (version.version === this.state.displayVersion[0].version) {
        captainFalcon = version._id
      }
    })
    setTimeout(() => {
      const response = {
        file: '35.225.241.144:3000/api/v1/download/' + captainFalcon
      }

      window.open(response.file)
    }, 100)
  }

  grabStats() {
    axios
      .get('35.225.241.144:3000/api/v1/stats')
      .then(res => {
        const statView = (
          <div className="stats">
            <ul>
              <b>{'applications'}</b> {': ' + res.data['applications']}
            </ul>
            <ul>
              <b>{'versions'}</b> {': ' + res.data['versions']}
            </ul>
            <ul>
              <b>{'Store'}</b> {': ' + res.data.stores[0]._id}
              <br />
              <b>{'Number of Apps'}</b> {': ' + res.data.stores[0].count}
            </ul>
            <ul>
              <b>{'Store'}</b> {': ' + res.data.stores[1]._id}
              <br />
              <b>{'Number of Apps'}</b> {': ' + res.data.stores[1].count}
            </ul>
          </div>
        )
        this.setState({ stats: statView })
      })
      .catch(err => {
        console.log(err)
      })
  }

  handleFiles(files) {
    var reader = new FileReader()
    reader.onload = e => {
      // Use reader.result
      // csv format: package name, app store, version
      const input = reader.result.split(',')
      const postBody = []
      for (let i = 0; i < input.length; i += 3) {
        const appData = {
          packageName: input[i],
          appStore: input[i + 1],
          appVersion: input[i + 2]
        }

        postBody.push(appData)
      }
      axios
        .post('35.225.241.144:3000/api/v1/applications/', {
          appData: postBody
        })
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
          console.log('error')
          console.log(err)
        })
    }
    reader.readAsText(files[0])
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
    this.setState({ newData: [] })
    this.setState({ displayVersion: [] })
    this.setState({ versions: [] })
    this.setState({ evidenceData: [] })
    const dataArray = []
    axios
      .get('35.225.241.144:3000/api/v1/applications/' + event)
      .then(res => {
        this.setState({ responseVersions: res.data[0].versions })
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

          if (obj.metadata.permissions !== undefined) {
            obj.metadata.permissions.forEach(permission => {
              dataObj['permissions'] += '\n' + permission
            })
          }

          if (obj.metadata['apk_type'] === undefined) {
            dataObj['apk_type'] = 'APK'
          }

          dataArray.push(dataObj)
        })

        if (boy.versions[0].report.length !== 0) {
          const reportArray = []
          const reportObj = boy.versions[0].report

          const fileSystemArray = []
          const networkArray = []
          if (reportObj[0].report.app_evidence[1].file_system.length) {
            reportObj[0].report.app_evidence[1].file_system.forEach(element => {
              const fileSystemObj = {
                path: element.path,
                evidence_types: element.evidence_types
              }

              fileSystemArray.push(fileSystemObj)
            })
          }

          if (reportObj[0].report.app_evidence[2].network.length) {
            reportObj[0].report.app_evidence[2].network.forEach(element => {
              const networkObj = {
                path: element.path,
                evidence_types: element.evidence_types
              }

              networkArray.push(networkObj)
            })
          }

          fileSystemArray.forEach((e, i) => {
            const dataObj = {
              app_package_name: boy.metadata['package'],
              version: reportObj.version
            }
            if (fileSystemArray[i]) {
              dataObj['file path'] = fileSystemArray[i].path
              dataObj['file evidence types'] = fileSystemArray[
                i
              ].evidence_types.toString()
            }

            if (networkArray[i]) {
              dataObj['network address'] = fileSystemArray[i].path
              dataObj['network evidence types'] = fileSystemArray[
                i
              ].evidence_types.toString()
            }

            reportArray.push(dataObj)
          })

          this.setState({ evidenceData: reportArray })
        } else {
          this.setState({ evidenceData: [] })
        }

        const yeet = []
        yeet.push(dataArray[1])
        this.setState({ versions: generateVersionOptions(boy.versions) })
        this.setState({ newData: dataArray })
        this.setState({ displayVersion: yeet })
      })
      .catch(err => {
        console.log(err)
      })
  }

  onSubmit(event) {
    event.preventDefault()
    if (this.state.keywordFilter === 'appName') {
      axios
        .get('35.225.241.144:3000/api/v1/applications', {
          params: {
            appName: this.state.keyword
          }
        })
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
          this.setState({ refresh: false })
        })
        .catch(err => {
          this.setState({ response: [] })
        })
    } else if (this.state.keywordFilter === 'packageName') {
      axios
        .get('35.225.241.144:3000/api/v1/applications', {
          params: {
            packageName: this.state.keyword
          }
        })
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
          this.setState({ refresh: false })
        })
        .catch(err => {
          this.setState({ response: [] })
        })
    }
  }

  componentWillMount() {
    this.grabStats()
  }

  render() {
    const sView = (
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
                  <div className="item" onClick={() => this.onAppClick(app_id)}>
                    <Link className="routeLink" to={`/app/${app_id}`}>
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
                    </Link>
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
    )
    const screen = (
      <header className="App-header">
        <div className="gridwrapper">
          <div className="menu">
            <h1 id="header">Forensic Android App Database</h1>
            <div className="searchbar">
              <SearchBar
                onSubmit={this.onSubmit}
                value={this.state.keyword}
                onChange={this.onKeywordChange}
              />
            </div>
            <div className="filereader">
              <ReactFileReader
                handleFiles={this.handleFiles}
                fileTypes={['.csv', '.txt']}
              >
                <button className="btn">Upload</button>
              </ReactFileReader>
              {/* <span
                title={'CSV format is app package name, version, app store'}
              >
                !
              </span> */}
            </div>
            <div className="dropdown">
              <DropDown
                onKeywordChange={this.handleKeywordTypeChange}
                options={keywordOptions}
                defaultValue={keywordOptions[0].options[0]}
              />
            </div>
          </div>
          {this.state.refresh ? this.state.stats : sView}
        </div>
      </header>
    )

    const infoScreen = (
      <header className="App-header">
        <div className="gridwrapperInfo">
          <div className="menu">
            <h1 id="header">Forensic Android App Database</h1>
            <button onClick={this.downloadAPK}>Download APK</button>
            <DropDown
              onKeywordChange={this.handleVersionChange}
              options={this.state.versions}
              defaultValue={this.state.versions[0]}
            />
          </div>
          <div className="scrollerInfo">
            <ScrollView ref={scroller => (this._scroller = scroller)}>
              <div id="left">
                {this.state.displayVersion.map(obj => {
                  return (
                    <ScrollElement name={obj.app_name}>
                      <div className="itemInfo">
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
                {this.state.evidenceData.map(obj => {
                  return (
                    <ScrollElement name={obj.app_name}>
                      <div className="itemInfo">
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
          </div>
        </div>
      </header>
    )

    return (
      <Router>
        <div className="App">
          <Route exact={true} path="/" render={() => screen} />
          <Route path="/app/:app_id" render={() => infoScreen} />
        </div>
      </Router>
    )
  }
}

export default App
