import React from 'react'
import Select from 'react-select'

function DropDown(props) {
  return (
    <Select
      value={props.value}
      onChange={props.onChange}
      options={props.options}
      placeholder={props.placeholder}
      formatGroupLabel={props.formatGroupLabel}
      isClearable={true}
      isSearchable={true}
      isMulti={true}
    />
  )
}

export default DropDown
