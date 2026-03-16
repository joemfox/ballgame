import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

export default function Transactions() {
    const [transactions, setTransactions] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        axios.get('/api/transactions')
            .then(res => { setTransactions(res.data); setLoading(false) })
            .catch(err => { console.error(err); setLoading(false) })
    }, [])

    function formatDate(iso) {
        const d = new Date(iso)
        return d.toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
    }

    return (
        <div className="p-4 space-y-4 max-w-2xl">
            <h2 className="text-xl font-semibold">Transactions</h2>
            {loading ? (
                <p className="text-muted-foreground text-sm">Loading...</p>
            ) : transactions.length === 0 ? (
                <p className="text-muted-foreground text-sm">No transactions yet.</p>
            ) : (
                <table className="w-full text-sm border rounded-md overflow-hidden">
                    <thead>
                        <tr className="border-b bg-muted">
                            <th className="text-left px-3 py-2 font-medium">Date</th>
                            <th className="text-left px-3 py-2 font-medium">Team</th>
                            <th className="text-left px-3 py-2 font-medium">Type</th>
                            <th className="text-left px-3 py-2 font-medium">Player</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.map(t => (
                            <tr key={t.id} className="border-b last:border-0 hover:bg-muted/50">
                                <td className="px-3 py-2 text-muted-foreground whitespace-nowrap">{formatDate(t.timestamp)}</td>
                                <td className="px-3 py-2 font-medium">
                                    <Link to={`/team/${t.team}`} className="hover:underline">{t.team}</Link>
                                </td>
                                <td className="px-3 py-2">
                                    <span className={t.transaction_type === 'add'
                                        ? 'text-green-700 dark:text-green-400 font-medium'
                                        : 'text-red-700 dark:text-red-400 font-medium'}>
                                        {t.transaction_type === 'add' ? 'Add' : 'Drop'}
                                    </span>
                                </td>
                                <td className="px-3 py-2">
                                    {t.player_fg_id
                                        ? <Link to={`/player/${t.player_fg_id}`} className="hover:underline">{t.player_name}</Link>
                                        : t.player_name}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
