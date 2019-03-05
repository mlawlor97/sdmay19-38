import React from 'react'

function SearchBar(props) {
  return (
    <div id="search-bar">
      <form onSubmit={props.onSubmit}>
        <label>
          Keyword:
          <input type="text" value={props.value} onChange={props.onChange} />
        </label>
        <input type="submit" value="Submit" />
      </form>
    </div>
  )
}

export default SearchBar
