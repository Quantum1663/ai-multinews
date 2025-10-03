import { useAppStore } from '../store/useAppStore'

export default function Settings() {
  const { lang, setLang, threshold, setThreshold } = useAppStore()
  return (
    <div className="space-y-6 max-w-xl">
      <div className="border rounded-2xl p-4">
        <h3 className="font-semibold mb-2">Language</h3>
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value as any)}
          className="border rounded-xl px-2 py-1"
        >
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
          <option value="ur">اردو</option>
        </select>
      </div>
      <div className="border rounded-2xl p-4">
        <h3 className="font-semibold mb-2">Risk threshold</h3>
        <input
          type="range" min={0} max={100}
          value={threshold}
          onChange={(e) => setThreshold(parseInt(e.target.value))}
          className="w-full"
        />
        <div className="text-sm mt-1">Current: {threshold}</div>
      </div>
    </div>
  )
}
