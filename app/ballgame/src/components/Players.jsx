import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { DataTable } from './Table'

const playerTableColumns = [
      {
        accessorKey: "name",
        header: "name"
      },
      {
        accessorKey: "team",
        header: "Team",
      },
      {
        accessorKey:'stats',
        header:"Stats"
      }
]

export default function Players() {
    const [players, setPlayers] = useState([])
    useEffect(() => {
        axios.get('http://localhost:8000/api/players')
            .then(response => {
                // console.log(response.data)
                setPlayers(response.data)
            })
            .catch(err => {
                console.log(err)
            })
    }, [])

    return (
        <div className="container mx-auto py-10 w-full">
        <DataTable columns={playerTableColumns} data={players}/>
        </div>
    )
}