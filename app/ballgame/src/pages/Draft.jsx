import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import StatlineTable from '@/components/StatlineTable.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const POLL_INTERVAL = 5000

export default function Draft({ team, isAdmin, onRosterChange, setDraftMode }) {
    const [draft, setDraft] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (setDraftMode) setDraftMode(true)
        return () => { if (setDraftMode) setDraftMode(false) }
    }, [setDraftMode])
    const [starting, setStarting] = useState(false)
    const [startError, setStartError] = useState(null)
    const [pickError, setPickError] = useState(null)
    const [pickVersion, setPickVersion] = useState(0)

    const fetchDraft = useCallback(() => {
        axios.get('/api/draft')
            .then(res => { setDraft(res.data); setLoading(false); setError(null) })
            .catch(err => {
                if (err.response?.status === 404) {
                    setError('No draft found for the current season.')
                } else {
                    setError('Failed to load draft.')
                }
                setLoading(false)
            })
    }, [])

    useEffect(() => {
        fetchDraft()
        const interval = setInterval(fetchDraft, POLL_INTERVAL)
        return () => clearInterval(interval)
    }, [fetchDraft])

    const makePick = (fg_id) => {
        setPickError(null)
        axios.post('/api/draft/pick', { player_fg_id: fg_id })
            .then(() => { fetchDraft(); setPickVersion(v => v + 1); if (onRosterChange) onRosterChange() })
            .catch(err => setPickError(err.response?.data?.detail || 'Pick failed.'))
    }

    const startDraft = () => {
        setStarting(true)
        setStartError(null)
        axios.post('/api/draft/start', {})
            .then(() => { fetchDraft(); setPickVersion(v => v + 1) })
            .catch(err => setStartError(err.response?.data?.detail || 'Failed to start draft.'))
            .finally(() => setStarting(false))
    }

    const isMyTurn = draft?.status === 'active' && draft?.current_team === team

    const draftActionColumn = {
        id: 'draft_action',
        header: '',
        cell: ({ row }) => {
            const { fg_id } = row.original
            return (
                <Button variant="ghost" size="sm" disabled={!isMyTurn}
                    onClick={() => makePick(fg_id)}>
                    Draft
                </Button>
            )
        }
    }

    // Group all picks by round
    const picksByRound = {}
    if (draft?.picks) {
        const n = draft.order.length
        for (let pick of draft.picks) {
            const round = Math.floor((pick.pick_number - 1) / n) + 1
            if (!picksByRound[round]) picksByRound[round] = []
            picksByRound[round].push(pick)
        }
    }

    if (loading) return <p className="p-4 text-sm text-muted-foreground">Loading draft...</p>
    if (error) return (
        <div className="p-4">
            <p className="text-sm text-red-500 mb-3">{error}</p>
            {isAdmin && (
                <div>
                    <Button onClick={startDraft} disabled={starting} size="sm">
                        {starting ? 'Starting…' : 'Start Draft'}
                    </Button>
                    {startError && <p className="text-sm text-red-500 mt-2">{startError}</p>}
                </div>
            )}
        </div>
    )

    return (
        <div className="flex gap-4 h-full">
            {/* Picks board */}
            <div className="w-56 shrink-0 border-r pr-3 overflow-y-auto">
                <h3 className="font-semibold text-sm mb-2">
                    Draft {draft.year}
                    <span className="ml-2 text-xs text-muted-foreground capitalize">({draft.status})</span>
                </h3>
                {draft.status === 'active' && (
                    <p className="text-xs mb-3">
                        On the clock: <span className="font-semibold">{draft.current_team}</span>
                        {isMyTurn && <span className="ml-1 text-green-600">(you!)</span>}
                    </p>
                )}
                {draft.status === 'pending' && (
                    <div className="mb-3">
                        <p className="text-xs text-muted-foreground mb-2">Draft has not started yet.</p>
                        {isAdmin && (
                            <div>
                                <Button onClick={startDraft} disabled={starting} size="sm">
                                    {starting ? 'Starting…' : 'Start Draft'}
                                </Button>
                                {startError && <p className="text-xs text-red-500 mt-1">{startError}</p>}
                            </div>
                        )}
                    </div>
                )}
                {draft.status === 'complete' && (
                    <p className="text-xs text-muted-foreground mb-3">Draft complete.</p>
                )}
                {pickError && <p className="text-xs text-red-500 mb-2">{pickError}</p>}
                {Object.keys(picksByRound).sort((a, b) => a - b).map(round => (
                    <div key={round} className="mb-3">
                        <p className="text-xs font-medium text-muted-foreground mb-1">Round {round}</p>
                        {picksByRound[round].map(pick => (
                            <div key={pick.pick_number} className={`text-xs flex gap-1 py-0.5 ${pick.pick_number === draft.current_pick ? 'font-semibold' : ''}`}>
                                <span className="text-muted-foreground w-5 shrink-0">{pick.pick_number}.</span>
                                <span className="font-medium w-8 shrink-0">{pick.team}</span>
                                <span className="truncate">{pick.player_name ?? '—'}</span>
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Player pool */}
            <div className="flex-1 overflow-hidden">
                <Tabs defaultValue="hit">
                    <TabsList>
                        <TabsTrigger value="hit">Hitters</TabsTrigger>
                        <TabsTrigger value="pitch">Pitchers</TabsTrigger>
                    </TabsList>
                    <TabsContent value="hit">
                        <StatlineTable
                            type="hit"
                            customActionColumn={draftActionColumn}
                            defaultOwnershipFilter="available"
                            ownershipOptions={['all', 'available']}
                            rosterVersion={pickVersion}
                        />
                    </TabsContent>
                    <TabsContent value="pitch">
                        <StatlineTable
                            type="pitch"
                            customActionColumn={draftActionColumn}
                            defaultOwnershipFilter="available"
                            ownershipOptions={['all', 'available']}
                            rosterVersion={pickVersion}
                        />
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    )
}
