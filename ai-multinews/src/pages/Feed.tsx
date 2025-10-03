import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Badge from '../components/Badge'
import FactShieldScore from '../components/FactShieldScore'
import { ingest } from '../lib/api'

type FeedItem = {
  id: string
  title: string
  source: string
  m: number
  h: number
  cred: number
  agree: number
}

// Temporary seeded list (replace with real API later)
const items: FeedItem[] = [
  { id: '1', title: 'Article A', source: 'NDTV', m: 0.34, h: 0.12, cred: 0.8, agree: 0.7 },
  { id: '2', title: 'Article B', source: 'PIB', m: 0.10, h: 0.05, cred: 0.95, agree: 0.9 },
]

function scoreOf(it: FeedItem) {
  return Math.round(100 - (50 * it.m + 30 * it.h + 10 * (1 - it.cred) + 10 * (1 - it.agree)))
}

export default function Feed() {
  const [newUrl, setNewUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const nav = useNavigate()

  async function onIngest() {
    if (!newUrl) return
    try {
      setBusy(true)
      setErr(null)
      const res = await ingest({ url: newUrl })
      setNewUrl('')
      nav(`/article/${res.id}`)
    } catch (e: any) {
      setErr(e?.message ?? 'Failed to ingest URL')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Ingest bar */}
      <div className="rounded-2xl border p-4 bg-zinc-50">
        <div className="flex flex-col md:flex-row gap-2">
          <input
            className="flex-1 border rounded-2xl px-3 py-2 bg-white"
            placeholder="Paste a news URL to ingest (e.g., https://example.com/article)"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
          />
          <button
            onClick={onIngest}
            disabled={!newUrl || busy}
            className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-50"
          >
            {busy ? 'Ingesting…' : 'Ingest'}
          </button>
        </div>
        {err && <p className="text-sm text-red-600 mt-2">{err}</p>}
      </div>

      {/* Feed list */}
      <div className="space-y-4">
        {items.map((it) => (
          <Link
            key={it.id}
            to={`/article/${it.id}`}
            className="block border rounded-2xl p-4 hover:bg-zinc-50"
          >
            <div className="flex items-center justify-between gap-4">
              <h3 className="font-semibold">{it.title}</h3>
              <Badge>{it.source}</Badge>
            </div>

            <div className="mt-3 rounded-2xl border p-4 bg-white">
              <FactShieldScore score={scoreOf(it)} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
