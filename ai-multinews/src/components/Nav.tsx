import { Link, NavLink } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'

export default function Nav() {
  const { lang, setLang } = useAppStore()
  return (
    <header className="border-b">
      <div className="container flex items-center justify-between py-3">
        <Link to="/" className="font-bold text-lg">🛡️ FactShield</Link>
        <nav className="flex items-center gap-4">
          <NavLink to="/" className="hover:underline">Feed</NavLink>
          <NavLink to="/checks" className="hover:underline">Checks</NavLink>
          <NavLink to="/settings" className="hover:underline">Settings</NavLink>
          <select
            className="border rounded-xl px-2 py-1 text-sm"
            value={lang}
            onChange={(e) => setLang(e.target.value as any)}
          >
            <option value="en">EN</option>
            <option value="hi">हिं</option>
            <option value="ur">ارد</option>
          </select>
        </nav>
      </div>
    </header>
  )
}
