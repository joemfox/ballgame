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
    scoreType
}) {
    const [players, setPlayers] = useState([])
    const [{ pageIndex, pageSize }, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
    const [pageCount, setPageCount] = useState(-1)
    
    const columns = columnData[`${scoreType}_columns_${type}`]
  
    const defaultSort = {desc:true,id:'FAN_total'}
    const [sorting, setSorting] = useState([defaultSort])
  
    const [metrics,setMetrics] = useState([])
    
    const [filters, setColumnFilters] = useState([])
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
    useEffect(() => {
        let params = new URLSearchParams()
        params.append('page', pageIndex + 1)
        params.append('ordering', sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : '-FAN_total')
        params.append('search', filters.map(d => d.value).join(''))
        for (let position in positionFilters) {
            if (positionFilters[position]) {
                params.append('positions', position)
            }
        }
        console.log(params)
        axios.get(`http://localhost:8000/api/players/2023/${type}`, {
            params: params
        })
            .then(response => {
                if (response.data.results) {
                    let count = Math.ceil(response.data.count / response.data.results.length)
                    setMetrics({'avg':response.data.avg_total,'stdDev':response.data.stddev_total})
                    setPageCount(count)
                    setPagination({ pageIndex: pageIndex, pageSize: response.data.results.length })
                    setPlayers(response.data.results)
                }
            })
            .catch(err => {
                console.log(err)
            })
    }, [type, pageIndex, sorting, filters,positionFilters])
    
    const table = useReactTable({
        data:players,
        columns,
        getCoreRowModel: getCoreRowModel(),
        onSortingChange: setSorting,
        manualSorting:true,
        onColumnFiltersChange: setColumnFilters,
        manualFiltering:true,
        manualPagination:true,
        onPaginationChange:setPagination,
        pageCount: pageCount,
        state:{
            // pagination,
            sorting,
            filters
        },
        meta:{
            updateRow:(rowIndex,value) => {
                setData(f => {
                    f = f.map((row,index) => {
                        if(index === rowIndex) {
                            return value
                        } else {   
                            return row
                        }
                    })
                    return f
                })
            },
            metrics:metrics
        },
        debugTable:true
    })

    return (
        <div>
                        <PositionSelectDropdown 
                positionFilters={positionFilters}
                setPositionFilters={setPositionFilters} 
            />
            <div className="flex items-center justify-end space-x-2 py-4">
                <Input 
                    placeholder="Filter by name ..."
                    // value={(table.getColumn("name")?.getFilterValue()) ?? ""}
                    onChange={(event) =>{
                        table.getColumn("name")?.setFilterValue(event.target.value)
                        table.setPageIndex(0)
                    }}
                    className="max-w-md"/>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                        table.previousPage()
                        
                    }}
                    disabled={!table.getCanPreviousPage()}
                >
                    Previous
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                        table.nextPage()
                    }}
                    disabled={!table.getCanNextPage()}
                >
                    Next
                </Button>
            </div>
            <div className="rounded-md border geist-mono">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (table.getRowModel().rows.map((row) => {console.log(row.original);return(
                            <TableRow
                                draggable={true}
                                key={row.original.fg_id}
                                dragData={{id:row.original.fg_id, positions:row.original.positions} }
                                data-state={row.getIsSelected() && 'selected'}
                                className="h-4"
                                >
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id} className="h-4 pt-0 pb-0">
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </TableCell>
                                ))}
                            </TableRow>
                        )}))
                            : (
                                <TableRow>
                                    <TableCell colSpan={columns.length} className="h-24 text-center">
                                        No results.
                                    </TableCell>
                                </TableRow>
                            )}
                    </TableBody>
                </Table>
            </div>
            <div className="flex items-center justify-end space-x-2 py-4">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                        table.previousPage()
                        
                    }}
                    disabled={!table.getCanPreviousPage()}
                >
                    Previous
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                        table.nextPage()
                    }}
                    disabled={!table.getCanNextPage()}
                >
                    Next
                </Button>
            </div>
        </div>
    )
}