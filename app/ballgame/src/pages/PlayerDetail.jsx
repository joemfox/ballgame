import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'
import columnData from '@/lib/dataColumns'

const RAW_TO_FAN = {
    outs: 'FAN_outs', bb: 'FAN_bb', triples: 'FAN_triples', h: 'FAN_h',
    cycle: 'FAN_cycle', doubles: 'FAN_doubles', outfield_assists: 'FAN_outfield_assists',
    cs: 'FAN_cs', e: 'FAN_e', gidp: 'FAN_gidp', hr: 'FAN_hr', r: 'FAN_r',
    lob: 'FAN_lob', po: 'FAN_po', rl2o: 'FAN_rl2o', rbi: 'FAN_rbi',
    k_looking: 'FAN_k_looking', k: 'FAN_k', sb: 'FAN_sb',
    ip: 'FAN_ip', er: 'FAN_er', bs: 'FAN_bs', balks: 'FAN_balks', hb: 'FAN_hb',
    bra: 'FAN_bra', dpi: 'FAN_dpi', wp: 'FAN_wp', ir: 'FAN_ir', irs: 'FAN_irs',
    perfect_game: 'FAN_perfect_game', no_hitter: 'FAN_no_hitter', relief_loss: 'FAN_relief_loss',
}

function getShadeStyle(val, range, colorRange) {
    if (!range || range.min === null || range.max === null || range.min === range.max) return {}
    if (typeof val !== 'number') return {}
    const { min, max } = range
    const cr = (colorRange && colorRange.min !== null && colorRange.max !== null) ? colorRange : range
    const shade = (t) => `${(Math.pow(Math.max(0, Math.min(1, t)), 3) * 0.18).toFixed(3)}`
    const t = min === max ? 0 : (val - min) / (max - min)
    const isRaw = colorRange !== null
    if (cr.max <= 0) {
        const intensity = isRaw ? t : (1 - t)
        return { backgroundColor: `rgba(112, 0, 160, ${shade(intensity)})` }
    } else if (cr.min >= 0) {
        return { backgroundColor: `rgba(0, 255, 100, ${shade(t)})` }
    } else {
        if (val >= 0) {
            return { backgroundColor: `rgba(0, 255, 100, ${shade(t)})` }
        } else {
            return { backgroundColor: `rgba(112, 0, 160, ${shade(1 - t)})` }
        }
    }
}

const DATE_COL = {
    id: 'date',
    accessorKey: 'date',
    header: 'Date',
    cell: ({ row }) => <div className="text-left text-muted-foreground tabular-nums">{row.getValue('date')}</div>,
}

const AB_COL = {
    id: 'ab',
    accessorKey: 'ab',
    header: 'AB',
    cell: ({ row }) => <div className="text-right">{row.getValue('ab') ?? '-'}</div>,
}

function GameLog({ rows, type }) {
    const [scoreType, setScoreType] = useState('RAW')

    const activeClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
    const inactiveClass = 'bg-muted text-foreground hover:bg-muted/80'

    const statCols = columnData[`${scoreType}_columns_${type}`].slice(3)
    const cols = type === 'hit'
        ? [DATE_COL, statCols[0], AB_COL, ...statCols.slice(1)]
        : [DATE_COL, ...statCols]
    const table = useReactTable({ data: rows ?? [], columns: cols, getCoreRowModel: getCoreRowModel() })

    if (!rows?.length) return <p className="text-sm text-muted-foreground mt-4">No game log entries.</p>
    return (
        <div className="mt-8">
            <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Game Log</p>
                <div className="flex rounded-md border overflow-hidden text-xs w-fit">
                    {['FAN', 'RAW'].map(s => (
                        <button key={s} onClick={() => setScoreType(s)}
                            className={`px-2 py-1 ${scoreType === s ? activeClass : inactiveClass}`}>
                            {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
                        </button>
                    ))}
                </div>
            </div>
            <div className="overflow-auto h-[calc(100vh-280px)] rounded-md border">
                <table className="text-sm geist-mono w-full" style={{ minWidth: 'max-content' }}>
                    <thead className="sticky top-0 z-10">
                        <tr className="border-b">
                            {table.getHeaderGroups()[0].headers.map(header => (
                                <th key={header.id}
                                    style={header.column.columnDef.meta?.highlight ? {} : { backgroundColor: 'hsl(var(--background))' }}
                                    className={`px-3 py-2 font-medium text-right first:text-left ${header.column.columnDef.meta?.highlight ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'} ${header.column.columnDef.meta?.className ?? ''}`}>
                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {table.getRowModel().rows.map((row, i) => (
                            <tr key={i} className="border-b last:border-0 hover:bg-muted/40">
                                {row.getVisibleCells().map(cell => (
                                    <td key={cell.id}
                                        className={`px-3 py-1.5 tabular-nums text-right ${cell.column.id === 'date' ? 'text-left' : ''} ${cell.column.columnDef.meta?.highlight ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''} ${cell.column.columnDef.meta?.className ?? ''}`}>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

const SPRING_TYPES = new Set(['S', 'E'])
const POST_TYPES = new Set(['D', 'L', 'W', 'F', 'P', 'A'])
const GAME_TYPE_SHORT = { S: 'ST', E: 'EX', A: 'AS', D: 'DS', L: 'LCS', W: 'WS', F: 'WC', P: 'PS' }

// [label, rawKey, fanKey] — rawKey is null for Total which has no raw stat
const HIT_COLS = [
    ['H', 'h', 'FAN_h'], ['2B', 'doubles', 'FAN_doubles'], ['3B', 'triples', 'FAN_triples'],
    ['HR', 'hr', 'FAN_hr'], ['R', 'r', 'FAN_r'], ['RBI', 'rbi', 'FAN_rbi'],
    ['BB', 'bb', 'FAN_bb'], ['K', 'k', 'FAN_k'], ['K👀', 'k_looking', 'FAN_k_looking'],
    ['SB', 'sb', 'FAN_sb'], ['CS', 'cs', 'FAN_cs'], ['LOB', 'lob', 'FAN_lob'],
    ['Outs', 'outs', 'FAN_outs'], ['GIDP', 'gidp', 'FAN_gidp'], ['E', 'e', 'FAN_e'],
    ['PO', 'po', 'FAN_po'], ['RL2O', 'rl2o', 'FAN_rl2o'], ['OA', 'outfield_assists', 'FAN_outfield_assists'],
    ['CYC', 'cycle', 'FAN_cycle'], ['Total', null, 'FAN_total'],
]
const PITCH_COLS = [
    ['IP', 'ip', 'FAN_ip'], ['H', 'h', 'FAN_h'], ['ER', 'er', 'FAN_er'],
    ['BB', 'bb', 'FAN_bb'], ['K', 'k', 'FAN_k'], ['HR', 'hr', 'FAN_hr'],
    ['BS', 'bs', 'FAN_bs'], ['HB', 'hb', 'FAN_hb'], ['WP', 'wp', 'FAN_wp'],
    ['Balks', 'balks', 'FAN_balks'], ['IR', 'ir', 'FAN_ir'], ['IRS', 'irs', 'FAN_irs'],
    ['E', 'e', 'FAN_e'], ['BRA', 'bra', 'FAN_bra'], ['DPI', 'dpi', 'FAN_dpi'],
    ['PG', 'perfect_game', 'FAN_perfect_game'], ['NH', 'no_hitter', 'FAN_no_hitter'],
    ['RL', 'relief_loss', 'FAN_relief_loss'], ['Total', null, 'FAN_total'],
]

function fmt(val) {
    if (val == null) return '-'
    if (typeof val === 'number') return val % 1 === 0 ? val : val.toFixed(1)
    return val
}

function SeasonStatsTable({ stats, cols, globalRanges }) {
    return (
        <div className="overflow-x-auto mt-4">
            <table className="text-sm geist-mono border-collapse">
                <thead className="sticky top-0 z-10 bg-background">
                    <tr>
                        <th className="px-2 py-1 text-left text-muted-foreground font-medium w-12"></th>
                        {cols.map(([label, , fanKey]) => {
                            const isTotal = fanKey === 'FAN_total'
                            return (
                                <th key={label} className={`px-2 py-1 text-right font-medium ${isTotal ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'}`}>{label}</th>
                            )
                        })}
                    </tr>
                </thead>
                <tbody>
                    <tr className="border-t">
                        <td className="px-2 py-1 text-muted-foreground">Raw</td>
                        {cols.map(([label, rawKey, fanKey]) => {
                            const isTotal = fanKey === 'FAN_total'
                            const val = rawKey != null ? stats[rawKey] : null
                            const range = rawKey ? globalRanges[rawKey] : null
                            const colorRange = rawKey ? globalRanges[RAW_TO_FAN[rawKey]] : null
                            const shadeStyle = !isTotal && range ? getShadeStyle(val, range, colorRange) : {}
                            return (
                                <td key={label} className={`px-2 py-1 text-right tabular-nums${isTotal ? ' bg-orange-50 dark:bg-orange-950/40' : ''}`} style={shadeStyle}>
                                    {rawKey != null ? fmt(val) : ''}
                                </td>
                            )
                        })}
                    </tr>
                    <tr className="border-t">
                        <td className="px-2 py-1 text-muted-foreground">FAN</td>
                        {cols.map(([label, , fanKey]) => {
                            const isTotal = fanKey === 'FAN_total'
                            const val = stats[fanKey]
                            const range = !isTotal ? globalRanges[fanKey] : null
                            const shadeStyle = range ? getShadeStyle(val, range, null) : {}
                            return (
                                <td key={label} className={`px-2 py-1 text-right tabular-nums ${isTotal ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''}`} style={shadeStyle}>
                                    {fmt(val)}
                                </td>
                            )
                        })}
                    </tr>
                </tbody>
            </table>
        </div>
    )
}

function TodayStatlines({ playerid, isPitcher }) {
    const [data, setData] = useState(null)

    useEffect(() => {
        const localDate = new Date().toLocaleDateString('en-CA')
        axios.get(`/api/statlines/today?playerid=${playerid}&date=${localDate}`)
            .then(r => setData(r.data))
            .catch(() => setData(null))
    }, [playerid])

    const games = data ? (isPitcher ? data.pitching : data.batting) : []
    if (!data || !games.length) return null

    const cols = isPitcher ? PITCH_COLS : HIT_COLS

    return (
        <div className="mt-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Today</p>
            <div className="overflow-x-auto">
                <table className="text-sm geist-mono border-collapse">
                    <thead className="sticky top-0 z-10 bg-background">
                        <tr>
                            <th className="px-2 py-1 text-left text-muted-foreground font-medium w-10"></th>
                            <th className="px-2 py-1 text-left text-muted-foreground font-medium w-8"></th>
                            {cols.map(([lbl, , fanKey]) => {
                                const isTotal = fanKey === 'FAN_total'
                                return (
                                    <th key={lbl} className={`px-2 py-1 text-right font-medium ${isTotal ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'}`}>{lbl}</th>
                                )
                            })}
                        </tr>
                    </thead>
                    <tbody>
                        {games.map((game, gi) => {
                            const gt = game.game_type
                            const isNonR = gt && gt !== 'R'
                            const rowBg = isNonR
                                ? SPRING_TYPES.has(gt) ? 'bg-green-50/60 dark:bg-green-950/20' : 'bg-yellow-50/60 dark:bg-yellow-950/20'
                                : ''
                            const badge = isNonR
                                ? <span className={`text-xs px-1 py-0.5 rounded font-semibold ${SPRING_TYPES.has(gt) ? 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300' : 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200'}`}>{GAME_TYPE_SHORT[gt] ?? gt}</span>
                                : null
                            return (
                                <React.Fragment key={gi}>
                                    <tr className={`border-t ${rowBg}`}>
                                        <td className="px-2 py-1 text-muted-foreground">Raw</td>
                                        <td className="px-2 py-1">{badge}</td>
                                        {cols.map(([lbl, rawKey, fanKey]) => {
                                            const isTotal = fanKey === 'FAN_total'
                                            const val = rawKey != null ? game[rawKey] : null
                                            return (
                                                <td key={lbl} className={`px-2 py-1 text-right tabular-nums${isTotal ? ' bg-orange-50 dark:bg-orange-950/40' : ''}`}>
                                                    {rawKey != null ? fmt(val) : ''}
                                                </td>
                                            )
                                        })}
                                    </tr>
                                    <tr className={`border-b ${rowBg}`}>
                                        <td className="px-2 py-1 text-muted-foreground">FAN</td>
                                        <td className="px-2 py-1"></td>
                                        {cols.map(([lbl, , fanKey]) => {
                                            const isTotal = fanKey === 'FAN_total'
                                            const val = game[fanKey]
                                            return (
                                                <td key={lbl} className={`px-2 py-1 text-right tabular-nums ${isTotal ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''}`}>
                                                    {fmt(val)}
                                                </td>
                                            )
                                        })}
                                    </tr>
                                </React.Fragment>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default function PlayerDetail() {
    const { playerid } = useParams()
    const [player, setPlayer] = useState(null)
    const [season, setSeason] = useState(null)
    const [hitStats, setHitStats] = useState(null)
    const [pitchStats, setPitchStats] = useState(null)
    const [hitLog, setHitLog] = useState(null)
    const [pitchLog, setPitchLog] = useState(null)
    const [globalRanges, setGlobalRanges] = useState({})

    useEffect(() => {
        axios.get(`/api/player?playerid=${playerid}`).then(r => setPlayer(r.data)).catch(console.error)
        axios.get('/api/season').then(r => setSeason(r.data.season)).catch(console.error)
    }, [playerid])

    useEffect(() => {
        if (!season || !playerid) return
        axios.get(`/api/player/${playerid}/season/${season}/hit`).then(r => setHitStats(r.data)).catch(() => setHitStats(null))
        axios.get(`/api/player/${playerid}/season/${season}/pitch`).then(r => setPitchStats(r.data)).catch(() => setPitchStats(null))
        axios.get(`/api/statlines/batting?playerid=${playerid}&year=${season}`).then(r => setHitLog(r.data)).catch(() => setHitLog([]))
        axios.get(`/api/statlines/pitching?playerid=${playerid}&year=${season}`).then(r => setPitchLog(r.data)).catch(() => setPitchLog([]))
    }, [playerid, season])

    useEffect(() => {
        if (!season || !player) return
        const type = player.positions?.some(p => ['SP', 'RP'].includes(p)) ? 'pitch' : 'hit'
        axios.get(`/api/players/${season}/${type}/column-ranges`).then(r => setGlobalRanges(r.data)).catch(() => {})
    }, [season, player])

    if (!player) return <div className="p-4 text-sm text-muted-foreground">Loading...</div>

    const isPitcher = player.positions?.some(p => ['SP', 'RP'].includes(p))
    const stats = isPitcher ? pitchStats : hitStats
    const statCols = isPitcher ? PITCH_COLS : HIT_COLS
    const logRows = isPitcher ? pitchLog : hitLog
    const logType = isPitcher ? 'pitch' : 'hit'

    return (
        <div className="p-4 w-full">
            <div className="mb-4">
                <h2 className="text-xl font-semibold">{player.name}</h2>
                <div className="flex gap-3 mt-1 text-sm text-muted-foreground justify-center">
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
                <SeasonStatsTable stats={stats} cols={statCols} globalRanges={globalRanges} />
            )}
            <TodayStatlines playerid={playerid} isPitcher={isPitcher} />
            <GameLog rows={logRows} type={logType} />
        </div>
    )
}
