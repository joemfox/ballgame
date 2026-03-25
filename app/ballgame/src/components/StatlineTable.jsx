import React, {useEffect, useState, useMemo, useRef} from 'react'
import { flexRender, getCoreRowModel, useReactTable  } from "@tanstack/react-table"
import axios from 'axios'

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PositionSelectDropdown } from './PositionDropdown'
import columnData from '../lib/dataColumns'

// Maps raw stat keys to their FAN equivalents for color-direction lookup
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

export default function DataTable({
    type,
    team,
    openPositions,
    rosterVersion,
    onRosterChange,
    customActionColumn,
    defaultOwnershipFilter = 'all',
    ownershipOptions,
    hideControls = false,
    readOnly = false,
    tableHeight = 'calc(100vh - 200px)',
    playerOrder = null,
    externalScoreType = null,
}) {
    const [players, setPlayers] = useState([])
    const [{ pageIndex, pageSize }, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
    const [pageCount, setPageCount] = useState(-1)
    const [season, setSeason] = useState(null)
    const [_scoreType, setScoreType] = useState('FAN')
    const scoreType = externalScoreType ?? _scoreType
    const [ownershipFilter, setOwnershipFilter] = useState(defaultOwnershipFilter)
    const [metrics, setMetrics] = useState([])
    const [sumTotal, setSumTotal] = useState(null)
    const [isScrolled, setIsScrolled] = useState(false)
    const [globalRanges, setGlobalRanges] = useState({})
    const tableWrapperRef = useRef(null)

    const baseColumns = columnData[`${scoreType}_columns_${type}`]

    const actionColumn = {
        id: 'actions',
        header: '',
        meta: { pinned: true, width: 72 },
        cell: ({ row }) => {
            const { fg_id, team_assigned, positions } = row.original
            if (!team) return null
            if (team_assigned === team) {
                return (
                    <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-800"
                        onClick={() => { if (window.confirm('Drop this player?')) rosterDrop(fg_id) }}>Drop</Button>
                )
            }
            if (!team_assigned) {
                const canAdd = openPositions && positions && positions.some(p => openPositions.includes(p))
                return (
                    <Button variant="ghost" size="sm" disabled={!canAdd}
                        onClick={() => lineupAdd(fg_id)}>Add</Button>
                )
            }
            return <span className="text-xs text-muted-foreground">{team_assigned}</span>
        }
    }

    const resolvedActionColumn = customActionColumn ?? (team && !readOnly ? actionColumn : null)
    const columns = resolvedActionColumn ? [resolvedActionColumn, ...baseColumns] : baseColumns

    const pinnedOffsets = useMemo(() => {
        const offsets = {}
        let left = 0
        for (const col of columns) {
            if (col.meta?.pinned) {
                const id = col.id ?? col.accessorKey
                offsets[id] = left
                left += col.meta.width ?? 0
            }
        }
        return offsets
    }, [columns])

    const lastPinnedId = useMemo(() => {
        const keys = Object.keys(pinnedOffsets)
        return keys.length ? keys[keys.length - 1] : null
    }, [pinnedOffsets])

    function getShadeStyle(val, range, colorRange) {
        if (!range || range.min === null || range.max === null || range.min === range.max) return {}
        if (typeof val !== 'number') return {}
        const { min, max } = range
        // Use colorRange (FAN equivalent) to determine color direction if provided,
        // otherwise fall back to the value range itself.
        const cr = (colorRange && colorRange.min !== null && colorRange.max !== null) ? colorRange : range
        // Cubic curve: compresses the bottom 90% to subtle shading,
        // leaving strong highlights only for the top ~10% of values.
        const shade = (t) => `${(Math.pow(Math.max(0, Math.min(1, t)), 3) * 0.18).toFixed(3)}`
        const t = min === max ? 0 : (val - min) / (max - min)
        // isRaw: we have a separate colorRange (FAN equivalent), so this is a raw counting stat.
        // Raw stats are always non-negative counts — higher = more extreme, so always use shade(t).
        // FAN stats can be negative — most-negative is most extreme, so use shade(1-t) for neg columns.
        const isRaw = colorRange !== null
        if (cr.max <= 0) {
            const intensity = isRaw ? t : (1 - t)
            return { backgroundColor: `rgba(112, 0, 160, ${shade(intensity)})` }
        } else if (cr.min >= 0) {
            return { backgroundColor: `rgba(0, 255, 100, ${shade(t)})` }
        } else {
            // Mixed FAN column: split on sign
            if (val >= 0) {
                return { backgroundColor: `rgba(0, 255, 100, ${shade(t)})` }
            } else {
                return { backgroundColor: `rgba(112, 0, 160, ${shade(1 - t)})` }
            }
        }
    }

    useEffect(() => {
        const el = tableWrapperRef.current
        if (!el) return
        const handler = () => setIsScrolled(el.scrollLeft > 0)
        el.addEventListener('scroll', handler, { passive: true })
        return () => el.removeEventListener('scroll', handler)
    }, [])

    const defaultSort = {desc: true, id: 'FAN_total'}
    const [sorting, setSorting] = useState([defaultSort])

    const [filters, setColumnFilters] = useState([])
    const [positionFilters, setPositionFilters] = useState({
        "C": false, "1B": false, "2B": false, "SS": false, "3B": false,
        "LF": false, "CF": false, "RF": false, "DH": false, "SP": false, "RP": false,
    })

    useEffect(() => {
        axios.get('/api/season')
            .then(res => setSeason(res.data.season))
            .catch(err => console.error('Failed to fetch season', err))
    }, [])

    useEffect(() => {
        if (!season) return
        axios.get(`/api/players/${season}/${type}/column-ranges`)
            .then(res => setGlobalRanges(res.data))
            .catch(err => console.error('Failed to fetch column ranges', err))
    }, [season, type])

    function lineupAdd(fg_id) {
        axios.post('/api/lineup/add', { player_id: fg_id })
            .then(() => {
                setPlayers(prev => prev.map(p =>
                    p.fg_id === fg_id ? { ...p, team_assigned: team } : p
                ))
                if (onRosterChange) onRosterChange()
            })
            .catch(err => console.error(err))
    }

    function rosterDrop(fg_id) {
        axios.post('/api/roster/drop', { player_id: fg_id })
            .then(() => {
                setPlayers(prev => prev.map(p =>
                    p.fg_id === fg_id ? { ...p, team_assigned: null } : p
                ))
                if (onRosterChange) onRosterChange()
            })
            .catch(err => console.error(err))
    }

    useEffect(() => {
        if (!season) return
        let params = new URLSearchParams()
        params.append('page', pageIndex + 1)
        params.append('ordering', sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : '-FAN_total')
        params.append('search', filters.map(d => d.value).join(''))
        for (let position in positionFilters) {
            if (positionFilters[position]) {
                params.append('positions', position)
            }
        }
        if (team && ownershipFilter === 'mine') {
            params.append('team', team)
        } else if (ownershipFilter === 'available') {
            params.append('available', 'true')
        }
        axios.get(`/api/players/${season}/${type}`, { params })
            .then(response => {
                if (response.data.results) {
                    const count = Math.ceil(response.data.count / response.data.results.length)
                    setMetrics({ avg: response.data.avg_total, stdDev: response.data.stddev_total })
                    setSumTotal(response.data.sum_total ?? null)
                    setPageCount(count)
                    setPagination({ pageIndex, pageSize: response.data.results.length })
                    const sorted = playerOrder
                        ? [...response.data.results].sort((a, b) => {
                            const ai = playerOrder.indexOf(a.fg_id)
                            const bi = playerOrder.indexOf(b.fg_id)
                            if (ai === -1 && bi === -1) return 0
                            if (ai === -1) return 1
                            if (bi === -1) return -1
                            return ai - bi
                          })
                        : response.data.results
                    setPlayers(sorted)
                }
            })
            .catch(err => console.error(err))
    }, [type, pageIndex, sorting, filters, positionFilters, season, rosterVersion, ownershipFilter, team])

    // Re-sort when playerOrder changes (e.g. lineup loads after initial fetch)
    useEffect(() => {
        if (!playerOrder || !playerOrder.length) return
        setPlayers(prev => {
            if (!prev.length) return prev
            return [...prev].sort((a, b) => {
                const ai = playerOrder.indexOf(a.fg_id)
                const bi = playerOrder.indexOf(b.fg_id)
                if (ai === -1 && bi === -1) return 0
                if (ai === -1) return 1
                if (bi === -1) return -1
                return ai - bi
            })
        })
    }, [playerOrder?.join(',')])

    const table = useReactTable({
        data: players,
        columns,
        getCoreRowModel: getCoreRowModel(),
        onSortingChange: setSorting,
        manualSorting: true,
        onColumnFiltersChange: setColumnFilters,
        manualFiltering: true,
        manualPagination: true,
        onPaginationChange: setPagination,
        pageCount,
        state: {
            pagination: { pageIndex, pageSize },
            sorting,
            filters,
        },
        meta: { metrics },
    })

    const activeToggleClass = 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300'
    const inactiveToggleClass = 'bg-muted text-foreground hover:bg-muted/80'

    const PaginationControls = () => (
        <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
                Previous
            </Button>
            <span className="text-sm text-muted-foreground">
                {pageIndex + 1} / {pageCount > 0 ? pageCount : 1}
            </span>
            <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
                Next
            </Button>
        </div>
    )

    return (
        <div>
            {!hideControls && (
            <div className="flex flex-wrap items-center gap-2 py-2">
                <PositionSelectDropdown positionFilters={positionFilters} setPositionFilters={setPositionFilters} type={type} />
                {(team || ownershipOptions) && (
                    <div className="flex rounded-md border overflow-hidden text-sm">
                        {(ownershipOptions ?? ['all', 'available', 'mine']).map(f => (
                            <button key={f} onClick={() => { setOwnershipFilter(f); setPagination(p => ({ ...p, pageIndex: 0 })) }}
                                className={`px-3 py-1 capitalize ${ownershipFilter === f ? activeToggleClass : inactiveToggleClass}`}>
                                {f}
                            </button>
                        ))}
                    </div>
                )}
                {!externalScoreType && (
                <div className="flex rounded-md border overflow-hidden text-sm">
                    {['FAN', 'RAW'].map(s => (
                        <button key={s} onClick={() => setScoreType(s)}
                            className={`px-3 py-1 ${scoreType === s ? activeToggleClass : inactiveToggleClass}`}>
                            {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
                        </button>
                    ))}
                </div>
                )}
                <div className="flex items-center gap-2 ml-auto">
                    <Input
                        placeholder="Filter by name..."
                        onChange={(e) => { table.getColumn("name")?.setFilterValue(e.target.value); table.setPageIndex(0) }}
                        className="w-40 sm:w-56"
                    />
                    <PaginationControls />
                </div>
            </div>
            )}


            <div ref={tableWrapperRef} className="rounded-md border geist-mono overflow-auto" style={{ height: tableHeight }}>
                <Table style={{ minWidth: 'max-content' }}>
                    <TableHeader className="sticky top-0 z-20">
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    const meta = header.column.columnDef.meta
                                    const pinned = meta?.pinned
                                    const colId = header.column.id
                                    const isLastPinned = colId === lastPinnedId
                                    const stickyStyle = pinned ? {
                                        position: 'sticky',
                                        left: pinnedOffsets[colId],
                                        zIndex: 20,
                                        minWidth: meta.width,
                                        maxWidth: meta.width,
                                        backgroundColor: meta?.highlight ? undefined : 'hsl(var(--background))',
                                        ...(isLastPinned ? {
                                            borderRight: '1px solid hsl(var(--border))',
                                            boxShadow: isScrolled ? '4px 0 8px -2px rgba(0,0,0,0.12)' : 'none',
                                        } : {})
                                    } : {}
                                    const highlightClass = meta?.highlight ? 'bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300' : ''
                                    const headerStyle = pinned ? stickyStyle : (meta?.highlight ? {} : { backgroundColor: 'hsl(var(--background))' })
                                    return (
                                        <TableHead key={header.id} className={`${meta?.className ?? ''} ${highlightClass} pinned-cols`} style={headerStyle}>
                                            {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? table.getRowModel().rows.map((row) => (
                            <TableRow
                                draggable={true}
                                key={row.original.fg_id}
                                dragData={{ id: row.original.fg_id, positions: row.original.positions, team_assigned: row.original.team_assigned }}
                                data-state={row.getIsSelected() && 'selected'}
                                className="h-8"
                            >
                                {row.getVisibleCells().map((cell) => {
                                    const meta = cell.column.columnDef.meta
                                    const pinned = meta?.pinned
                                    const colId = cell.column.id
                                    const isLastPinned = colId === lastPinnedId
                                    const highlightClass = meta?.highlight ? 'bg-orange-50 dark:bg-orange-950 text-orange-900 dark:text-orange-200' : ''

                                    // Data-driven shading for non-pinned, non-highlight numeric cells
                                    let shadeStyle = {}
                                    if (!pinned && !meta?.highlight) {
                                        const key = cell.column.columnDef.accessorKey
                                        const range = globalRanges[key]
                                        if (range) {
                                            const fanKey = RAW_TO_FAN[key]
                                            const colorRange = fanKey ? globalRanges[fanKey] : null
                                            shadeStyle = getShadeStyle(cell.getValue(), range, colorRange)
                                        }
                                    }

                                    const stickyStyle = pinned ? {
                                        position: 'sticky',
                                        left: pinnedOffsets[colId],
                                        zIndex: 10,
                                        minWidth: meta.width,
                                        maxWidth: meta.width,
                                        backgroundColor: meta?.highlight ? undefined : 'hsl(var(--background))',
                                        ...(isLastPinned ? {
                                            borderRight: '1px solid hsl(var(--border))',
                                            boxShadow: isScrolled ? '4px 0 8px -2px rgba(0,0,0,0.12)' : 'none',
                                        } : {})
                                    } : shadeStyle

                                    return (
                                        <TableCell key={cell.id} className={`py-0 ${meta?.className ?? ''} ${highlightClass} pinned-cols`} style={stickyStyle}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    )
                                })}
                            </TableRow>
                        )) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    No results.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {!hideControls && (
            <div className="flex justify-end py-2">
                <PaginationControls />
            </div>
            )}
        </div>
    )
}
