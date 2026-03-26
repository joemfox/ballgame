import React, { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'
import { useDrop, useDrag } from 'react-dnd'
import { ItemTypes } from '@/App'
import { Button } from "@/components/ui/button"
import { Minus, Lock, Unlock } from 'lucide-react'

const DB_POSITIONS = {
    lineup_C: "C",
    lineup_1B: "1B",
    lineup_2B: "2B",
    lineup_SS: "SS",
    lineup_3B: "3B",
    lineup_OF1: "OF",
    lineup_OF2: "OF",
    lineup_OF3: "OF",
    lineup_OF4: "OF",
    lineup_OF5: "OF",
    lineup_DH: "DH",
    lineup_UTIL: "UTIL",
    lineup_SP1: "SP",
    lineup_SP2: "SP",
    lineup_SP3: "SP",
    lineup_SP4: "SP",
    lineup_SP5: "SP",
    lineup_RP1: "RP",
    lineup_RP2: "RP",
    lineup_RP3: "RP",
}

const SLOT_ORDER = [
    'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
    'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
    'lineup_DH', 'lineup_UTIL',
    'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
    'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
]
const PITCHER_SLOTS = new Set(['lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5', 'lineup_RP1', 'lineup_RP2', 'lineup_RP3'])

const OF_POSITIONS = ['LF', 'CF', 'RF', 'OF']
const IF_POSITIONS = ['2B', 'SS', '3B']
const HITTER_POSITIONS = ['C', '1B', '2B', 'SS', '3B', 'LF', 'CF', 'RF', 'OF', 'IF', 'OF', 'IF-OF', 'DH']

function PlayerSlot({ forwardRef, playerInfo, position, highlighted, isDragging, onDropPlayer, pendingDrop, onConfirmDrop, onCancelDrop }) {
    return (
        <div ref={forwardRef} className={`${isDragging ? 'opacity-30' : ''} rounded-md border p-1 pl-2 mx-1 my-0.5 flex flex-row items-center gap-1`}>
            <div className="w-8 shrink-0 text-sm text-center font-bold border-r-2 mr-1 border-border text-muted-foreground">{position}</div>
            <div className="flex-1 min-w-0 overflow-hidden">
                {playerInfo.fg_id ? (
                    <span className="flex items-start gap-1 min-w-0">
                        <Link to={`/player/${playerInfo.fg_id}`} className="font-light text-sm text-left truncate block min-w-0 hover:underline">{playerInfo.name}</Link>
                        {playerInfo.level && playerInfo.level !== 'MLB' && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">{playerInfo.level}</span>}
                        {playerInfo.is_injured && <span className="text-[10px] px-1 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300 font-semibold leading-none shrink-0">{/IL/i.test(playerInfo.role) ? playerInfo.role : 'IL'}</span>}
                        {!playerInfo.is_injured && playerInfo.level === 'MLB' && playerInfo.role && <span className="text-[10px] px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold leading-none shrink-0">{playerInfo.role}</span>}
                        {!playerInfo.level && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">FA</span>}
                    </span>
                ) : (
                    <p className="font-light text-sm text-left truncate text-muted-foreground">—</p>
                )}
                {playerInfo.name && (playerInfo.positions?.length > 0 || playerInfo.mlb_org) && (
                    <p className="text-xs text-muted-foreground truncate text-left">
                        {playerInfo.mlb_org}
                        {playerInfo.mlb_org && playerInfo.positions?.length > 0 && <span className="mx-1">|</span>}
                        {playerInfo.positions?.join(', ')}
                    </p>
                )}
            </div>
            {playerInfo.fan_total != null && (
                <span className="shrink-0 text-xs text-muted-foreground tabular-nums">{Number(playerInfo.fan_total).toFixed(1)}</span>
            )}
            {playerInfo.name && onDropPlayer && !pendingDrop && (
                <Button variant="ghost" size="sm" className="shrink-0 text-muted-foreground hover:text-foreground h-6 w-6 p-0 border border-border bg-muted/50 font-bold"
                    onClick={() => onDropPlayer()}><Minus className="w-3.5 h-3.5 stroke-[2.5]" /></Button>
            )}
            {pendingDrop && (
                <div className="shrink-0 flex items-center gap-1">
                    <Button variant="ghost" size="sm" className="h-6 px-1 text-xs text-red-600 hover:text-red-800"
                        onClick={onConfirmDrop}>Drop</Button>
                    <Button variant="ghost" size="sm" className="h-6 px-1 text-xs"
                        onClick={onCancelDrop}>Cancel</Button>
                </div>
            )}
        </div>
    )
}

function PlayerSlotWrapper({ position, db_position, setDisplayLineup, onDropPlayer, onDraftPick, onSwapSlots, ...props }) {
    const [playerInfo, setPlayerInfo] = useState({ name: '', stats: '', positions: [], fg_id: null })
    const [pendingDrop, setPendingDrop] = useState(false)

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
        if (!p) {
            setPlayerInfo({ name: '', stats: '', positions: [], fg_id: null })
        } else if (p.name) {
            setPlayerInfo(p)
        } else {
            fetchNewPlayerInfo(p.fg_id ?? p)
        }
    }, [props.player])

    function onDrop(item) {
        const displacedFgId = playerInfo.fg_id

        if (item.sourceSlot && item.sourceSlot !== db_position) {
            // Drag from another lineup slot — swap
            setDisplayLineup(f => ({ ...f, [item.sourceSlot]: displacedFgId || null }))
            fetchNewPlayerInfo(item.id)
            if (onSwapSlots) onSwapSlots(item.sourceSlot, db_position, item.id, displacedFgId || null)
        } else if (!item.sourceSlot) {
            // Drag from stats table
            if (onDraftPick && !item.team_assigned) {
                // Free agent in draft mode — make a pick
                onDraftPick(item.id, db_position, () => fetchNewPlayerInfo(item.id))
            } else {
                // Already owned player — just reassign lineup slot
                axios.post('/api/lineup/assign', { slot: db_position, player_id: item.id })
                    .then(() => fetchNewPlayerInfo(item.id))
                    .catch(err => console.error(err))
            }
        }
    }

    function canDrop(item) {
        const isHitter = item.positions?.some(p => HITTER_POSITIONS.includes(p))
        const isOF = item.positions?.some(p => OF_POSITIONS.includes(p))
        const eligible = item.positions?.includes(position)
        const ofSlotEligible = position === 'OF' && isOF
        const ifEligible = IF_POSITIONS.includes(position) && (item.positions?.includes('IF') || item.positions?.includes('IN'))
        const dhSlotEligible = position === 'DH' && isHitter
        const utilSlotEligible = position === 'UTIL' && isHitter
        return eligible || ofSlotEligible || ifEligible || dhSlotEligible || utilSlotEligible
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
            onDropPlayer={playerInfo.fg_id ? () => setPendingDrop(true) : null}
            pendingDrop={pendingDrop}
            onConfirmDrop={() => { setPendingDrop(false); onDropPlayer(playerInfo.fg_id) }}
            onCancelDrop={() => setPendingDrop(false)}
        />
    )
}

export default function LineupCard({ team, rosterVersion, onRosterChange, onDraftPick }) {
    const [serverLineup, setServerLineup] = useState({})
    const [displayLineup, setDisplayLineup] = useState({})
    const [teamInfo, setTeamInfo] = useState(null)
    const [lockInfo, setLockInfo] = useState(null)

    const refreshLineup = useCallback(() => {
        if (!team) return
        axios.get('/api/lineup/full', { params: { team } })
            .then(res => setServerLineup(res.data))
    }, [team])

    useEffect(() => {
        axios.get('/api/schedule/lock_time')
            .then(res => setLockInfo(res.data))
            .catch(() => { })
    }, [])

    useEffect(() => {
        if (!team) return
        axios.get(`/api/team/${team}`).then(res => setTeamInfo(res.data)).catch(() => { })
    }, [team])

    useEffect(() => { refreshLineup() }, [refreshLineup, rosterVersion])

    useEffect(() => {
        const lineup = {}
        Object.keys(serverLineup).filter(k => k !== 'lineup_team').forEach(pos => {
            lineup[pos] = serverLineup[pos]
        })
        setDisplayLineup(lineup)
    }, [serverLineup])

    function handleSwapSlots(sourceSlot, targetSlot, sourceFgId, targetFgId) {
        const changes = { [targetSlot]: sourceFgId, [sourceSlot]: targetFgId }
        axios.post('/api/lineup', { team, ...changes })
            .then(() => refreshLineup())
            .catch(err => console.error(err))
    }

    function handleDropPlayer(fgId) {
        axios.post('/api/roster/drop', { player_id: fgId })
            .then(() => { refreshLineup(); if (onRosterChange) onRosterChange() })
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

    function formatLockTime(isoString) {
        const d = new Date(isoString)
        return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' })
    }

    return (
        <div className="p-1">
            {lockInfo && (
                lockInfo.is_locked
                    ? <div className="flex flex-col gap-0.5 px-1 mb-1">
                        <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Lock className="w-3 h-3 shrink-0" />Lineup locked
                        </span>
                        <span className="text-xs text-muted-foreground pl-4">Changes apply to tomorrow</span>
                      </div>
                    : lockInfo.roster_lock_time
                        ? <p className="flex items-center gap-1 text-xs text-muted-foreground px-1 mb-1">
                            <Unlock className="w-3 h-3 shrink-0" />Locks at {formatLockTime(lockInfo.roster_lock_time)}
                          </p>
                        : null
            )}
            {teamInfo && (
                <p className="text-sm font-semibold mb-2 px-1">{teamInfo.city} {teamInfo.nickname}</p>
            )}
            {SLOT_ORDER.filter(slot => slot in displayLineup).map((playerSlot, i) => (
                <React.Fragment key={playerSlot}>
                    {i > 0 && PITCHER_SLOTS.has(playerSlot) && !PITCHER_SLOTS.has(SLOT_ORDER[i - 1]) && (
                        <hr className="my-2 border-border" />
                    )}
                    <PlayerSlotWrapper
                        position={DB_POSITIONS[playerSlot]}
                        db_position={playerSlot}
                        player={displayLineup[playerSlot]}
                        setDisplayLineup={setDisplayLineup}
                        onDropPlayer={onDraftPick ? null : handleDropPlayer}
                        onDraftPick={onDraftPick}
                        onSwapSlots={onDraftPick ? null : handleSwapSlots}
                    />
                </React.Fragment>
            ))}
        </div>
    )
}