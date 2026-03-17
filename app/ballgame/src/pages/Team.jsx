import { useState, useEffect } from 'react'
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
]

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
                <th key={key} className={`px-3 py-2 font-medium text-right first:text-left ${key === 'FAN_total' ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300' : 'text-muted-foreground'}`}>
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
                  const display = val == null ? '-' : (isFan || key === 'ip') ? Number(val).toFixed(1) : val
                  return (
                    <td key={key} className={`px-3 py-1.5 tabular-nums ${isDate || isPlayer || isType ? 'text-left' : 'text-right'} ${isFan ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''}`}>
                      {isType && val ? (
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

const NON_SUMMABLE = new Set(['slot', 'name', 'positions', 'team_assigned', 'game_type'])

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
                  className={`px-3 py-1.5 tabular-nums text-right ${cell.column.id === 'slot' || cell.column.id === 'name' ? 'text-left' : ''} ${meta?.highlight ? 'bg-orange-50 dark:bg-orange-950/40 font-bold text-orange-900 dark:text-orange-200' : ''} ${meta?.className ?? ''}`}>
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

function DayLineupTable({ data, scoreType }) {
  if (!data) return <p className="text-sm text-muted-foreground">Loading...</p>

  const hitCols = [SLOT_COL, GAME_TYPE_COL, ...columnData[`${scoreType}_columns_hit`]]
  const pitchCols = [SLOT_COL, GAME_TYPE_COL, ...columnData[`${scoreType}_columns_pitch`]]

  const dayTotal = [
    ...data.hitters.filter(r => !r.game_type || r.game_type === 'R').map(r => r.FAN_total ?? 0),
    ...data.pitchers.filter(r => !r.game_type || r.game_type === 'R').map(r => r.FAN_total ?? 0),
  ].reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-end">
        <span className="text-sm font-semibold">
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

function YesterdayTable({ team }) {
  const [data, setData] = useState(null)
  const [scoreType, setScoreType] = useState('FAN')

  const activeClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
  const inactiveClass = 'bg-muted text-foreground hover:bg-muted/80'

  useEffect(() => {
    if (!team) return
    setData(null)
    axios.get('/api/lineup/yesterday', { params: { team } })
      .then(r => setData(r.data))
      .catch(() => setData({ hitters: [], pitchers: [], date: '' }))
  }, [team])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex rounded-md border overflow-hidden text-sm w-fit">
          {['FAN', 'RAW'].map(s => (
            <button key={s} onClick={() => setScoreType(s)}
              className={`px-3 py-1 ${scoreType === s ? activeClass : inactiveClass}`}>
              {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
            </button>
          ))}
        </div>
        {data?.date && <span className="text-xs text-muted-foreground">{data.date}</span>}
      </div>
      <DayLineupTable data={data} scoreType={scoreType} />
    </div>
  )
}

function TodayTable({ team }) {
  const [data, setData] = useState(null)
  const [scoreType, setScoreType] = useState('FAN')

  const activeClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
  const inactiveClass = 'bg-muted text-foreground hover:bg-muted/80'

  useEffect(() => {
    if (!team) return
    setData(null)
    const localDate = new Date().toLocaleDateString('en-CA') // YYYY-MM-DD in local tz
    axios.get('/api/lineup/today', { params: { team, date: localDate } })
      .then(r => setData(r.data))
      .catch(() => setData({ hitters: [], pitchers: [], date: '' }))
  }, [team])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex rounded-md border overflow-hidden text-sm w-fit">
          {['FAN', 'RAW'].map(s => (
            <button key={s} onClick={() => setScoreType(s)}
              className={`px-3 py-1 ${scoreType === s ? activeClass : inactiveClass}`}>
              {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
            </button>
          ))}
        </div>
        {data?.date && <span className="text-xs text-muted-foreground">{data.date}</span>}
      </div>
      <DayLineupTable data={data} scoreType={scoreType} />
    </div>
  )
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
  const [season, setSeason] = useState(null)
  const [view, setView] = useState('season')
  const [teamInfo, setTeamInfo] = useState(null)

  const activeClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
  const inactiveClass = 'bg-muted text-foreground hover:bg-muted/80'

  useEffect(() => {
    axios.get('/api/season').then(r => setSeason(r.data.season)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!displayTeam) return
    axios.get(`/api/team/${displayTeam}`).then(r => setTeamInfo(r.data)).catch(() => {})
  }, [displayTeam])

  useEffect(() => {
    if (!displayTeam) return
    axios.get('/api/lineup', { params: { team: displayTeam } })
      .then(res => {
        const lineup = res.data
        const open = []
        for (const [slot, pos] of Object.entries(SLOT_POSITIONS)) {
          if (!lineup[slot]) open.push(pos)
        }
        if (open.includes('OF')) { open.push('LF'); open.push('CF'); open.push('RF') }
        if (open.includes('UTIL')) open.push(...['C','1B','2B','SS','3B','LF','CF','RF','OF','DH'])
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
          <TeamScore team={displayTeam} season={season} />
        </div>
        <div className="min-w-[200px]">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Sombrero Cup</p>
          <SombreroTable team={displayTeam} season={season} />
        </div>
      </div>
      <div className="flex rounded-md border overflow-hidden text-sm w-fit">
        {[['season', 'Season'], ['yesterday', 'Yesterday'], ['today', 'Today']].map(([val, label]) => (
          <button key={val} onClick={() => setView(val)}
            className={`px-3 py-1 ${view === val ? activeClass : inactiveClass}`}>
            {label}
          </button>
        ))}
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
              hideControls={false}
              readOnly={readOnly}
              tableHeight="auto"
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
              hideControls={false}
              readOnly={readOnly}
              tableHeight="auto"
            />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Best Performances</p>
            <BestPerformances team={displayTeam} season={season} />
          </div>
        </>
      ) : view === 'yesterday' ? (
        <YesterdayTable team={displayTeam} />
      ) : (
        <TodayTable team={displayTeam} />
      )}
    </div>
  )
}
