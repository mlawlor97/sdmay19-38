import React from 'react'
import DropDown from './DropDown'

import categoryOptions from '../dropdownOptions/categories'
import versionOptions from '../dropdownOptions/versions'

class DropDownOrganizer extends React.Component {
  constructor(props) {
    super(props)
    this.state = { selectedCategoryOption: null, selectedVersionOption: null }
    this.handleCategoryChange = this.handleCategoryChange.bind(this)
    this.handleVersionChange = this.handleVersionChange.bind(this)
  }

  handleCategoryChange(selectedOption) {
    this.setState({ selectedCategoryOption: selectedOption }, () =>
      console.log(
        `Categroy option selected:`,
        this.state.selectedCategoryOption
      )
    )
  }

  handleVersionChange(selectedOption) {
    this.setState({ selectedVersionOption: selectedOption }, () =>
      console.log(`Version option selected:`, this.state.selectedVersionOption)
    )
  }

  render() {
    const { selectedCategoryOption, selectedVersionOption } = this.state

    return (
      <div>
        <DropDown
          value={selectedCategoryOption}
          onChange={this.handleCategoryChange}
          options={categoryOptions}
          placeholder={'Categories'}
        />
        <DropDown
          value={selectedVersionOption}
          onChange={this.handleVersionChange}
          options={versionOptions}
          placeholder={'Versions'}
        />
      </div>
    )
  }
}

export default DropDownOrganizer
