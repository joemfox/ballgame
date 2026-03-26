import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'
import StatlineTable from '@/components/StatlineTable.jsx'
import columnData from '@/lib/dataColumns'

const PERF_COLS = [
  ['Date', 'date'],
  ['Player', 'player_name'],
  ['', 'type'],
  ['IP', 'ip'],
  ['ER', 'er'],
  ['AB', 'ab'],
  ['H', 'h'],
  ['HR', 'hr'],
  ['RBI', 'rbi'],
  ['R', 'r'],
  ['SB', 'sb'],
  ['K', 'k'],
  ['FAN', 'FAN_total'],
  ['', 'summary'],
]

function perfSummary(row) {
  if (row.type === 'H') {
    const base = row.ab != null ? `${row.h ?? 0}-${row.ab}` : null
    const bits = []
    if ((row.hr ?? 0) > 0) bits.push(`${row.hr} HR`)
    if ((row.rbi ?? 0) > 0) bits.push(`${row.rbi} RBI`)
    if ((row.r ?? 0) > 0) bits.push(`${row.r} R`)
    if ((row.sb ?? 0) > 0) bits.push(`${row.sb} SB`)
    if ((row.bb ?? 0) > 0) bits.push(`${row.bb} BB`)
    if ((row.k ?? 0) > 0) bits.push(`${row.k} K`)
    return base ? [base, ...bits].join(', ') : bits.join(', ')
  }
  if (row.type === 'P' && row.ip != null) {
    const whole = Math.floor(row.ip)
    const frac = Math.round((row.ip % 1) * 10)
    const ipStr = frac === 0 ? `${whole} IP` : whole > 0 ? `${whole} ${frac}/3 IP` : `${frac}/3 IP`
    const br = (row.h ?? 0) + (row.bb ?? 0) + (row.hb ?? 0)
    const outs = whole * 3 + frac
    const bf = outs + br
    const parts = [`${ipStr} (${br} BR of ${bf} BF)`]
    if ((row.er ?? 0) > 0) parts.push(`${row.er} runs`)
    if ((row.k ?? 0) > 0) parts.push(`${row.k} K`)
    if ((row.hr ?? 0) > 0) parts.push(`${row.hr} HR`)
    return parts.join(', ')
  }
  return null
}

function BestPerformances({ team, season }) {
  const [page, setPage] = useState(1)
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!team || !season) return
    setData(null)
    axios.get('/api/statlines/team', { params: { team, year: season, page } })
      .then(r => setData(r.data))
      .catch(() => setData({ results: [], count: 0 }))
  }, [team, season, page])

  if (!data) return <p className="text-sm text-muted-foreground">Loading...</p>
  if (!data.results.length) return <p className="text-sm text-muted-foreground">No game data.</p>

  const totalPages = Math.ceil(data.count / 5)

  return (
    <div>
      <div className="overflow-x-auto rounded-md border">
        <table className="text-sm geist-mono w-full">
          <thead className="sticky top-0 z-10">
            <tr className="border-b bg-muted/50">
              {PERF_COLS.map(([label, key]) => (
                <th key={key} className={`px-3 py-2 font-medium ${key === 'summary' ? 'text-left' : 'text-right first:text-left'} ${key === 'FAN_total' ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'}`}>
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.results.map((row, i) => (
              <tr key={i} className="border-b last:border-0 hover:bg-muted/40">
                {PERF_COLS.map(([, key]) => {
                  const val = row[key]
                  const isFan = key === 'FAN_total'
                  const isDate = key === 'date'
                  const isPlayer = key === 'player_name'
                  const isType = key === 'type'
                  const isSummary = key === 'summary'
                  const display = val == null ? '-' : (isFan || key === 'ip') ? Number(val).toFixed(1) : val
                  return (
                    <td key={key} className={`px-3 py-1.5 tabular-nums ${isDate || isPlayer || isType || isSummary ? 'text-left' : 'text-right'} ${isFan ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''}`}>
                      {isSummary ? (
                        <span className="text-sm text-muted-foreground whitespace-nowrap">{perfSummary(row)}</span>
                      ) : isType && val ? (
                        <span className={`text-xs px-1 py-0.5 rounded font-semibold ${val === 'H' ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' : 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300'}`}>{val}</span>
                      ) : isPlayer && row.fg_id ? (
                        <Link to={`/player/${row.fg_id}`} className="hover:underline">{val}</Link>
                      ) : display}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-2 text-sm text-muted-foreground">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-2 py-1 rounded border border-input disabled:opacity-40 hover:bg-muted">Prev</button>
          <span>Page {page} of {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-2 py-1 rounded border border-input disabled:opacity-40 hover:bg-muted">Next</button>
        </div>
      )}
    </div>
  )
}

const SLOT_POSITIONS = {
  lineup_C: 'C', lineup_1B: '1B', lineup_2B: '2B', lineup_SS: 'SS', lineup_3B: '3B',
  lineup_OF1: 'OF', lineup_OF2: 'OF', lineup_OF3: 'OF', lineup_OF4: 'OF', lineup_OF5: 'OF',
  lineup_DH: 'DH', lineup_UTIL: 'UTIL',
  lineup_SP1: 'SP', lineup_SP2: 'SP', lineup_SP3: 'SP', lineup_SP4: 'SP', lineup_SP5: 'SP',
  lineup_RP1: 'RP', lineup_RP2: 'RP', lineup_RP3: 'RP',
}

const HITTER_SLOTS = ['lineup_C','lineup_1B','lineup_2B','lineup_SS','lineup_3B','lineup_OF1','lineup_OF2','lineup_OF3','lineup_OF4','lineup_OF5','lineup_DH','lineup_UTIL']
const PITCHER_SLOTS = ['lineup_SP1','lineup_SP2','lineup_SP3','lineup_SP4','lineup_SP5','lineup_RP1','lineup_RP2','lineup_RP3']

function ordinal(n) {
  const s = ['th','st','nd','rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

const RANK_CLASS = {
  1: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200 border-yellow-300 dark:border-yellow-700',
  2: 'bg-slate-100 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 border-slate-300 dark:border-slate-600',
  3: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700',
}

function TeamScore({ team, season }) {
  const [entry, setEntry] = useState(null)
  const [rank, setRank] = useState(null)

  useEffect(() => {
    if (!team || !season) return
    axios.get(`/api/standings/${season}`)
      .then(r => {
        const idx = r.data.findIndex(s => s.team === team)
        if (idx >= 0) { setEntry(r.data[idx]); setRank(idx + 1) }
      })
      .catch(() => {})
  }, [team, season])

  if (!entry) return null

  const rankClass = RANK_CLASS[rank] || 'bg-muted text-muted-foreground border-border'

  return (
    <div className="flex items-center gap-4 pb-2">
      <div className="text-5xl font-bold tabular-nums">{entry.total.toFixed(1)}</div>
      <div className={`text-3xl font-bold px-4 py-1.5 rounded-xl border-2 ${rankClass}`}>{ordinal(rank)}</div>
      <div className="text-sm text-muted-foreground leading-relaxed">
        <div>Bat: {entry.bat_total.toFixed(1)}</div>
        <div>Pitch: {entry.pitch_total.toFixed(1)}</div>
      </div>
    </div>
  )
}

const SLOT_COL = {
  id: 'slot',
  accessorKey: 'slot',
  header: 'Slot',
  meta: { pinned: true, width: 60 },
  cell: ({ row }) => <div className="text-left">{row.getValue('slot')}</div>,
}

const NON_SUMMABLE = new Set(['slot', 'name', 'positions', 'team_assigned', 'game_type', 'summary'])

function StatTable({ rows, columns }) {
  const table = useReactTable({ data: rows, columns, getCoreRowModel: getCoreRowModel() })

  // Compute column sums for the total row — only count R (scoring) games
  const scoringRows = rows.filter(r => !r.game_type || r.game_type === 'R')
  const totals = {}
  for (const col of columns) {
    const key = col.accessorKey
    if (!key || NON_SUMMABLE.has(col.id ?? key)) continue
    const sum = scoringRows.reduce((acc, row) => {
      const v = row[key]
      return typeof v === 'number' ? acc + v : acc
    }, 0)
    const hasAny = scoringRows.some(row => row[key] != null)
    totals[key] = hasAny ? sum : null
  }

  return (
    <div className="overflow-x-auto rounded-md border">
      <table className="text-sm geist-mono w-full">
        <thead>
          <tr className="border-b bg-muted/50">
            {table.getHeaderGroups()[0].headers.map(header => {
              const meta = header.column.columnDef.meta
              const widthStyle = meta?.width ? { minWidth: meta.width, maxWidth: meta.width } : {}
              return (
                <th key={header.id}
                  style={widthStyle}
                  className={`px-3 py-2 font-medium text-right first:text-left ${meta?.highlight ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'} ${meta?.className ?? ''}`}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row, i) => {
            const gt = row.original.game_type
            const rowBg = gt && gt !== 'R'
              ? SPRING_TYPES.has(gt) ? 'bg-green-50/60 dark:bg-green-950/20' : 'bg-yellow-50/60 dark:bg-yellow-950/20'
              : ''
            return (
            <tr key={i} className={`border-b hover:bg-muted/40 ${rowBg}`}>
              {row.getVisibleCells().map(cell => {
                const meta = cell.column.columnDef.meta
                const widthStyle = meta?.width ? { minWidth: meta.width, maxWidth: meta.width } : {}
                return (
                <td key={cell.id}
                  style={widthStyle}
                  className={`px-3 py-1.5 tabular-nums ${['slot', 'name', 'game_type', 'summary'].includes(cell.column.id) ? 'text-left' : 'text-right'} ${meta?.highlight ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''} ${meta?.className ?? ''}`}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              )})}
            </tr>
          )})}
        </tbody>
        <tfoot>
          <tr className="border-t-2 bg-muted/30 font-semibold">
            {columns.map((col, i) => {
              const key = col.accessorKey
              const id = col.id ?? key
              const meta = col.meta
              const widthStyle = meta?.width ? { minWidth: meta.width, maxWidth: meta.width } : {}
              let content = ''
              if (id === 'slot') content = 'Total'
              else if (!NON_SUMMABLE.has(id) && key && totals[key] != null) {
                const v = totals[key]
                content = v % 1 === 0 ? v : v.toFixed(1)
              }
              return (
                <td key={id}
                  style={widthStyle}
                  className={`px-3 py-1.5 tabular-nums text-right ${id === 'slot' ? 'text-left text-muted-foreground font-bold' : ''} ${meta?.highlight ? 'bg-orange-100 dark:bg-orange-950/60 font-bold text-orange-900 dark:text-orange-200' : ''} ${meta?.className ?? ''}`}>
                  {content}
                </td>
              )
            })}
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

const SPRING_TYPES = new Set(['S', 'E'])
const POST_TYPES = new Set(['D', 'L', 'W', 'F', 'P', 'A'])
const GAME_TYPE_SHORT = { S: 'ST', E: 'EX', A: 'AS', D: 'DS', L: 'LCS', W: 'WS', F: 'WC', P: 'PS' }

const HITTER_HIGHLIGHTS = [
  // [rawKey, fanKey, labelFn]
  ['hr',              'FAN_hr',              (n)    => `${n} HR`],
  ['k',               'FAN_k',               (n, r) => r.k_looking > 0 ? `${n} K (${r.k_looking} looking)` : `${n} K`],
  ['cs',              'FAN_cs',              (n)    => `${n} CS`],
  ['rl2o',            'FAN_rl2o',            (n)    => `${n} RL2O`],
  ['gidp',            'FAN_gidp',            (n)    => `${n} GIDP`],
  ['triples',         'FAN_triples',         (n)    => `${n} 3B`],
  ['doubles',         'FAN_doubles',         (n)    => `${n} 2B`],
  ['sb',              'FAN_sb',              (n)    => `${n} SB`],
  ['bb',              'FAN_bb',              (n)    => `${n} BB`],
  ['lob',             'FAN_lob',             (n)    => `${n} LOB`],
  ['e',               'FAN_e',               (n)    => `${n} E`],
  ['po',              'FAN_po',              (n)    => `${n} PO`],
  ['outfield_assists','FAN_outfield_assists', (n)    => `${n} OA`],
  ['cycle',           'FAN_cycle',           ()     => 'Cycle'],
  ['rbi',             'FAN_rbi',             (n)    => `${n} RBI`],
  ['r',               'FAN_r',               (n)    => `${n} R`],
]

const HITTER_SUMMARY_COL = {
  id: 'summary',
  header: '',
  cell: ({ row }) => {
    const r = row.original
    if (r.ab == null) return null
    const base = `${r.h ?? 0}-${r.ab}`
    const highlights = HITTER_HIGHLIGHTS
      .filter(([rawKey]) => (r[rawKey] ?? 0) > 0)
      .map(([rawKey, fanKey, labelFn]) => ({ label: labelFn(r[rawKey], r), impact: Math.abs(r[fanKey] ?? 0) }))
      .filter(c => c.impact > 0)
      .sort((a, b) => b.impact - a.impact)
      .slice(0, 2)
      .map(c => c.label)
    return <span className="text-left text-sm text-muted-foreground whitespace-nowrap">{[base, ...highlights].join(', ')}</span>
  },
}

function formatIP(ip) {
  if (ip == null) return null
  const whole = Math.floor(ip)
  const frac = Math.round((ip % 1) * 10)
  if (frac === 0) return whole === 1 ? '1 IP' : `${whole} IP`
  return whole > 0 ? `${whole} ${frac}/3 IP` : `${frac}/3 IP`
}

const PITCHER_HIGHLIGHTS = [
  ['hr',           'FAN_hr',           (n) => `${n} HR`],
  ['hb',           'FAN_hb',           (n) => `${n} HBP`],
  ['bs',           'FAN_bs',           (n) => `${n} BS`],
  ['k',            'FAN_k',            (n) => `${n} K`],
  ['bb',           'FAN_bb',           (n) => `${n} BB`],
  ['wp',           'FAN_wp',           (n) => `${n} WP`],
  ['balks',        'FAN_balks',        (n) => `${n} BALK`],
  ['e',            'FAN_e',            (n) => `${n} E`],
  ['ir',           'FAN_ir',           (n) => `${n} IR`],
  ['dpi',          'FAN_dpi',          (n) => `${n} DPI`],
  ['relief_loss',  'FAN_relief_loss',  ()  => 'RL'],
  ['no_hitter',    'FAN_no_hitter',    ()  => 'NH'],
  ['perfect_game', 'FAN_perfect_game', ()  => 'PG'],
]

const PITCHER_SUMMARY_COL = {
  id: 'summary',
  header: '',
  cell: ({ row }) => {
    const r = row.original
    if (r.ip == null) return null
    const outs = Math.floor(r.ip) * 3 + Math.round((r.ip % 1) * 10)
    const br = (r.h ?? 0) + (r.bb ?? 0) + (r.hb ?? 0)
    const bf = outs + br
    const parts = [`${formatIP(r.ip)} (${br} BR of ${bf} BF)`]
    if ((r.er ?? 0) > 0) parts.push(`${r.er} runs`)
    const highlights = PITCHER_HIGHLIGHTS
      .filter(([rawKey]) => (r[rawKey] ?? 0) > 0)
      .map(([rawKey, fanKey, labelFn]) => ({ label: labelFn(r[rawKey], r), impact: Math.abs(r[fanKey] ?? 0) }))
      .filter(c => c.impact > 0)
      .sort((a, b) => b.impact - a.impact)
      .slice(0, 2)
      .map(c => c.label)
    return <span className="text-left text-sm text-muted-foreground whitespace-nowrap">{[...parts, ...highlights].join(', ')}</span>
  },
}

function insertAfterFanTotal(cols, summaryCol) {
  const idx = cols.findIndex(c => c.accessorKey === 'FAN_total')
  if (idx < 0) return cols
  return [...cols.slice(0, idx + 1), summaryCol, ...cols.slice(idx + 1)]
}

const GAME_TYPE_COL = {
  id: 'game_type',
  accessorKey: 'game_type',
  header: '',
  meta: { width: 36 },
  cell: ({ row }) => {
    const gt = row.getValue('game_type')
    if (!gt || gt === 'R') return null
    const label = GAME_TYPE_SHORT[gt] ?? gt
    const cls = SPRING_TYPES.has(gt)
      ? 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300'
      : 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200'
    return <span className={`text-xs px-1 py-0.5 rounded font-semibold ${cls}`}>{label}</span>
  },
}

function DayLineupTable({ data, date, scoreType }) {
  if (!data) return <p className="text-sm text-muted-foreground">Loading...</p>

  const hitCols = [SLOT_COL, GAME_TYPE_COL, ...insertAfterFanTotal(columnData[`${scoreType}_columns_hit`], HITTER_SUMMARY_COL)]
  const pitchCols = [SLOT_COL, GAME_TYPE_COL, ...insertAfterFanTotal(columnData[`${scoreType}_columns_pitch`], PITCHER_SUMMARY_COL)]

  const dayTotal = [
    ...data.hitters.filter(r => !r.game_type || r.game_type === 'R').map(r => r.FAN_total ?? 0),
    ...data.pitchers.filter(r => !r.game_type || r.game_type === 'R').map(r => r.FAN_total ?? 0),
  ].reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        {date && <span className="text-xs text-muted-foreground">{date}</span>}
        <span className="text-sm font-semibold ml-auto">
          <span className="text-muted-foreground font-normal">Team total: </span>
          <span className="text-orange-800 dark:text-orange-300">{dayTotal.toFixed(1)} FAN pts</span>
        </span>
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Hitters</p>
        {data.hitters.length ? <StatTable rows={data.hitters} columns={hitCols} /> : <p className="text-sm text-muted-foreground">No hitters in lineup.</p>}
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Pitchers</p>
        {data.pitchers.length ? <StatTable rows={data.pitchers} columns={pitchCols} /> : <p className="text-sm text-muted-foreground">No pitchers in lineup.</p>}
      </div>
    </div>
  )
}

function YesterdayTable({ team, scoreType }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!team) return
    setData(null)
    axios.get('/api/lineup/yesterday', { params: { team } })
      .then(r => setData(r.data))
      .catch(() => setData({ hitters: [], pitchers: [], date: '' }))
  }, [team])

  return <DayLineupTable data={data} date={data?.date} scoreType={scoreType} />
}

function TodayTable({ team, scoreType }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!team) return
    setData(null)
    const localDate = new Date().toLocaleDateString('en-CA') // YYYY-MM-DD in local tz
    axios.get('/api/lineup/today', { params: { team, date: localDate } })
      .then(r => setData(r.data))
      .catch(() => setData({ hitters: [], pitchers: [], date: '' }))
  }, [team])

  return <DayLineupTable data={data} date={data?.date} scoreType={scoreType} />
}

function SombreroTable({ team, season }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!season) return
    axios.get(`/api/standings/sombrero/${season}`)
      .then(r => setData(r.data))
      .catch(() => setData([]))
  }, [season])

  if (!data) return <p className="text-sm text-muted-foreground">Loading...</p>
  if (!data.length) return <p className="text-sm text-muted-foreground">No sombreros yet for {season}.</p>

  return (
    <table className="w-full text-sm border rounded-md overflow-hidden">
      <thead>
        <tr className="border-b bg-muted">
          <th className="text-left px-3 py-2 font-medium">#</th>
          <th className="text-left px-3 py-2 font-medium">Team</th>
          <th className="text-right px-3 py-2 font-medium">Sombreros</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={row.team} className={`border-b last:border-0 hover:bg-muted/50 ${row.team === team ? 'bg-orange-50 dark:bg-orange-950/30' : ''}`}>
            <td className="px-3 py-2 text-muted-foreground">{i + 1}</td>
            <td className={`px-3 py-2 font-medium ${row.team === team ? 'text-orange-900 dark:text-orange-200' : ''}`}>
              <Link to={`/team/${row.team}`} className="hover:underline">{row.team_name || row.team}</Link>
            </td>
            <td className={`px-3 py-2 text-right tabular-nums font-bold ${row.team === team ? 'text-orange-900 dark:text-orange-200' : ''}`}>{row.sombrero}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function Team({ team, viewTeam, rosterVersion = 0, onRosterChange }) {
  const displayTeam = viewTeam ?? team
  const readOnly = viewTeam != null && viewTeam !== team

  const [openPositions, setOpenPositions] = useState([])
  const [lineup, setLineup] = useState(null)
  const [season, setSeason] = useState(null)
  const [upcomingSeason, setUpcomingSeason] = useState(null)
  const [view, setView] = useState('season')
  const [scoreType, setScoreType] = useState('FAN')
  const [teamInfo, setTeamInfo] = useState(null)

  const activeClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
  const inactiveClass = 'bg-muted text-foreground hover:bg-muted/80'

  const hitSlotMap = useMemo(() => lineup
    ? Object.fromEntries(HITTER_SLOTS.map(s => [lineup[s]?.fg_id, SLOT_POSITIONS[s]]).filter(([id]) => id))
    : {}, [lineup])
  const pitchSlotMap = useMemo(() => lineup
    ? Object.fromEntries(PITCHER_SLOTS.map(s => [lineup[s]?.fg_id, SLOT_POSITIONS[s]]).filter(([id]) => id))
    : {}, [lineup])
  const hitOrder = useMemo(() => lineup
    ? HITTER_SLOTS.map(s => lineup[s]?.fg_id).filter(Boolean)
    : null, [lineup])
  const pitchOrder = useMemo(() => lineup
    ? PITCHER_SLOTS.map(s => lineup[s]?.fg_id).filter(Boolean)
    : null, [lineup])
  const hitSlotCol = useMemo(() => ({
    id: 'slot', header: 'Slot', meta: { pinned: true, width: 50 },
    cell: ({ row }) => <div className="text-left text-xs text-muted-foreground font-semibold">{hitSlotMap[row.original.fg_id] ?? ''}</div>,
  }), [hitSlotMap])
  const pitchSlotCol = useMemo(() => ({
    id: 'slot', header: 'Slot', meta: { pinned: true, width: 50 },
    cell: ({ row }) => <div className="text-left text-xs text-muted-foreground font-semibold">{pitchSlotMap[row.original.fg_id] ?? ''}</div>,
  }), [pitchSlotMap])

  useEffect(() => {
    axios.get('/api/season').then(r => { setSeason(r.data.season); setUpcomingSeason(r.data.upcoming_season) }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!displayTeam) return
    axios.get(`/api/team/${displayTeam}`).then(r => setTeamInfo(r.data)).catch(() => {})
  }, [displayTeam])

  useEffect(() => {
    if (!displayTeam) return
    axios.get('/api/lineup', { params: { team: displayTeam } })
      .then(res => {
        const lineupData = res.data
        setLineup(lineupData)
        const open = []
        for (const [slot, pos] of Object.entries(SLOT_POSITIONS)) {
          if (!lineupData[slot]) open.push(pos)
        }
        if (open.includes('OF')) { open.push('LF'); open.push('CF'); open.push('RF') }
        if (open.includes('DH')) open.push(...['C','1B','2B','SS','3B','LF','CF','RF','OF','IF','IF-OF'])
        if (open.includes('UTIL')) open.push(...['C','1B','2B','SS','3B','LF','CF','RF','OF','DH','IF','IF-OF'])
        if (['2B', 'SS', '3B'].some(p => open.includes(p))) { open.push('IF'); open.push('IN') }
        setOpenPositions([...new Set(open)])
      })
      .catch(() => setOpenPositions([]))
  }, [displayTeam, rosterVersion])

  return (
    <div className="space-y-8">
      {teamInfo && (
        <h1 className="text-2xl font-bold">{teamInfo.city} {teamInfo.nickname}</h1>
      )}
      <div className="flex flex-col sm:flex-row gap-8 sm:justify-between">
        <div className="space-y-4 flex items-center">
          <TeamScore team={displayTeam} season={upcomingSeason} />
        </div>
        <div className="min-w-[200px]">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Sombrero Cup</p>
          <SombreroTable team={displayTeam} season={upcomingSeason} />
        </div>
      </div>
      <div className="space-y-2">
        <div className="flex rounded-md border overflow-hidden text-sm w-fit">
          {[['season', 'Season'], ['yesterday', 'Yesterday'], ['today', 'Today']].map(([val, label]) => (
            <button key={val} onClick={() => setView(val)}
              className={`px-3 py-1 ${view === val ? activeClass : inactiveClass}`}>
              {label}
            </button>
          ))}
        </div>
        <div className="flex rounded-md border overflow-hidden text-sm w-fit">
          {['FAN', 'RAW'].map(s => (
            <button key={s} onClick={() => setScoreType(s)}
              className={`px-3 py-1 ${scoreType === s ? activeClass : inactiveClass}`}>
              {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
            </button>
          ))}
        </div>
      </div>

      {view === 'season' ? (
        <>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Hitters</p>
            <StatlineTable
              type="hit"
              team={displayTeam}
              openPositions={openPositions}
              rosterVersion={rosterVersion}
              onRosterChange={onRosterChange}
              defaultOwnershipFilter="mine"
              ownershipOptions={['mine']}
              hideControls={true}
              readOnly={true}
              tableHeight="auto"
              externalScoreType={scoreType}
              playerOrder={hitOrder}
              customActionColumn={hitSlotCol}
            />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Pitchers</p>
            <StatlineTable
              type="pitch"
              team={displayTeam}
              openPositions={openPositions}
              rosterVersion={rosterVersion}
              onRosterChange={onRosterChange}
              defaultOwnershipFilter="mine"
              ownershipOptions={['mine']}
              hideControls={true}
              readOnly={true}
              tableHeight="auto"
              externalScoreType={scoreType}
              playerOrder={pitchOrder}
              customActionColumn={pitchSlotCol}
            />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Best Performances</p>
            <BestPerformances team={displayTeam} season={upcomingSeason} />
          </div>
        </>
      ) : view === 'yesterday' ? (
        <YesterdayTable team={displayTeam} scoreType={scoreType} />
      ) : (
        <TodayTable team={displayTeam} scoreType={scoreType} />
      )}
    </div>
  )
}
