import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getArticle, classify, verify, factShieldScore } from '../lib/api'
import type { TClassifyOut, TVerifyOut } from '../lib/api'
import HighlightText from '../components/HighlightText'
import FactShieldScore from '../components/FactShieldScore'

type Loaded = {
  title: string
  text: string
  url?: string | null
  cls: TClassifyOut
  ver: TVerifyOut
  score: number
}

export default function Article() {
  const { id } = useParams()
  const [data, setData] = useState<Loaded | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    async function run() {
      try {
        setLoading(true)
        setErr(null)
        if (!id) throw new Error('No article id')
        const art = await getArticle(id)
        const cls = await classify(art.text, 'auto')
        const ver = await verify(art.text, art.url ?? undefined)
        const score = factShieldScore(cls.misinfo_prob, cls.hate_prob, ver.cred_score, ver.agree_score)
        if (!alive) return
        setData({ title: art.title, text: art.text, url: art.url ?? undefined, cls, ver, score })
      } catch (e: any) {
        if (!alive) return
        setErr(e?.message ?? 'Failed to load article')
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [id])

  if (loading) return <div className="grid place-items-center py-16">Loading…</div>
  if (err) return <div className="text-red-600">{err}</div>
  if (!data) return null

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <h1 className="text-2xl font-bold">{data.title}</h1>
        <HighlightText text={data.text} spans={data.cls.spans} />
      </div>
      <aside className="space-y-4">
        <FactShieldScore
          score={Math.round(data.score)}
          parts={[
            { name: 'Misinformation', value: data.cls.misinfo_prob },
            { name: 'Hate', value: data.cls.hate_prob },
            { name: 'Credibility', value: data.ver.cred_score },
            { name: 'Agreement', value: data.ver.agree_score },
          ]}
        />
        <div className="rounded-2xl border p-4">
          <h3 className="font-semibold mb-2">Corroborating sources</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            {data.ver.references.map((r, i) => (
              <li key={i}><a className="underline" href={r.url} target="_blank" rel="noreferrer">{r.title}</a></li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  )
}
