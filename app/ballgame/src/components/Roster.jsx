import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'

export default function Roster({ team, onRosterChange }) {
    const [players, setPlayers] = useState([])
    const [lockInfo, setLockInfo] = useState(null)

    useEffect(() => {
        axios.get('/api/schedule/lock_time')
            .then(res => setLockInfo(res.data))
            .catch(() => {})
    }, [])

    useEffect(() => {
        if (!team) return
        axios.get('/api/roster')
            .then(res => setPlayers(res.data))
            .catch(err => console.error(err))
    }, [team])

    function drop(fg_id) {
        axios.post('/api/roster/drop', { player_id: fg_id })
            .then(() => {
                setPlayers(prev => prev.filter(p => p.fg_id !== fg_id))
                if (onRosterChange) onRosterChange()
            })
            .catch(err => console.error(err))
    }

    if (!team) return <p className="p-4 text-sm text-muted-foreground">No team assigned to your account.</p>

    function LockBanner() {
        if (!lockInfo || !lockInfo.roster_lock_time) return null
        const lockDate = new Date(lockInfo.roster_lock_time)
        if (lockInfo.is_locked) {
            const formatted = lockDate.toLocaleDateString(undefined, { month: 'long', day: 'numeric' })
            return (
                <p className="text-xs text-muted-foreground px-3 py-2 border-b">
                    Rosters locked for {formatted} — transactions will not affect today's scores
                </p>
            )
        }
        const timeStr = lockDate.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
        return (
            <p className="text-xs text-muted-foreground px-3 py-2 border-b">
                Rosters lock at {timeStr}
            </p>
        )
    }

    return (
        <div className="rounded-md border geist-mono">
            <LockBanner />
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Pos</TableHead>
                        <TableHead></TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {players.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={3} className="text-center h-24">No players on roster.</TableCell>
                        </TableRow>
                    ) : players.map(p => (
                        <TableRow key={p.fg_id} className="h-4">
                            <TableCell className="h-4 pt-0 pb-0">{p.name}</TableCell>
                            <TableCell className="h-4 pt-0 pb-0">{p.positions?.join(', ')}</TableCell>
                            <TableCell className="h-4 pt-0 pb-0">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-red-600 hover:text-red-800"
                                    onClick={() => drop(p.fg_id)}
                                >
                                    Drop
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}
