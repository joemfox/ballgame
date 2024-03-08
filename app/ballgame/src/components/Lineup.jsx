import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useDrop, useDragDropManager } from 'react-dnd'
import { ItemTypes } from '@/App'
import { Button } from "@/components/ui/button"

const DB_POSITIONS = {
lineup_1B:"1B",
lineup_2B:"2B",
lineup_3B:"3B",
lineup_C:"C",
lineup_CF:"CF",
lineup_LF:"LF",
lineup_RF:"RF",
lineup_RP1:"RP",
lineup_RP2:"RP",
lineup_RP3:"RP",
lineup_SP1:"SP",
lineup_SP2:"SP",
lineup_SP3:"SP",
lineup_SP4:"SP",
lineup_SP5:"SP",
lineup_SS:"SS",
 }

function PlayerSlot({ forwardRef, playerInfo, position, highlighted, ...props }) {
    return (
        <div ref={forwardRef} className={`${!highlighted ? 'opacity-50' : ''} rounded-md border p-4 pl-2 m-2 flex flex-row flex-wrap w-full`}>
            <div className="basis-10 shrink-0 grow-0 text-2xl text-center align-middle font-bold border-r-2 mr-2 pt-1 border-slate-900 text-slate-600">{position}</div>
            <p className=" basis-11/12 shrink-0 font-light text-xl text-left align-middle">{playerInfo.name}</p>
            <div className="basis-full geist-mono text-sm">{JSON.stringify(playerInfo.stats)}</div>
        </div>)
}

function PlayerSlotWrapper({ position, db_position, setDisplayLineup, ...props }) {
    const [player, setPlayer] = useState(props.player)
    const [playerInfo, setPlayerInfo] = useState({ name: '', stats: '' })

    const fetchNewPlayerInfo = (player) => {
        axios.get(`http://localhost:8000/api/player?playerid=${player}`)
            .then(response => {
                setPlayerInfo(response.data)
                setPlayer(player.fg_id)
                setDisplayLineup(f => ({
                    ...f,
                    [db_position]: player
                }))
            })
            .catch(err => {
                console.error(err)
            })
    }
    useEffect(() => {
        if (props.player) {
            fetchNewPlayerInfo(props.player.fg_id ? props.player.fg_id : props.player)
        }
    }, [props.player])

    function onDrop(item, monitor) {
        if (item.id) {
            fetchNewPlayerInfo(item.id)
        }
    }
    function canDrop(item, monitor) {
        console.log(item)

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
        axios.post('http://localhost:8000/api/lineup', {
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
        console.log('server: ', serverLineup)
        let newLineup = {}
        Object.keys(serverLineup).filter(d => d !== 'lineup_team').map(pos => {
            newLineup[pos] = serverLineup[pos]
        })
        console.log('display: ',newLineup)
        setDisplayLineup(newLineup)
    }, [serverLineup])
    return (
        <div className="relative">
            {Object.keys(displayLineup).map((playerSlot, i) => (
                <PlayerSlotWrapper key={`${playerSlot}-${i}`} position={DB_POSITIONS[playerSlot]} db_position={playerSlot} player={displayLineup[playerSlot]} setDisplayLineup={setDisplayLineup} />
            ))}
            <Button onClick={saveLineup} >Save</Button>
        </div>
    )
}