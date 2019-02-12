import React from 'react'
import ReactTable from 'react-table'
import 'react-table/react-table.css'

function Table(props) {
  return (
    <ReactTable
      data={props.data}
      columns={props.columns}
      getTdProps={props.getTdProps}
      defaultPageSize={10}
      filterable={true}
    />
  )
}

export default Table
