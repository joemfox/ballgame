import React, { useMemo } from "react"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const ALL_POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "DH", "SP", "RP"]
const HIT_POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "DH"]
const PITCH_POSITIONS = ["SP", "RP"]
const OF_POSITIONS = ["LF", "CF", "RF"]
const IF_POSITIONS = ["1B", "2B", "SS", "3B"]

export function PositionSelectDropdown({ positionFilters, setPositionFilters, type }) {
    const POSITIONS = type === 'pitch' ? PITCH_POSITIONS : HIT_POSITIONS
    const buttonLabel = useMemo(() => {
        const selected = POSITIONS.filter(d => positionFilters[d])
        return selected.length === 0 ? 'Positions' : selected.join(', ')
    }, [positionFilters])

    const isAnySelected = POSITIONS.some(p => positionFilters[p])

    function toggleGroup(positions) {
        const allOn = positions.every(p => positionFilters[p])
        setPositionFilters(f => {
            const next = { ...f }
            positions.forEach(p => { next[p] = !allOn })
            return next
        })
    }

    function clearAll() {
        setPositionFilters(f => {
            const next = { ...f }
            POSITIONS.forEach(p => { next[p] = false })
            return next
        })
    }

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" className={isAnySelected ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border-orange-300 dark:border-orange-800' : ''}>{buttonLabel}</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48">
                <DropdownMenuLabel className="flex justify-between items-center py-1.5">
                    <span>Position</span>
                    {isAnySelected && (
                        <button
                            onClick={(e) => { e.preventDefault(); clearAll() }}
                            className="text-xs text-muted-foreground hover:text-foreground underline"
                        >
                            Clear
                        </button>
                    )}
                </DropdownMenuLabel>
                {type !== 'pitch' && (<>
                <DropdownMenuSeparator />
                <div className="flex gap-1 px-2 py-1.5">
                    <button
                        onClick={(e) => { e.preventDefault(); toggleGroup(OF_POSITIONS) }}
                        className={`flex-1 text-xs px-2 py-1 rounded border font-medium transition-colors
                            ${OF_POSITIONS.every(p => positionFilters[p])
                                ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border-orange-300 dark:border-orange-800'
                                : 'bg-muted text-foreground border-input hover:bg-muted/80'}`}
                    >OF</button>
                    <button
                        onClick={(e) => { e.preventDefault(); toggleGroup(IF_POSITIONS) }}
                        className={`flex-1 text-xs px-2 py-1 rounded border font-medium transition-colors
                            ${IF_POSITIONS.every(p => positionFilters[p])
                                ? 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border-orange-300 dark:border-orange-800'
                                : 'bg-muted text-foreground border-input hover:bg-muted/80'}`}
                    >IF</button>
                </div>
                </>)}
                <DropdownMenuSeparator />
                {(type === 'pitch' ? [PITCH_POSITIONS] : [["C"], IF_POSITIONS, OF_POSITIONS, ["DH"]]).map((group, gi) => (
                    <React.Fragment key={gi}>
                        {gi > 0 && <DropdownMenuSeparator className="my-0.5" />}
                        {group.map(d => (
                            <DropdownMenuCheckboxItem
                                key={d}
                                checked={positionFilters[d]}
                                onCheckedChange={(value) => setPositionFilters(f => ({ ...f, [d]: value }))}
                            >{d}</DropdownMenuCheckboxItem>
                        ))}
                    </React.Fragment>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
