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
import { DataTable } from './Table'
import { data } from 'autoprefixer'

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
                                axios.post('http://localhost:8000/api/add-player',{id:player.fg_id,team_id:"TST"})
                                    .then(response => {
                                        console.log(response)
                                        table.options.meta?.updateRow(row.index,response.data)
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
        accessorKey: "team",
        header: ({column}) => {
            return (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
                        Team
                        <ArrowUpDown className="ml-2 h-4 w-4"/>
                    </Button>
            )
        }
    },
    {
        accessorKey: "mlbam_id",
        header: "id"
    },
    {
        accessorKey: "name",
        header: ({column}) => {
            return (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
                        Name
                        <ArrowUpDown className="ml-2 h-4 w-4"/>
                    </Button>
            )
        }
    },
    {
        accessorKey: 'stats',
        header: "Stats"
    }
]

export default function Players() {
    const [players, setPlayers] = useState([])
    const [{pageIndex, pageSize}, setPagination] = useState({pageIndex:0,pageSize:100})
    const [pageCount, setPageCount] = useState(-1)

    const [sorting, setSorting] = React.useState([])
    const [filters, setColumnFilters] = React.useState([])

    useEffect(() => {
        axios.get(`http://localhost:8000/api/players`,{
            params:{
                page: pageIndex+1,
                ordering:sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : null,
                search:filters.map(d => d.value).join('')
            }
        })
            .then(response => {
                if (response.data.count) {
                    let count = Math.ceil(response.data.count/response.data.results.length)
                    setPageCount(count)
                    setPagination({pageIndex:pageIndex,pageSize:response.data.results.length})
                    setPlayers(response.data.results)
                }
            })
            .catch(err => {
                console.log(err)
            })
    }, [pageIndex,sorting,filters])

    return (
        <div className="container mx-auto py-10">
            <DataTable 
                columns={playerTableColumns} 
                data={players.length > 0 ? players : []} 
                setData={setPlayers}
                pageIndex={pageIndex} 
                pageSize={pageSize}
                pagination={{pageIndex:pageIndex,pageSize:pageSize}}
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