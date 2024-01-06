import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useDrop, useDragDropManager } from 'react-dnd'
import { ItemTypes } from '@/App'
import { Button } from "@/components/ui/button"

const POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "SP", "SP", "SP", "SP", "SP", "RP","RP","RP"]

function PlayerSlot({ forwardRef, playerInfo, position, highlighted, ...props }) {
    return (
        <div ref={forwardRef} className={`${!highlighted ? 'opacity-50' : ''} rounded-md border p-4 pl-2 m-2 grid grid-cols-3 grid-rows-2`}>
            <div className="col-span-1 row-span-2 text-5xl text-center align-middle font-bold border-r-2 mr-2 pt-1 border-slate-900 text-slate-600">{position}</div>
            <p className="col-span-2 font-light text-2xl">{playerInfo.name}</p>
            <div className="col-span-2 geist-mono text-sm">{JSON.stringify(playerInfo.stats)}</div>
        </div>)
}

function PlayerSlotWrapper({ position, db_position, setDisplayLineup, ...props }) {
    const [player, setPlayer] = useState(props.player)
    const [playerInfo, setPlayerInfo] = useState({ name: '', stats: '' })

    const fetchNewPlayerInfo = (id) => {
        axios.get(`http://localhost:8000/api/player/?id=${id}`)
            .then(response => {
                setPlayerInfo(response.data)
                setPlayer(id)
                setDisplayLineup(f => ({
                    ...f,
                    [db_position]: id
                }))
            })
            .catch(err => {
                console.error(err)
            })
    }
    useEffect(() => {
        if (props.player !== null) {
            fetchNewPlayerInfo(props.player)
        }
    }, [props.player])

    function onDrop(item, monitor) {
        if (item.id) {
            fetchNewPlayerInfo(item.id)
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
        <PlayerSlot forwardRef={drop} playerInfo={playerInfo} position={position} {...props} {...collectedProps} />
    )
}

export default function LineupCard({ team }) {
    const [serverLineup, setServerLineup] = useState({})
    const [displayLineup, setDisplayLineup] = useState({})

    const saveLineup = () => {
        let newLineup = {}
        Object.keys(serverLineup).filter(d => d !== 'lineup_team').map(pos => {
            if (displayLineup[pos] !== serverLineup[pos]) {
                newLineup[pos] = displayLineup[pos]
            }
        })
        console.log(newLineup)
        axios.post('http://localhost:8000/api/lineup/', {
            team: 'TST',
            ...newLineup

        }).then(response => {
            console.log(response)
        })
    }
    useEffect(() => {
        axios.get('http://localhost:8000/api/lineup', {
            params: {
                team: 'TST'
            }
        }).then(response => {
            setServerLineup(response.data)
        })


    }, [])

    useEffect(() => {
        let newLineup = {}
        Object.keys(serverLineup).filter(d => d !== 'lineup_team').map(pos => {
            newLineup[pos] = serverLineup[pos]
        })
        setDisplayLineup(newLineup)
    }, [serverLineup])
    return (
        <div>
            {Object.keys(displayLineup).map((playerSlot, i) => (
                <PlayerSlotWrapper key={`${playerSlot}-${i}`} position={POSITIONS[i]} db_position={playerSlot} player={displayLineup[playerSlot]} setDisplayLineup={setDisplayLineup} />
            ))}
            <Button onClick={saveLineup} >Save</Button>
        </div>
    )
}