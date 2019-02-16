import React from 'react'
import DropDown from './DropDown'

import categoryOptions from '../dropdownOptions/categories'
import versionOptions from '../dropdownOptions/versions'
import dateOptions from '../dropdownOptions/date'
import keywordOptions from '../dropdownOptions/keywordOptions'

function DropDownOrganizer(props) {
  const groupStyles = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  }

  const groupBadgeStyles = {
    backgroundColor: '#EBECF0',
    borderRadius: '2em',
    color: '#172B4D',
    display: 'inline-block',
    fontSize: 12,
    fontWeight: 'normal',
    lineHeight: '1',
    minWidth: 1,
    padding: '0.16666666666667em 0.5em',
    textAlign: 'center'
  }

  const formatGroupLabel = data => (
    <div style={groupStyles}>
      <span>{data.label}</span>
      <span style={groupBadgeStyles}>{data.options.length}</span>
    </div>
  )

  return (
    <div>
      {/* <DropDown
        value={props.categoryValue}
        onChange={props.onCategoryChange}
        options={categoryOptions}
        formatGroupLabel={formatGroupLabel}
        placeholder={'Categories'}
      />
      <DropDown
        value={props.versionValue}
        onChange={props.onVersionChange}
        options={versionOptions}
        formatGroupLabel={formatGroupLabel}
        placeholder={'Versions'}
      />
      <DropDown
        value={props.dateValue}
        onChange={props.onDateChange}
        options={dateOptions}
        formatGroupLabel={formatGroupLabel}
        placeholder={'Date'}
      /> */}
      <DropDown
        defaultValue={keywordOptions[0].options[0]}
        onChange={props.onKeywordChange}
        options={keywordOptions}
        formatGroupLabel={formatGroupLabel}
      />
    </div>
  )
}

export default DropDownOrganizer
