import React, {useMemo} from 'react'
import { flexRender, getCoreRowModel, useReactTable  } from "@tanstack/react-table"

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

function useSkipper() {
    const shouldSkipRef = React.useRef(true)
    const shouldSkip = shouldSkipRef.current
  
    // Wrap a function with this to skip a pagination reset temporarily
    const skip = React.useCallback(() => {
      shouldSkipRef.current = false
    }, [])
  
    React.useEffect(() => {
      shouldSkipRef.current = true
    })
  
    return [shouldSkip, skip]
  }

export function DataTable({
    columns, data, setData, pageIndex, pageSize, setPagination, pageCount, sorting, setSorting, filters, setColumnFilters
}) {

    const pagination = useMemo(() => {
        return {
            pageIndex:pageIndex,
            pageSize:pageSize
        }
    },[pageIndex,pageSize])

    const [autoResetPageIndex, skipAutoResetPageIndex] = useSkipper()

    const table = useReactTable({
        data,
        columns,
        autoResetPageIndex,
        getCoreRowModel: getCoreRowModel(),
        onSortingChange: setSorting,
        manualSorting:true,
        onColumnFiltersChange: setColumnFilters,
        manualFiltering:true,
        manualPagination:true,
        onPaginationChange:setPagination,
        pageCount: pageCount,
        state:{
            pagination,
            sorting,
            filters
        },
        meta:{
            updateRow:(rowIndex,value) => {
                skipAutoResetPageIndex()
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
            }
        },
        debugTable:false
    })

    return (
        <div>
            <div className="flex items-center justify-end space-x-2 py-4">
                <Input 
                    placeholder="Filter by name ..."
                    // value={(table.getColumn("name")?.getFilterValue()) ?? ""}
                    onChange={(event) =>{
                        table.getColumn("name")?.setFilterValue(event.target.value)
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
            <div className="rounded-md border">
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
                        {table.getRowModel().rows?.length ? (table.getRowModel().rows.map((row) => (
                            <TableRow
                                key={row.id}
                                data-state={row.getIsSelected() && 'selected'}>
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id}>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </TableCell>
                                ))}
                            </TableRow>
                        )))
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