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
        cell: ({ row }) => {
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
                            onClick={() => console.log('add to team API endpoint')}
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
        header: "Team",
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

    useEffect(() => {
        axios.get(`http://localhost:8000/api/players`,{
            params:{
                page: pageIndex+1,
                ordering:sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : null
            }
        })
            .then(response => {
                if (response.data.count) {
                    console.log(response.data)
                    let count = Math.ceil(response.data.count/response.data.results.length)
                    setPageCount(count)
                    setPagination({pageIndex:pageIndex,pageSize:response.data.results.length})
                    setPlayers(response.data.results)
                }
            })
            .catch(err => {
                console.log(err)
            })
    }, [pageIndex,sorting])
    console.log('pagination state: ',{pageIndex,pageSize})

    return (
        <div className="container mx-auto py-10">
            <DataTable 
                columns={playerTableColumns} 
                data={players.length > 0 ? players : []} 
                pageIndex={pageIndex} 
                pageSize={pageSize}
                pageCount={pageCount}
                setPagination={setPagination}
                sorting={sorting}
                setSorting={setSorting}
                />
        </div>
    )
}