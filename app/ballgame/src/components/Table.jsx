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

export function DataTable({
    columns, data, pageIndex, pageSize, setPagination, pageCount, sorting, setSorting
}) {

    const pagination = useMemo(() => {
        return {
            pageIndex:pageIndex,
            pageSize:pageSize
        }
    },[pageIndex,pageSize])


    const table = useReactTable({
        data,
        columns,
        autoResetPageIndex:true,
        getCoreRowModel: getCoreRowModel(),
        onSortingChange: setSorting,
        manualSorting:true,
        // getSortedRowModel: getSortedRowModel(),
        // onColumnFiltersChange: setColumnFilters,
        // getFilteredRowModel: getFilteredRowModel(),
        manualPagination:true,
        onPaginationChange:setPagination,
        pageCount: pageCount,
        state:{
            pagination,
            sorting
        },
        debugTable:false
    })

    return (
        <div>
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