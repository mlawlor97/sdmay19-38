import React from 'react'

function SearchBar(props) {
  return (
    <form onSubmit={props.onSubmit}>
      <label>
        Keyword:
        <input type="text" value={props.value} onChange={props.onChange} />
      </label>
      <input type="submit" value="Submit" />
    </form>
  )
}

export default SearchBar
