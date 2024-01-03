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
        header: "name"
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

    useEffect(() => {
        axios.get(`http://localhost:8000/api/players?page=${pageIndex+1}`)
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
    }, [pageIndex])
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
                />
        </div>
    )
}