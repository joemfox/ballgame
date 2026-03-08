import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'

function StatRow({ label, value }) {
    if (value == null || value === 0) return null
    return (
        <tr className="border-b last:border-0">
            <td className="py-1 pr-4 text-muted-foreground text-sm">{label}</td>
            <td className="py-1 text-sm tabular-nums text-right">{typeof value === 'number' ? value.toFixed(1) : value}</td>
        </tr>
    )
}

const HIT_STATS = [
    ['H', 'h'], ['2B', 'doubles'], ['3B', 'triples'], ['HR', 'hr'], ['R', 'r'], ['RBI', 'rbi'],
    ['BB', 'bb'], ['K', 'k'], ['K (looking)', 'k_looking'], ['SB', 'sb'], ['CS', 'cs'],
    ['LOB', 'lob'], ['Outs', 'outs'], ['GIDP', 'gidp'], ['E', 'e'], ['PO', 'po'],
    ['RL2O', 'rl2o'], ['OA', 'outfield_assists'], ['Cycle', 'cycle'],
]
const HIT_FAN = [
    ['FAN H', 'FAN_h'], ['FAN 2B', 'FAN_doubles'], ['FAN 3B', 'FAN_triples'], ['FAN HR', 'FAN_hr'],
    ['FAN R', 'FAN_r'], ['FAN RBI', 'FAN_rbi'], ['FAN BB', 'FAN_bb'], ['FAN K', 'FAN_k'],
    ['FAN K👀', 'FAN_k_looking'], ['FAN SB', 'FAN_sb'], ['FAN CS', 'FAN_cs'],
    ['FAN LOB', 'FAN_lob'], ['FAN Outs', 'FAN_outs'], ['FAN GIDP', 'FAN_gidp'], ['FAN E', 'FAN_e'],
    ['FAN PO', 'FAN_po'], ['FAN RL2O', 'FAN_rl2o'], ['FAN OA', 'FAN_outfield_assists'],
    ['FAN Total', 'FAN_total'],
]
const PITCH_STATS = [
    ['IP', 'ip'], ['H', 'h'], ['ER', 'er'], ['BB', 'bb'], ['K', 'k'], ['HR', 'hr'],
    ['BS', 'bs'], ['HB', 'hb'], ['WP', 'wp'], ['Balks', 'balks'],
    ['IR', 'ir'], ['IRS', 'irs'], ['E', 'e'], ['BRA', 'bra'], ['DPI', 'dpi'],
    ['Perfect Game', 'perfect_game'], ['No-Hitter', 'no_hitter'], ['Relief Loss', 'relief_loss'],
]
const PITCH_FAN = [
    ['FAN IP', 'FAN_ip'], ['FAN H', 'FAN_h'], ['FAN ER', 'FAN_er'], ['FAN BB', 'FAN_bb'],
    ['FAN K', 'FAN_k'], ['FAN HR', 'FAN_hr'], ['FAN BS', 'FAN_bs'], ['FAN HB', 'FAN_hb'],
    ['FAN WP', 'FAN_wp'], ['FAN Balks', 'FAN_balks'], ['FAN IR', 'FAN_ir'], ['FAN IRS', 'FAN_irs'],
    ['FAN E', 'FAN_e'], ['FAN BRA', 'FAN_bra'], ['FAN DPI', 'FAN_dpi'],
    ['FAN PG', 'FAN_perfect_game'], ['FAN NH', 'FAN_no_hitter'], ['FAN RL', 'FAN_relief_loss'],
    ['FAN Total', 'FAN_total'],
]

export default function PlayerDetail() {
    const { playerid } = useParams()
    const [player, setPlayer] = useState(null)
    const [season, setSeason] = useState(null)
    const [hitStats, setHitStats] = useState(null)
    const [pitchStats, setPitchStats] = useState(null)

    useEffect(() => {
        axios.get(`/api/player?playerid=${playerid}`).then(r => setPlayer(r.data)).catch(console.error)
        axios.get('/api/season').then(r => setSeason(r.data.season)).catch(console.error)
    }, [playerid])

    useEffect(() => {
        if (!season || !playerid) return
        axios.get(`/api/player/${playerid}/season/${season}/hit`).then(r => setHitStats(r.data)).catch(() => setHitStats(null))
        axios.get(`/api/player/${playerid}/season/${season}/pitch`).then(r => setPitchStats(r.data)).catch(() => setPitchStats(null))
    }, [playerid, season])

    if (!player) return <div className="p-4 text-sm text-muted-foreground">Loading...</div>

    const isPitcher = player.positions?.some(p => ['SP', 'RP'].includes(p))
    const stats = isPitcher ? pitchStats : hitStats
    const rawRows = isPitcher ? PITCH_STATS : HIT_STATS
    const fanRows = isPitcher ? PITCH_FAN : HIT_FAN

    return (
        <div className="p-4 max-w-md">
            <div className="mb-4">
                <h2 className="text-xl font-semibold">{player.name}</h2>
                <div className="flex gap-3 mt-1 text-sm text-muted-foreground">
                    <span>{player.positions?.join(', ')}</span>
                    {player.team_assigned && <span>· {player.team_assigned.abbreviation}</span>}
                    {player.fan_total != null && (
                        <span>· <span className="font-medium text-foreground">{Number(player.fan_total).toFixed(1)} FAN pts</span></span>
                    )}
                </div>
            </div>

            {!stats ? (
                <p className="text-sm text-muted-foreground">No {season} season stats.</p>
            ) : (
                <div className="flex gap-8">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Raw</p>
                        <table>
                            <tbody>
                                {rawRows.map(([label, key]) => <StatRow key={key} label={label} value={stats[key]} />)}
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">FAN Points</p>
                        <table>
                            <tbody>
                                {fanRows.map(([label, key]) => <StatRow key={key} label={label} value={stats[key]} />)}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
