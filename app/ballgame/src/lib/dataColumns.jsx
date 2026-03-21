import { Button } from "@/components/ui/button"
import { Link } from 'react-router-dom'

const sortableHeader = ({ column, key, title }) => {
    return (
        <Button
            variant={["asc","desc"].includes(column.getIsSorted()) ? "default" : "ghost"}
            size="sm"
            title={title}
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
            {key}
        </Button>
    )
}
const rightAlignedCell = ({row,key}) => {
    const val = row.getValue(key)
    return <div className="text-right">{val ?? '-'}</div>
}

export const statlineColumns_hit = [
    { accessorKey:'ab', header:'ab' },
    { accessorKey:'r', header:'r' },
    { accessorKey:'h', header:'h' },
    { accessorKey:'outs', header:'outs' },
    { accessorKey:'doubles', header:'doubles' },
    { accessorKey:'triples', header:'triples' },
    { accessorKey:'hr', header:'hr' },
    { accessorKey:'rbi', header:'rbi' },
    { accessorKey:'bb', header:'bb' },
    { accessorKey:'k', header:'k' },
    { accessorKey:'lob', header:'lob' },
    { accessorKey:'sb', header:'sb' },
    { accessorKey:'cs', header:'cs' },
    { accessorKey:'e', header:'e' },
    { accessorKey:'k_looking', header:'k_looking' },
    { accessorKey:'rl2o', header:'rl2o' },
    { accessorKey:'cycle', header:'cycle' },
    { accessorKey:'gidp', header:'gidp' },
    { accessorKey:'po', header:'po' },
    { accessorKey:'outfield_assists', header:'outfield_assists' },
    { accessorKey:'FAN_total', header:'FAN_total' },
]

const fanTotalColumn_hit = {
    accessorKey: "FAN_total",
    meta: { pinned: true, width: 64, highlight: true },
    header: ({ column }) => sortableHeader({ column, key: 'Total', title: 'FAN fantasy points total' }),
    cell: ({row}) => <div className="text-right font-bold">{row.getValue('FAN_total')}</div>
}

const fanTotalColumn_pitch = {
    accessorKey: "FAN_total",
    meta: { pinned: true, width: 64, highlight: true },
    header: ({ column }) => sortableHeader({ column, key: 'Total', title: 'FAN fantasy points total' }),
    cell: ({row}) => <div className="text-right font-bold">{row.getValue('FAN_total')}</div>
}

export const FAN_columns_hit = [
    {
        accessorKey:'player_name',
        header: 'name',
        id:'name',
        meta: { pinned: true, width: 150 },
        cell: ({row}) => {
            const role = row.original.role
            const isInjured = row.original.is_injured
            const MINOR_LEVELS = new Set(['AAA', 'AA', 'A+', 'A', 'A-', 'R', 'Rk'])
            const showMinorBadge = role && MINOR_LEVELS.has(role)
            return (
                <span className="flex items-center gap-1">
                    <Link to={`/player/${row.original.fg_id}`} className="hover:underline">{row.getValue('name')}</Link>
                    {isInjured && <span className="text-[10px] px-1 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300 font-semibold leading-none shrink-0">IL</span>}
                    {showMinorBadge && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">{role}</span>}
                    {!role && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">Free Agent</span>}
                </span>
            )
        }
    },
    {
        accessorKey: 'positions',
        header: "pos",
        meta: { pinned: true, width: 72 },
        cell: ({row}) => {
            const positions = row.original.positions.map((d,i) => (<><span>{d}</span><span>{i+1 < row.original.positions.length ? ', ' : ''}</span></>))
            return <div key={row.id} className="text-left">{positions}</div>
        }
    },
    {
        accessorKey: 'team_assigned',
        header: 'team',
        id: 'team_assigned',
        meta: { pinned: true, width: 60 },
        cell: ({ row }) => {
            const val = row.getValue('team_assigned')
            return val
                ? <Link to={`/team/${val}`} className="text-left text-muted-foreground hover:underline">{val}</Link>
                : <div className="text-left text-muted-foreground"></div>
        }
    },
    fanTotalColumn_hit,
    {
        accessorKey:"FAN_h",
        header: ({ column }) => sortableHeader({column, key:'H', title:'Hits'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_h'})
    },
    {
        accessorKey:"FAN_doubles",
        header: ({ column }) => sortableHeader({column, key:'2B', title:'Doubles'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_doubles'})
    },
    {
        accessorKey:"FAN_triples",
        header: ({ column }) => sortableHeader({column, key:'3B', title:'Triples'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_triples'})
    },
    {
        accessorKey:"FAN_hr",
        header: ({ column }) => sortableHeader({column, key:'HR', title:'Home Runs'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_hr'})
    },
    {
        accessorKey:"FAN_rbi",
        header: ({ column }) => sortableHeader({column, key:'RBI', title:'Runs Batted In'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_rbi'})
    },
    {
        accessorKey:"FAN_r",
        header: ({ column }) => sortableHeader({column, key:'R', title:'Runs Scored'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_r'})
    },
    {
        accessorKey:"FAN_sb",
        header: ({ column }) => sortableHeader({column, key:'SB', title:'Stolen Bases'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_sb'})
    },
    {
        accessorKey:"FAN_cs",
        header: ({ column }) => sortableHeader({column, key:'CS', title:'Caught Stealing'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_cs'})
    },
    {
        accessorKey:"FAN_bb",
        header: ({ column }) => sortableHeader({column, key:'BB', title:'Walks (Base on Balls)'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_bb'})
    },
    {
        accessorKey:"FAN_k",
        header: ({ column }) => sortableHeader({column, key:'K', title:'Strikeouts'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_k'})
    },
    {
        accessorKey:"FAN_k_looking",
        header: ({ column }) => sortableHeader({column, key:'K (👀)', title:'Strikeout Looking'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_k_looking'})
    },
    {
        accessorKey:"FAN_lob",
        header: ({ column }) => sortableHeader({column, key:'LOB', title:'Left on Base'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_lob'})
    },
    {
        accessorKey:"FAN_gidp",
        header: ({ column }) => sortableHeader({column, key:'GIDP', title:'Ground into Double Play'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_gidp'})
    },
    {
        accessorKey:"FAN_e",
        header: ({ column }) => sortableHeader({column, key:'E', title:'Errors'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_e'})
    },
    {
        accessorKey:"FAN_outs",
        header: ({ column }) => sortableHeader({column, key:'Outs', title:'Outs recorded'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_outs'})
    },
    {
        accessorKey:"FAN_po",
        header: ({ column }) => sortableHeader({column, key:'PO', title:'Picked off'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_po'})
    },
    {
        accessorKey:"FAN_rl2o",
        header: ({ column }) => sortableHeader({column, key:'RL2O', title:'Runners left in scoring position with 2 outs'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_rl2o'})
    },
    {
        accessorKey:"FAN_outfield_assists",
        header: ({ column }) => sortableHeader({column, key:'OA', title:'Outfield Assists'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_outfield_assists'})
    },
    {
        accessorKey:"FAN_cycle",
        header: ({ column }) => sortableHeader({column, key:'CYC', title:'Hit for the Cycle'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_cycle'})
    },
]

export const FAN_columns_pitch = [
    {
        accessorKey:'player_name',
        header: 'name',
        id:'name',
        meta: { pinned: true, width: 150 },
        cell: ({row}) => {
            const role = row.original.role
            const isInjured = row.original.is_injured
            const MINOR_LEVELS = new Set(['AAA', 'AA', 'A+', 'A', 'A-', 'R', 'Rk'])
            const showMinorBadge = role && MINOR_LEVELS.has(role)
            return (
                <span className="flex items-center gap-1">
                    <Link to={`/player/${row.original.fg_id}`} className="hover:underline">{row.getValue('name')}</Link>
                    {isInjured && <span className="text-[10px] px-1 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300 font-semibold leading-none shrink-0">IL</span>}
                    {showMinorBadge && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">{role}</span>}
                    {!role && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">Free Agent</span>}
                </span>
            )
        }
    },
    {
        accessorKey: 'positions',
        header: "pos",
        meta: { pinned: true, width: 72 },
        cell: ({row}) => {
            const positions = row.original.positions.map((d,i) => (<><span>{d}</span><span>{i+1 < row.original.positions.length ? ', ' : ''}</span></>))
            return <div key={row.id} className="text-left">{positions}</div>
        }
    },
    {
        accessorKey: 'team_assigned',
        header: 'team',
        id: 'team_assigned',
        meta: { pinned: true, width: 60 },
        cell: ({ row }) => <div className="text-left text-muted-foreground">{row.getValue('team_assigned') ?? ''}</div>
    },
    fanTotalColumn_pitch,
    {
        accessorKey:"FAN_ip",
        header: ({ column }) => sortableHeader({column, key:'IP', title:'Innings Pitched'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_ip'})
    },
    {
        accessorKey:"FAN_h",
        header: ({ column }) => sortableHeader({column, key:'H', title:'Hits Allowed'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_h'})
    },
    {
        accessorKey:"FAN_er",
        header: ({ column }) => sortableHeader({column, key:'ER', title:'Earned Runs Allowed'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_er'})
    },
    {
        accessorKey:"FAN_bb",
        header: ({ column }) => sortableHeader({column, key:'BB', title:'Walks (Base on Balls)'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_bb'})
    },
    {
        accessorKey:"FAN_k",
        header: ({ column }) => sortableHeader({column, key:'K', title:'Strikeouts'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_k'})
    },
    {
        accessorKey:"FAN_hr",
        header: ({ column }) => sortableHeader({column, key:'HR', title:'Home Runs Allowed'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_hr'})
    },
    {
        accessorKey:"FAN_bs",
        header: ({ column }) => sortableHeader({column, key:'BS', title:'Blown Saves'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_bs'})
    },
    {
        accessorKey:"FAN_hb",
        header: ({ column }) => sortableHeader({column, key:'HB', title:'Hit Batters'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_hb'})
    },
    {
        accessorKey:"FAN_wp",
        header: ({ column }) => sortableHeader({column, key:'WP', title:'Wild Pitches'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_wp'})
    },
    {
        accessorKey:"FAN_balks",
        header: ({ column }) => sortableHeader({column, key:'BALK', title:'Balks'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_balks'})
    },
    {
        accessorKey:"FAN_ir",
        header: ({ column }) => sortableHeader({column, key:'IR', title:'Inherited Runners'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_ir'})
    },
    {
        accessorKey:"FAN_irs",
        header: ({ column }) => sortableHeader({column, key:'IRS', title:'Inherited Runners Stranded'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_irs'})
    },
    {
        accessorKey:"FAN_e",
        header: ({ column }) => sortableHeader({column, key:'E', title:'Errors'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_e'})
    },
    {
        accessorKey:"FAN_dpi",
        header: ({ column }) => sortableHeader({column, key:'DPI', title:'Double Plays Induced'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_dpi'})
    },
    {
        accessorKey:"FAN_bra",
        header: ({ column }) => sortableHeader({column, key:'BRA', title:'Baserunners Allowed'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_bra'})
    },
    {
        accessorKey:"FAN_perfect_game",
        header: ({ column }) => sortableHeader({column, key:'PG', title:'Perfect Game'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_perfect_game'})
    },
    {
        accessorKey:"FAN_no_hitter",
        header: ({ column }) => sortableHeader({column, key:'NH', title:'No-Hitter'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_no_hitter'})
    },
    {
        accessorKey:"FAN_relief_loss",
        header: ({ column }) => sortableHeader({column, key:'RL', title:'Relief Loss'}),
        cell: ({row}) => rightAlignedCell({row,key:'FAN_relief_loss'})
    },
]

const namePositionColumns = [
    {
        accessorKey: 'player_name',
        header: 'name',
        id: 'name',
        meta: { pinned: true, width: 150 },
        cell: ({ row }) => {
            const role = row.original.role
            const isInjured = row.original.is_injured
            const MINOR_LEVELS = new Set(['AAA', 'AA', 'A+', 'A', 'A-', 'R', 'Rk'])
            const showMinorBadge = role && MINOR_LEVELS.has(role)
            return (
                <span className="flex items-center gap-1">
                    <Link to={`/player/${row.original.fg_id}`} className="hover:underline">{row.getValue('name')}</Link>
                    {isInjured && <span className="text-[10px] px-1 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300 font-semibold leading-none shrink-0">IL</span>}
                    {showMinorBadge && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">{role}</span>}
                    {!role && <span className="text-[10px] px-1 py-0.5 rounded bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 font-semibold leading-none shrink-0">Free Agent</span>}
                </span>
            )
        }
    },
    {
        accessorKey: 'positions',
        header: 'pos',
        meta: { pinned: true, width: 72 },
        cell: ({ row }) => {
            const positions = row.original.positions.map((d, i) => (
                <><span>{d}</span><span>{i + 1 < row.original.positions.length ? ', ' : ''}</span></>
            ))
            return <div key={row.id} className="text-left">{positions}</div>
        }
    },
    {
        accessorKey: 'team_assigned',
        header: 'team',
        id: 'team_assigned',
        meta: { pinned: true, width: 60 },
        cell: ({ row }) => {
            const val = row.getValue('team_assigned')
            return val
                ? <Link to={`/team/${val}`} className="text-left text-muted-foreground hover:underline">{val}</Link>
                : <div className="text-left text-muted-foreground"></div>
        }
    },
]

const rawFanTotal = {
    accessorKey: 'FAN_total',
    meta: { pinned: true, width: 64, highlight: true },
    header: ({ column }) => sortableHeader({ column, key: 'FAN', title: 'FAN fantasy points total' }),
    cell: ({ row }) => <div className="text-right font-bold">{row.getValue('FAN_total')}</div>
}

export const RAW_columns_hit = [
    ...namePositionColumns,
    rawFanTotal,
    { accessorKey: 'h', header: ({ column }) => sortableHeader({ column, key: 'H', title: 'Hits' }), cell: ({ row }) => rightAlignedCell({ row, key: 'h' }) },
    { accessorKey: 'doubles', header: ({ column }) => sortableHeader({ column, key: '2B', title: 'Doubles' }), cell: ({ row }) => rightAlignedCell({ row, key: 'doubles' }) },
    { accessorKey: 'triples', header: ({ column }) => sortableHeader({ column, key: '3B', title: 'Triples' }), cell: ({ row }) => rightAlignedCell({ row, key: 'triples' }) },
    { accessorKey: 'hr', header: ({ column }) => sortableHeader({ column, key: 'HR', title: 'Home Runs' }), cell: ({ row }) => rightAlignedCell({ row, key: 'hr' }) },
    { accessorKey: 'rbi', header: ({ column }) => sortableHeader({ column, key: 'RBI', title: 'Runs Batted In' }), cell: ({ row }) => rightAlignedCell({ row, key: 'rbi' }) },
    { accessorKey: 'r', header: ({ column }) => sortableHeader({ column, key: 'R', title: 'Runs Scored' }), cell: ({ row }) => rightAlignedCell({ row, key: 'r' }) },
    { accessorKey: 'sb', header: ({ column }) => sortableHeader({ column, key: 'SB', title: 'Stolen Bases' }), cell: ({ row }) => rightAlignedCell({ row, key: 'sb' }) },
    { accessorKey: 'cs', header: ({ column }) => sortableHeader({ column, key: 'CS', title: 'Caught Stealing' }), cell: ({ row }) => rightAlignedCell({ row, key: 'cs' }) },
    { accessorKey: 'bb', header: ({ column }) => sortableHeader({ column, key: 'BB', title: 'Walks (Base on Balls)' }), cell: ({ row }) => rightAlignedCell({ row, key: 'bb' }) },
    { accessorKey: 'k', header: ({ column }) => sortableHeader({ column, key: 'K', title: 'Strikeouts' }), cell: ({ row }) => rightAlignedCell({ row, key: 'k' }) },
    { accessorKey: 'k_looking', header: ({ column }) => sortableHeader({ column, key: 'K👀', title: 'Strikeout Looking' }), cell: ({ row }) => rightAlignedCell({ row, key: 'k_looking' }) },
    { accessorKey: 'lob', header: ({ column }) => sortableHeader({ column, key: 'LOB', title: 'Left on Base' }), cell: ({ row }) => rightAlignedCell({ row, key: 'lob' }) },
    { accessorKey: 'gidp', header: ({ column }) => sortableHeader({ column, key: 'GIDP', title: 'Ground into Double Play' }), cell: ({ row }) => rightAlignedCell({ row, key: 'gidp' }) },
    { accessorKey: 'e', header: ({ column }) => sortableHeader({ column, key: 'E', title: 'Errors' }), cell: ({ row }) => rightAlignedCell({ row, key: 'e' }) },
    { accessorKey: 'outs', header: ({ column }) => sortableHeader({ column, key: 'Outs', title: 'Outs Recorded' }), cell: ({ row }) => rightAlignedCell({ row, key: 'outs' }) },
    { accessorKey: 'po', header: ({ column }) => sortableHeader({ column, key: 'PO', title: 'Putouts' }), cell: ({ row }) => rightAlignedCell({ row, key: 'po' }) },
    { accessorKey: 'rl2o', header: ({ column }) => sortableHeader({ column, key: 'RL2O', title: 'Runners left in scoring position with 2 outs' }), cell: ({ row }) => rightAlignedCell({ row, key: 'rl2o' }) },
    { accessorKey: 'outfield_assists', header: ({ column }) => sortableHeader({ column, key: 'OA', title: 'Outfield Assists' }), cell: ({ row }) => rightAlignedCell({ row, key: 'outfield_assists' }) },
    { accessorKey: 'cycle', header: ({ column }) => sortableHeader({ column, key: 'CYC', title: 'Hit for the Cycle' }), cell: ({ row }) => rightAlignedCell({ row, key: 'cycle' }) },
]

export const RAW_columns_pitch = [
    ...namePositionColumns,
    rawFanTotal,
    { accessorKey: 'ip', header: ({ column }) => sortableHeader({ column, key: 'IP', title: 'Innings Pitched' }), cell: ({ row }) => rightAlignedCell({ row, key: 'ip' }) },
    { accessorKey: 'h', header: ({ column }) => sortableHeader({ column, key: 'H', title: 'Hits Allowed' }), cell: ({ row }) => rightAlignedCell({ row, key: 'h' }) },
    { accessorKey: 'er', header: ({ column }) => sortableHeader({ column, key: 'ER', title: 'Earned Runs Allowed' }), cell: ({ row }) => rightAlignedCell({ row, key: 'er' }) },
    { accessorKey: 'bb', header: ({ column }) => sortableHeader({ column, key: 'BB', title: 'Walks (Base on Balls)' }), cell: ({ row }) => rightAlignedCell({ row, key: 'bb' }) },
    { accessorKey: 'k', header: ({ column }) => sortableHeader({ column, key: 'K', title: 'Strikeouts' }), cell: ({ row }) => rightAlignedCell({ row, key: 'k' }) },
    { accessorKey: 'hr', header: ({ column }) => sortableHeader({ column, key: 'HR', title: 'Home Runs Allowed' }), cell: ({ row }) => rightAlignedCell({ row, key: 'hr' }) },
    { accessorKey: 'bs', header: ({ column }) => sortableHeader({ column, key: 'BS', title: 'Blown Saves' }), cell: ({ row }) => rightAlignedCell({ row, key: 'bs' }) },
    { accessorKey: 'hb', header: ({ column }) => sortableHeader({ column, key: 'HB', title: 'Hit Batters' }), cell: ({ row }) => rightAlignedCell({ row, key: 'hb' }) },
    { accessorKey: 'wp', header: ({ column }) => sortableHeader({ column, key: 'WP', title: 'Wild Pitches' }), cell: ({ row }) => rightAlignedCell({ row, key: 'wp' }) },
    { accessorKey: 'balks', header: ({ column }) => sortableHeader({ column, key: 'BALK', title: 'Balks' }), cell: ({ row }) => rightAlignedCell({ row, key: 'balks' }) },
    { accessorKey: 'ir', header: ({ column }) => sortableHeader({ column, key: 'IR', title: 'Inherited Runners' }), cell: ({ row }) => rightAlignedCell({ row, key: 'ir' }) },
    { accessorKey: 'irs', header: ({ column }) => sortableHeader({ column, key: 'IRS', title: 'Inherited Runners Stranded' }), cell: ({ row }) => rightAlignedCell({ row, key: 'irs' }) },
    { accessorKey: 'e', header: ({ column }) => sortableHeader({ column, key: 'E', title: 'Errors' }), cell: ({ row }) => rightAlignedCell({ row, key: 'e' }) },
    { accessorKey: 'dpi', header: ({ column }) => sortableHeader({ column, key: 'DPI', title: 'Double Plays Induced' }), cell: ({ row }) => rightAlignedCell({ row, key: 'dpi' }) },
    { accessorKey: 'bra', header: ({ column }) => sortableHeader({ column, key: 'BRA', title: 'Baserunners Allowed' }), cell: ({ row }) => rightAlignedCell({ row, key: 'bra' }) },
    { accessorKey: 'perfect_game', header: ({ column }) => sortableHeader({ column, key: 'PG', title: 'Perfect Game' }), cell: ({ row }) => rightAlignedCell({ row, key: 'perfect_game' }) },
    { accessorKey: 'no_hitter', header: ({ column }) => sortableHeader({ column, key: 'NH', title: 'No-Hitter' }), cell: ({ row }) => rightAlignedCell({ row, key: 'no_hitter' }) },
    { accessorKey: 'relief_loss', header: ({ column }) => sortableHeader({ column, key: 'RL', title: 'Relief Loss' }), cell: ({ row }) => rightAlignedCell({ row, key: 'relief_loss' }) },
]

// Columns that should always be visible regardless of viewport
const ALWAYS_SHOW = new Set(['name', 'positions', 'FAN_total', 'actions', 'team_assigned'])
const hideStats = cols => cols.map(col =>
    ALWAYS_SHOW.has(col.accessorKey) || ALWAYS_SHOW.has(col.id)
        ? col
        : { ...col, meta: { ...(col.meta ?? {}), className: 'xl:table-cell' } }
)

export default {
    FAN_columns_hit: hideStats(FAN_columns_hit),
    FAN_columns_pitch: hideStats(FAN_columns_pitch),
    RAW_columns_hit: hideStats(RAW_columns_hit),
    RAW_columns_pitch: hideStats(RAW_columns_pitch),
    statlineColumns_hit
}
