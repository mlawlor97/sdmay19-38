import React from 'react'
import Select from 'react-select'

function DropDown(props) {
  return (
    <Select
      value={props.value}
      onChange={props.onChange}
      options={props.options}
      placeholder={props.placeholder}
      isClearable={true}
      isSearchable={true}
    />
  )
}

export default DropDown
