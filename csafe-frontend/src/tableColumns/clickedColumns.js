import React from 'react'

const clickedColumns = [
  {
    Header: 'App Package Name',
    accessor: 'app_package_name',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Version',
    accessor: 'version',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'File System File Path',
    accessor: 'f_path',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'File System Evidence Types',
    accessor: 'f_evidence_types',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Network Address',
    accessor: 'n_path',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  },
  {
    Header: 'Network Evidence Types',
    accessor: 'n_evidence_types',
    Cell: row => (
      <div>
        <span title={row.value}>{row.value}</span>
      </div>
    )
  }
]

export default clickedColumns
