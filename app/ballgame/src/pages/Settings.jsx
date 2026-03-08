import { useState, useEffect } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function Settings({ onTeamUpdate }) {
    const [form, setForm] = useState({ city: '', abbreviation: '', nickname: '' })
    const [saved, setSaved] = useState(false)
    const [error, setError] = useState(null)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        axios.get('/api/team')
            .then(res => setForm(res.data))
            .catch(() => setError('Failed to load team info.'))
    }, [])

    const handleChange = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

    const handleSave = (e) => {
        e.preventDefault()
        setSaving(true)
        setError(null)
        setSaved(false)
        axios.patch('/api/team', form)
            .then(res => {
                setForm(res.data)
                setSaved(true)
                if (onTeamUpdate) onTeamUpdate(res.data.abbreviation)
            })
            .catch(err => setError(err.response?.data?.detail || 'Save failed.'))
            .finally(() => setSaving(false))
    }

    return (
        <div className="max-w-sm pt-2">
            <h2 className="text-lg font-semibold mb-4">Team Settings</h2>
            <form onSubmit={handleSave} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-1">City</label>
                    <Input value={form.city} onChange={handleChange('city')} />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1">Nickname</label>
                    <Input value={form.nickname} onChange={handleChange('nickname')} />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1">Abbreviation <span className="text-muted-foreground font-normal">(max 3 chars)</span></label>
                    <Input value={form.abbreviation} onChange={handleChange('abbreviation')} maxLength={3} className="w-24" />
                </div>
                {error && <p className="text-sm text-red-500">{error}</p>}
                {saved && <p className="text-sm text-green-600">Saved.</p>}
                <Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
            </form>
        </div>
    )
}
