import React, { useState, useMemo, useEffect } from "react"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "SP", "RP"]

export function PositionSelectDropdown({ positionFilters, setPositionFilters }) {
    const buttonLabel = useMemo(() => {
        let selected = POSITIONS.map(d => positionFilters[d] ? d : null).filter(d => d)
        if (selected.length === 0) {
            return 'Positions'
        } else {
            return selected.join(', ')
        }
    }, [positionFilters])

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline">{buttonLabel}</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
                <DropdownMenuLabel>Filter by position</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {
                    POSITIONS.map(d => (
                        <DropdownMenuCheckboxItem
                            key={d}
                            checked={positionFilters[d]}
                            onCheckedChange={(value) => {
                                setPositionFilters(f => {
                                    let newSet = {
                                        ...f
                                    }
                                    newSet[d] = value
                                    return newSet
                                })
                            }}
                        >{d}</DropdownMenuCheckboxItem>
                    ))
                }
            </DropdownMenuContent>
        </DropdownMenu>
    )
}