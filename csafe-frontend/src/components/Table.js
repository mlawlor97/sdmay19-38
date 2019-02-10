import React from 'react'
import ReactTable from 'react-table'
import 'react-table/react-table.css'

function Table(props) {
  const data = [
    {
      name: 'Matt',
      age: '21'
    }
  ]
  const columns = [
    {
      Header: 'Name',
      accessor: 'name' // String-based value accessors!
    },
    {
      Header: 'Age',
      accessor: 'age'
    }
  ]

  return <ReactTable data={data} columns={columns} />
}

export default Table
