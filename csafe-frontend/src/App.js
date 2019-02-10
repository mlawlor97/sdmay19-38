import React, { Component } from 'react'
//import './CSS/App.css'

import SearchBar from './components/SearchBar'
import Table from './components/Table'
import DropDownOrganizer from './components/DropDownOrganizer'

const axios = require('axios')

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      keyword: '',
      filters: {
        category: null,
        version: null,
        date: null
      }
    }

    this.onKeywordChange = this.onKeywordChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
  }

  onKeywordChange(event) {
    this.setState({ keyword: event.target.value })
  }

  onSubmit(event) {
    // Send request to server side
    event.preventDefault()
    // axios
    //   .post('<endpoint_here>', {
    //     keyword: this.state.value
    //   })
    //   .then(res => {
    //     console.log(`Keyword: ${this.state.value} sent`)
    //     getData(res)
    //   })
    console.log('A keyword was submitted: ' + this.state.keyword)
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <SearchBar
            onSubmit={this.onSubmit}
            value={this.state.keyword}
            onChange={this.onKeywordChange}
          />
          <DropDownOrganizer filters={this.state.filters} />
        </header>
      </div>
    )
  }
}

export default App
