import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

export default function Standings() {
    const [standings, setStandings] = useState([])
    const [season, setSeason] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        axios.get('/api/season')
            .then(res => setSeason(res.data.season))
            .catch(err => console.error(err))
    }, [])

    useEffect(() => {
        if (!season) return
        setLoading(true)
        axios.get(`/api/standings/${season}`)
            .then(res => { setStandings(res.data); setLoading(false) })
            .catch(err => { console.error(err); setLoading(false) })
    }, [season])

    return (
        <div className="p-4 max-w-lg">
            <h2 className="text-xl font-semibold mb-4">Standings {season}</h2>
            {loading ? (
                <p className="text-muted-foreground text-sm">Loading...</p>
            ) : standings.length === 0 ? (
                <p className="text-muted-foreground text-sm">No scoring data yet for {season}.</p>
            ) : (
                <table className="w-full text-sm border rounded-md overflow-hidden">
                    <thead>
                        <tr className="border-b bg-muted">
                            <th className="text-left px-3 py-2 font-medium">#</th>
                            <th className="text-left px-3 py-2 font-medium">Team</th>
                            <th className="text-right px-3 py-2 font-medium">Batting</th>
                            <th className="text-right px-3 py-2 font-medium">Pitching</th>
                            <th className="text-right px-3 py-2 font-medium bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {standings.map((row, i) => (
                            <tr key={row.team} className="border-b last:border-0 hover:bg-muted/50">
                                <td className="px-3 py-2 text-muted-foreground">{i + 1}</td>
                                <td className="px-3 py-2 font-medium"><Link to={`/team/${row.team}`} className="hover:underline">{row.team}</Link></td>
                                <td className="px-3 py-2 text-right tabular-nums">{row.bat_total.toFixed(1)}</td>
                                <td className="px-3 py-2 text-right tabular-nums">{row.pitch_total.toFixed(1)}</td>
                                <td className="px-3 py-2 text-right tabular-nums font-bold bg-orange-50 dark:bg-orange-950/40 text-orange-900 dark:text-orange-200">{row.total.toFixed(1)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
