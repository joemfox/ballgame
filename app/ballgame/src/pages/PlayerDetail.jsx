import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useParams, Link } from 'react-router-dom'
import axios from 'axios'
import DataTable from '../components/StatlineTable';
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import { FAN_columns_hit } from '../lib/dataColumns';


export default function PlayerDetail(){
    let {playerid} = useParams();
    let [playerData, setPlayerData] = useState({})
    let [battingStatLines, setBattingStatLines] = useState([])
    useEffect(() => {
        axios.get(`http://localhost:8000/api/player?playerid=${playerid}`)
            .then(response => {
                setPlayerData(response.data)
                console.log(response.data)
            })

        axios.get(`http://localhost:8000/api/statlines/batting?playerid=${playerid}`)
            .then(response => {
                setBattingStatLines(response.data)
                console.log(response.data)
            })
    },[playerid])

    
    
    return (
        <DndProvider backend={HTML5Backend}>
        {playerData.first_name} {playerData.last_name}
        {/* <DataTable
            data={battingStatLines.length > 0 ? battingStatLines : []}
            columns={FAN_columns}
        /> */}
        </DndProvider>
    )
}