import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useParams, Link } from 'react-router-dom'
import axios from 'axios'
import { DataTable } from '../components/StatlineTable';
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'


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

    const statlineColumns = [
        {
            accessorKey:'ab',
            header:'ab'
        },
        {
            accessorKey:'r',
            header:'r'
        },
        {
            accessorKey:'h',
            header:'h'
        },
        {
            accessorKey:'outs',
            header:'outs'
        },
        {
            accessorKey:'doubles',
            header:'doubles'
        },
        {
            accessorKey:'triples',
            header:'triples'
        },
        {
            accessorKey:'hr',
            header:'hr'
        },
        {
            accessorKey:'rbi',
            header:'rbi'
        },
        {
            accessorKey:'bb',
            header:'bb'
        },
        {
            accessorKey:'k',
            header:'k'
        },
        {
            accessorKey:'lob',
            header:'lob'
        },
        {
            accessorKey:'sb',
            header:'sb'
        },
        {
            accessorKey:'cs',
            header:'cs'
        },
        {
            accessorKey:'e',
            header:'e'
        },
        {
            accessorKey:'k_looking',
            header:'k_looking'
        },
        {
            accessorKey:'rl2o',
            header:'rl2o'
        },
        {
            accessorKey:'cycle',
            header:'cycle'
        },
        {
            accessorKey:'gidp',
            header:'gidp'
        },
        {
            accessorKey:'po',
            header:'po'
        },
        {
            accessorKey:'outfield_assists',
            header:'outfield_assists'
        },
        {
            accessorKey:'FAN_total',
            header:'FAN_total'
        },
    ]

    const FAN_columns = [
        {
            accessorKey:"FAN_outs",
            header:"outs"
        },
        {
            accessorKey:"FAN_bb",
            header:"bb"
        },
        {
            accessorKey:"FAN_triples",
            header:"triples"
        },
        {
            accessorKey:"FAN_hits",
            header:"hits"
        },
        {
            accessorKey:"FAN_cycle",
            header:"cycle"
        },
        {
            accessorKey:"FAN_doubles",
            header:"doubles"
        },
        {
            accessorKey:"FAN_outfield_assists",
            header:"outfield_assists"
        },
        {
            accessorKey:"FAN_cs",
            header:"cs"
        },
        {
            accessorKey:"FAN_e",
            header:"e"
        },
        {
            accessorKey:"FAN_gidp",
            header:"gidp"
        },
        {
            accessorKey:"FAN_hr",
            header:"hr"
        },
        {
            accessorKey:"FAN_r",
            header:"r"
        },
        {
            accessorKey:"FAN_lob",
            header:"lob"
        },
        {
            accessorKey:"FAN_po",
            header:"po"
        },
        {
            accessorKey:"FAN_rl2o",
            header:"rl2o"
        },
        {
            accessorKey:"FAN_rbi",
            header:"rbi"
        },
        {
            accessorKey:"FAN_k_looking",
            header:"k_looking"
        },
        {
            accessorKey:"FAN_k",
            header:"k"
        },
        {
            accessorKey:"FAN_sb",
            header:"sb"
        },
        {
            accessorKey:"FAN_total",
            header:"total"
    },
]
    
    return (
        <DndProvider backend={HTML5Backend}>
        {playerData.first_name} {playerData.last_name}
        <DataTable
            data={battingStatLines.length > 0 ? battingStatLines : []}
            columns={FAN_columns}
        />
        </DndProvider>
    )
}