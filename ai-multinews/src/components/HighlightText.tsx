type Span = { start: number; end: number; weight?: number }
export default function HighlightText({ text, spans }: { text: string; spans: Span[] }) {
  const pieces: { t: string; h: boolean; w?: number }[] = []
  let i = 0
  spans.forEach(s => {
    if (i < s.start) pieces.push({ t: text.slice(i, s.start), h: false })
    pieces.push({ t: text.slice(s.start, s.end), h: true, w: s.weight ?? 0.7 })
    i = s.end
  })
  if (i < text.length) pieces.push({ t: text.slice(i), h: false })
  return (
    <p className="leading-7">
      {pieces.map((c, idx) => (
        <span
          key={idx}
          className={c.h ? 'rounded-sm' : ''}
          style={c.h ? { background: `rgba(255,225,100,${Math.min(0.95, 0.4 + 0.6*(c.w||0.7))})` } : {}}
        >
          {c.t}
        </span>
      ))}
    </p>
  )
}
