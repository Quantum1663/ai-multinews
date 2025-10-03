type Part = { name: string; value: number }
export default function FactShieldScore({ score, parts }: { score: number; parts?: Part[] }) {
  const bucket = score >= 75 ? 'Safe' : score >= 50 ? 'Warning' : 'High-Risk'
  return (
    <div className="rounded-2xl p-4 shadow border">
      <div className="text-xl font-semibold">FactShield: {Math.round(score)}/100</div>
      <div className="h-3 w-full bg-zinc-200 rounded mt-2 overflow-hidden">
        <div className="h-3 rounded bg-black/80" style={{ width: `${score}%` }} />
      </div>
      <div className="text-sm mt-2 opacity-80">Status: {bucket}</div>
      {parts && (
        <ul className="text-xs mt-2 space-y-1">
          {parts.map(p => (
            <li key={p.name} className="flex justify-between">
              <span>{p.name}</span><span>{Math.round(p.value*100)}%</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
