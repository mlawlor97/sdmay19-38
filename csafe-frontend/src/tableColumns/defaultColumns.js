import React from 'react'

const defaultColumns = [
  {
    Header: 'Store',
    accessor: 'store_id',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'App Name',
    accessor: 'app_name',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Developer',
    accessor: 'Developer',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Package',
    accessor: 'Package',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Version',
    accessor: 'Version',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Category',
    accessor: 'Category',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Download',
    accessor: 'url',
    Cell: row => <a href={row.value}> {row.value} </a>
  }
]

export default defaultColumns
