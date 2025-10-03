import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { classify, verify, factShieldScore, memeCheck } from '../lib/api'
import FactShieldScore from '../components/FactShieldScore'
import HighlightText from '../components/HighlightText'

export default function Checks() {
  const [mode, setMode] = useState<'text'|'meme'>('text')

  // TEXT VERIFY MODE (already there)
  const [text, setText] = useState(''); const [url, setUrl] = useState('')
  const mut = useMutation({
    mutationFn: async () => {
      const cls = await classify(text, 'auto')
      const ver = await verify(text, url)
      const score = factShieldScore(cls.misinfo_prob, cls.hate_prob, ver.cred_score, ver.agree_score)
      return { cls, ver, score }
    },
  })

  // MEME MODE
  const [file, setFile] = useState<File | null>(null)
  const [caption, setCaption] = useState('')
  const memeMut = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file')
      return memeCheck(file, caption)
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <button className={`px-3 py-1 rounded-2xl border ${mode==='text'?'bg-black text-white':''}`} onClick={()=>setMode('text')}>Text/URL</button>
        <button className={`px-3 py-1 rounded-2xl border ${mode==='meme'?'bg-black text-white':''}`} onClick={()=>setMode('meme')}>Meme Check</button>
      </div>

      {mode==='text' ? (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-3">
            <input className="w-full border rounded-2xl px-3 py-2" placeholder="News URL (optional)" value={url} onChange={(e)=>setUrl(e.target.value)} />
            <textarea className="w-full border rounded-2xl px-3 py-2 min-h-[160px]" placeholder="Paste text to analyze" value={text} onChange={(e)=>setText(e.target.value)} />
            <button onClick={()=>mut.mutate()} className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-50" disabled={!text && !url || mut.isPending}>
              {mut.isPending ? 'Analyzing…' : 'Analyze'}
            </button>

            {mut.data && (
              <div className="space-y-4">
                <FactShieldScore
                  score={mut.data.score}
                  parts={[
                    { name: 'Misinformation', value: mut.data.cls.misinfo_prob },
                    { name: 'Hate', value: mut.data.cls.hate_prob },
                    { name: 'Credibility', value: mut.data.ver.cred_score },
                    { name: 'Agreement', value: mut.data.ver.agree_score },
                  ]}
                />
                <div>
                  <h3 className="font-semibold mb-2">Explanation</h3>
                  <HighlightText text={text} spans={mut.data.cls.spans} />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Corroborating sources</h3>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {mut.data.ver.references.map((r, i) => (
                      <li key={i}><a className="underline" href={r.url} target="_blank">{r.title}</a></li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-3 max-w-xl">
          <input type="file" accept="image/*" onChange={(e)=>setFile(e.target.files?.[0] || null)} />
          <input className="w-full border rounded-2xl px-3 py-2" placeholder="Caption (optional)" value={caption} onChange={(e)=>setCaption(e.target.value)} />
          <button onClick={()=>memeMut.mutate()} className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-50" disabled={!file || memeMut.isPending}>
            {memeMut.isPending ? 'Checking…' : 'Check Meme'}
          </button>
          {memeMut.data && (
            <div className="border rounded-2xl p-4">
              <div className="font-semibold">CLIP mismatch delta: {memeMut.data.clip_delta.toFixed(2)}</div>
              {memeMut.data.heatmap && <img src={memeMut.data.heatmap} alt="Heatmap" className="mt-2 rounded-xl" />}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
