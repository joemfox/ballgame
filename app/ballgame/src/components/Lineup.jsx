import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useDrop, useDragDropManager } from 'react-dnd'
import { ItemTypes } from '@/App'

const POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "SP", "SP", "SP", "SP", "SP", "RP"]

function PlayerSlot({forwardRef, player, position, highlighted, ...props }) {
    return (
        <div ref={forwardRef} className={`${!highlighted ? 'opacity-50' : ''} rounded-md border p-4 pl-2 m-2 grid grid-cols-3 grid-rows-2`}>
            <div className="col-span-1 row-span-2 text-5xl text-center align-middle font-bold border-r-2 mr-2 pt-1 border-slate-900 text-slate-600">{position}</div>
            <p className="col-span-2 font-light text-2xl">{player.name}</p>
            <div className="col-span-2 geist-mono text-sm">{JSON.stringify(player.stats)}</div>
        </div>)
}

function PlayerSlotWrapper({ position, ...props }) {
    const [player, setPlayer] = useState({ id: null, name: "Player Name", stats: "" })
    function onDrop(item, monitor) {
        if (item.id) {
            axios.get(`http://localhost:8000/api/player/?id=${item.id}`)
                .then(response => {
                    setPlayer(response.data)
                })
                .catch(err => {
                    console.error(err)
                })
        }
    }
    function canDrop(item, monitor) {
        return item.positions.includes(position)
    }
    function collect(monitor) {
        return {
            highlighted: !monitor.getItem() || monitor.canDrop()
        }
    }
    const [collectedProps, drop] = useDrop(() => ({
        accept: ItemTypes.PLAYER,
        drop: onDrop,
        canDrop: canDrop,
        collect: collect
    }))
    
    return (
        <PlayerSlot forwardRef={drop} player={player} position={position} {...props} {...collectedProps} />
    )
}

export default function LineupCard({ team }) {
    useEffect(() => {
        // axios.get('http://localhost:8000/api/lineup',{
        //     params:{
        //         team:'TST'
        //     }
        // }).then(response => {
        //     console.log(response)
        // })

        axios.post('http://localhost:8000/api/lineup/',{
            team:'TST',
            lineup_C:13755
        }).then(response => {
            console.log(response)
        })
    },[])
    return (
        <div>
            {POSITIONS.map((playerSlot,i) => (
                <PlayerSlotWrapper key={`${playerSlot}-${i}`} position={playerSlot} />
            ))}
        </div>
    )
}