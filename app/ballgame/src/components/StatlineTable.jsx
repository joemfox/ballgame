import React, {useEffect, useState} from 'react'
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

export default function DataTable({
    type,
    team,
    openPositions,
    rosterVersion,
    onRosterChange,
    customActionColumn,
    defaultOwnershipFilter = 'all',
    ownershipOptions,
}) {
    const [players, setPlayers] = useState([])
    const [{ pageIndex, pageSize }, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
    const [pageCount, setPageCount] = useState(-1)
    const [season, setSeason] = useState(null)
    const [scoreType, setScoreType] = useState('FAN')
    const [ownershipFilter, setOwnershipFilter] = useState(defaultOwnershipFilter)
    const [metrics, setMetrics] = useState([])
    const [sumTotal, setSumTotal] = useState(null)

    const baseColumns = columnData[`${scoreType}_columns_${type}`]

    const actionColumn = {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
            const { fg_id, team_assigned, positions } = row.original
            if (!team) return null
            if (team_assigned === team) {
                return (
                    <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-800"
                        onClick={() => rosterDrop(fg_id)}>Drop</Button>
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

    const resolvedActionColumn = customActionColumn ?? (team ? actionColumn : null)
    const columns = resolvedActionColumn ? [resolvedActionColumn, ...baseColumns] : baseColumns

    const defaultSort = {desc: true, id: 'FAN_total'}
    const [sorting, setSorting] = useState([defaultSort])

    const [filters, setColumnFilters] = useState([])
    const [positionFilters, setPositionFilters] = useState({
        "C": false, "1B": false, "2B": false, "SS": false, "3B": false,
        "LF": false, "CF": false, "RF": false, "SP": false, "RP": false,
    })

    useEffect(() => {
        axios.get('/api/season')
            .then(res => setSeason(res.data.season))
            .catch(err => console.error('Failed to fetch season', err))
    }, [])

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
                    setPlayers(response.data.results)
                }
            })
            .catch(err => console.error(err))
    }, [type, pageIndex, sorting, filters, positionFilters, season, rosterVersion, ownershipFilter])

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
            <div className="flex flex-wrap items-center gap-2 py-2">
                <PositionSelectDropdown positionFilters={positionFilters} setPositionFilters={setPositionFilters} />
                {(team || ownershipOptions) && (
                    <div className="flex rounded-md border overflow-hidden text-sm">
                        {(ownershipOptions ?? ['all', 'available', 'mine']).map(f => (
                            <button key={f} onClick={() => { setOwnershipFilter(f); setPagination(p => ({ ...p, pageIndex: 0 })) }}
                                className={`px-3 py-1 capitalize ${ownershipFilter === f ? 'bg-primary text-primary-foreground' : 'bg-background text-foreground hover:bg-muted'}`}>
                                {f}
                            </button>
                        ))}
                    </div>
                )}
                <div className="flex rounded-md border overflow-hidden text-sm">
                    {['FAN', 'RAW'].map(s => (
                        <button key={s} onClick={() => setScoreType(s)}
                            className={`px-3 py-1 ${scoreType === s ? 'bg-primary text-primary-foreground' : 'bg-background text-foreground hover:bg-muted'}`}>
                            {s === 'FAN' ? 'FAN Pts' : 'Raw Stats'}
                        </button>
                    ))}
                </div>
                <div className="flex items-center gap-2 ml-auto">
                    <Input
                        placeholder="Filter by name..."
                        onChange={(e) => { table.getColumn("name")?.setFilterValue(e.target.value); table.setPageIndex(0) }}
                        className="w-40 sm:w-56"
                    />
                    <PaginationControls />
                </div>
            </div>

            {ownershipFilter === 'mine' && sumTotal != null && (
                <div className="flex justify-end items-center py-1 px-2 text-sm font-medium">
                    Team total: <span className="ml-2 tabular-nums">{sumTotal.toFixed(1)} pts</span>
                </div>
            )}

            <div className="rounded-md border geist-mono">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <TableHead key={header.id} className={header.column.columnDef.meta?.className}>
                                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                    </TableHead>
                                ))}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? table.getRowModel().rows.map((row) => (
                            <TableRow
                                draggable={true}
                                key={row.original.fg_id}
                                dragData={{ id: row.original.fg_id, positions: row.original.positions }}
                                data-state={row.getIsSelected() && 'selected'}
                                className="h-8"
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id} className={`py-0 ${cell.column.columnDef.meta?.className ?? ''}`}>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </TableCell>
                                ))}
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

            <div className="flex justify-end py-2">
                <PaginationControls />
            </div>
        </div>
    )
}
