import { create } from 'zustand'

type State = {
  lang: 'en' | 'hi' | 'ur'
  setLang: (l: State['lang']) => void
  threshold: number
  setThreshold: (v: number) => void
}
export const useAppStore = create<State>((set) => ({
  lang: 'en',
  setLang: (lang) => set({ lang }),
  threshold: 75,
  setThreshold: (threshold) => set({ threshold }),
}))
