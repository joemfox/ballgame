import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Columns } from './Columns'
import { DataTable } from './Table'

export default function Players() {
    const [players, setPlayers] = useState([])
    useEffect(() => {
        axios.get('http://localhost:8000/api/players')
            .then(response => {
                console.log(response.data)
                setPlayers(response.data)
            })
            .catch(err => {
                console.log(err)
            })
    }, [])

    return (
        <div className="container mx-auto py-10">
        <DataTable columns={Columns} data={players}/>
        </div>
    )
}