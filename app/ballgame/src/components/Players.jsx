import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { ArrowUpDown, MoreHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTable } from './PlayerTable'
import { PositionSelectDropdown } from './PositionDropdown'



export default function Players() {
    const [players, setPlayers] = useState([])
    const [{ pageIndex, pageSize }, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
    const [pageCount, setPageCount] = useState(-1)

    const [sorting, setSorting] = React.useState([])
    const [filters, setColumnFilters] = React.useState([])
    const [positionFilters, setPositionFilters] = useState({
        "C": false,
        "1B": false,
        "2B": false,
        "SS": false,
        "3B": false,
        "LF": false,
        "CF": false,
        "RF": false,
        "SP": false,
        "RP": false,
    })

    const playerTableColumns = [
        {
            id: "actions",
            cell: ({ row, column, table }) => {
                const player = row.original
    
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Actions</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start">
                            <DropdownMenuLabel>Player actions</DropdownMenuLabel>
                            <DropdownMenuItem
                                onClick={() => {
                                    axios.post('http://localhost:8000/api/add-player', { id: player.fg_id, team_id: "TST" })
                                        .then(response => {
                                            console.log(response)
                                            table.options.meta?.updateRow(row.index, response.data)
                                        })
                                        .catch(err => {
                                            console.error(err)
                                        })
                                }}
                            >
                                Add to team
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>View player</DropdownMenuItem>
                            <DropdownMenuItem>Drop player</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
    
                )
            }
    
        },
        {
            accessorKey: "team_assigned",
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
                        Team
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            }
        },
        // {
        //     accessorKey: "fg_id",
        //     header: "id"
        // },
        {
            accessorKey: 'positions',
            header: "positions",
            cell: ({row}) => {
                const positions = row.original.positions.map((d,i) => (<><span className={`${positionFilters[d] ? 'bg-slate-400' : ''}`}>{d}</span><span>{i+1 < row.original.positions.length ? ', ' : ''}</span></>))
                return <div key={row.id} className={`text-left`}>{positions}</div>
            }
        },
        {
            accessorKey: "name",
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
                        Name
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            }
        },
        {
            accessorKey: 'stats',
            header: "Stats"
        }
    ]

    useEffect(() => {
        let params = new URLSearchParams()
        params.append('page', pageIndex + 1)
        // params.append('ordering', sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : null)
        // params.append('search', filters.map(d => d.value).join(''))
        // for (let position in positionFilters) {
        //     if (positionFilters[position]) {
        //         params.append('positions', position)
        //     }
        // }
        axios.get(`http://localhost:8000/api/players`, {
            params: params
        })
            .then(response => {
                if (response.data.items) {
                    let count = Math.ceil(response.data.items.count / response.data.items.length)
                    setPageCount(count)
                    setPagination({ pageIndex: pageIndex, pageSize: response.data.items.length })
                    setPlayers(response.data.items)
                }
            })
            .catch(err => {
                console.log(err)
            })
    }, [pageIndex, sorting, filters,positionFilters])

    return (
        <div className="container mx-auto py-10">
            <PositionSelectDropdown 
                positionFilters={positionFilters}
                setPositionFilters={setPositionFilters} 
            />
            <DataTable
                columns={playerTableColumns}
                data={players.length > 0 ? players : []}
                setData={setPlayers}
                pageIndex={pageIndex}
                pageSize={pageSize}
                pagination={{ pageIndex: pageIndex, pageSize: pageSize }}
                pageCount={pageCount}
                setPagination={setPagination}
                sorting={sorting}
                setSorting={setSorting}
                filters={filters}
                setColumnFilters={setColumnFilters}
            />
        </div>
    )
}