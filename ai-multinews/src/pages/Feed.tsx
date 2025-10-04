import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Badge from '../components/Badge'
import FactShieldScore from '../components/FactShieldScore'
import { ingest, getFeed } from '../lib/api'

function scoreOf(m: number, h: number, cred: number, agree: number) {
  return Math.round(100 - (50 * m + 30 * h + 10 * (1 - cred) + 10 * (1 - agree)))
}

export default function Feed() {
  const [newUrl, setNewUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const nav = useNavigate()

  const q = useQuery({
    queryKey: ['feed'],
    queryFn: () => getFeed(30, 0),
    refetchOnWindowFocus: false,
  })

  async function onIngest() {
    if (!newUrl) return
    try {
      setBusy(true); setErr(null)
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
      {q.isLoading ? (
        <div className="opacity-70">Loading feed…</div>
      ) : q.isError ? (
        <div className="text-red-600 text-sm">Failed to load feed.</div>
      ) : (
        <div className="space-y-4">
          {q.data?.items.length ? q.data.items.map((it) => {
            const score = scoreOf(it.m, it.h, it.cred, it.agree)
            return (
              <Link key={it.id} to={`/article/${it.id}`} className="block border rounded-2xl p-4 hover:bg-zinc-50">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="font-semibold line-clamp-2">{it.title}</h3>
                  <Badge>{it.source ?? 'Unknown'}</Badge>
                </div>
                <div className="mt-3 rounded-2xl border p-4 bg-white">
                  <FactShieldScore score={score} />
                </div>
                <div className="text-xs opacity-60 mt-1">Added: {new Date(it.created_at).toLocaleString()}</div>
              </Link>
            )
          }) : (
            <div className="opacity-70 text-sm">No articles yet. Try ingesting a URL above.</div>
          )}
        </div>
      )}
    </div>
  )
}

