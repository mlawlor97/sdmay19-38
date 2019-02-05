import React, { Component } from 'react'
import SearchBar from './components/SearchBar'
import './App.css'

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <SearchBar />
        </header>
      </div>
    )
  }
}

export default App
