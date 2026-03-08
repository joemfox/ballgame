import React, { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import { useDrop, useDrag } from 'react-dnd'
import { ItemTypes } from '@/App'
import { Button } from "@/components/ui/button"

const DB_POSITIONS = {
    lineup_1B: "1B",
    lineup_2B: "2B",
    lineup_3B: "3B",
    lineup_C: "C",
    lineup_CF: "CF",
    lineup_LF: "LF",
    lineup_RF: "RF",
    lineup_RP1: "RP",
    lineup_RP2: "RP",
    lineup_RP3: "RP",
    lineup_SP1: "SP",
    lineup_SP2: "SP",
    lineup_SP3: "SP",
    lineup_SP4: "SP",
    lineup_SP5: "SP",
    lineup_SS: "SS",
}

const OF_POSITIONS = ['LF', 'CF', 'RF']
const IF_POSITIONS = ['2B', 'SS', '3B']

function PlayerSlot({ forwardRef, playerInfo, position, highlighted, isDragging, onDropPlayer }) {
    return (
        <div ref={forwardRef} className={`${!highlighted ? 'opacity-50' : ''} ${isDragging ? 'opacity-30' : ''} rounded-md border p-1 pl-2 m-1 flex flex-row items-center w-full gap-1`}>
            <div className="w-8 shrink-0 text-sm text-center font-bold border-r-2 mr-1 border-slate-300 text-slate-600">{position}</div>
            <div className="flex-1 min-w-0">
                <p className="font-light text-sm text-left truncate">{playerInfo.name}</p>
                {playerInfo.name && playerInfo.positions?.length > 0 && (
                    <p className="text-xs text-muted-foreground truncate">{playerInfo.positions.join(', ')}</p>
                )}
            </div>
            {playerInfo.fan_total != null && (
                <span className="shrink-0 text-xs text-muted-foreground tabular-nums">{Number(playerInfo.fan_total).toFixed(1)}</span>
            )}
            {playerInfo.name && onDropPlayer && (
                <Button variant="ghost" size="sm" className="shrink-0 text-red-500 hover:text-red-700 h-6 px-1 text-xs"
                    onClick={onDropPlayer}>Drop</Button>
            )}
        </div>
    )
}

function PlayerSlotWrapper({ position, db_position, setDisplayLineup, onDropPlayer, ...props }) {
    const [playerInfo, setPlayerInfo] = useState({ name: '', stats: '', positions: [], fg_id: null })

    const fetchNewPlayerInfo = useCallback((fg_id) => {
        if (!fg_id) return
        axios.get(`/api/player?playerid=${fg_id}`)
            .then(response => {
                setPlayerInfo(response.data)
                setDisplayLineup(f => ({ ...f, [db_position]: fg_id }))
            })
            .catch(err => console.error(err))
    }, [db_position, setDisplayLineup])

    useEffect(() => {
        const p = props.player
        if (p) {
            fetchNewPlayerInfo(p.fg_id ?? p)
        } else {
            setPlayerInfo({ name: '', stats: '', positions: [], fg_id: null })
        }
    }, [props.player])

    function onDrop(item) {
        const displacedFgId = playerInfo.fg_id

        if (item.sourceSlot && item.sourceSlot !== db_position) {
            // Drag from another lineup slot — swap
            setDisplayLineup(f => ({ ...f, [item.sourceSlot]: displacedFgId || null }))
            fetchNewPlayerInfo(item.id)
        } else if (!item.sourceSlot) {
            // Drag from stats table — assign to roster via API
            axios.post('/api/lineup/assign', { slot: db_position, player_id: item.id })
                .then(() => fetchNewPlayerInfo(item.id))
                .catch(err => console.error(err))
        }
    }

    function canDrop(item) {
        const eligible = item.positions?.includes(position)
        const ofEligible = OF_POSITIONS.includes(position) && item.positions?.includes('OF')
        const ifEligible = IF_POSITIONS.includes(position) && (item.positions?.includes('IF') || item.positions?.includes('IN'))
        return eligible || ofEligible || ifEligible
    }

    const [{ highlighted }, drop] = useDrop(() => ({
        accept: ItemTypes.PLAYER,
        drop: onDrop,
        canDrop: canDrop,
        collect: monitor => ({ highlighted: !monitor.getItem() || monitor.canDrop() }),
    }), [playerInfo, db_position])

    const [{ isDragging }, drag] = useDrag({
        type: ItemTypes.PLAYER,
        item: { id: playerInfo.fg_id, positions: playerInfo.positions || [], sourceSlot: db_position },
        canDrag: !!playerInfo.fg_id,
        collect: monitor => ({ isDragging: monitor.isDragging() }),
    }, [playerInfo.fg_id, playerInfo.positions, db_position])

    const combinedRef = useCallback(node => { drag(node); drop(node) }, [drag, drop])

    return (
        <PlayerSlot
            forwardRef={combinedRef}
            playerInfo={playerInfo}
            position={position}
            highlighted={highlighted}
            isDragging={isDragging}
            onDropPlayer={playerInfo.fg_id ? () => onDropPlayer(playerInfo.fg_id) : null}
        />
    )
}

export default function LineupCard({ team, rosterVersion }) {
    const [serverLineup, setServerLineup] = useState({})
    const [displayLineup, setDisplayLineup] = useState({})

    const refreshLineup = useCallback(() => {
        if (!team) return
        axios.get('/api/lineup', { params: { team } })
            .then(res => setServerLineup(res.data))
    }, [team])

    useEffect(() => { refreshLineup() }, [refreshLineup, rosterVersion])

    useEffect(() => {
        const lineup = {}
        Object.keys(serverLineup).filter(k => k !== 'lineup_team').forEach(pos => {
            lineup[pos] = serverLineup[pos]
        })
        setDisplayLineup(lineup)
    }, [serverLineup])

    function handleDropPlayer(fgId) {
        axios.post('/api/roster/drop', { player_id: fgId })
            .then(() => refreshLineup())
            .catch(err => console.error(err))
    }

    const saveLineup = () => {
        const changes = {}
        Object.keys(serverLineup).filter(k => k !== 'lineup_team').forEach(pos => {
            if (displayLineup[pos] !== serverLineup[pos]) {
                changes[pos] = displayLineup[pos]
            }
        })
        if (Object.keys(changes).length === 0) return
        axios.post('/api/lineup', { team, ...changes })
            .then(() => refreshLineup())
            .catch(err => console.error(err))
    }

    return (
        <div className="p-1">
            {Object.keys(displayLineup).map((playerSlot, i) => (
                <PlayerSlotWrapper
                    key={`${playerSlot}-${i}`}
                    position={DB_POSITIONS[playerSlot]}
                    db_position={playerSlot}
                    player={displayLineup[playerSlot]}
                    setDisplayLineup={setDisplayLineup}
                    onDropPlayer={handleDropPlayer}
                />
            ))}
            <Button onClick={saveLineup} size="sm" className="mt-1 w-full">Save</Button>
        </div>
    )
}