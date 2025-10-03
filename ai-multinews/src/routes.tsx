import { lazy } from 'react'
const Feed = lazy(() => import('./pages/Feed'))
const Article = lazy(() => import('./pages/Article'))
const Checks = lazy(() => import('./pages/Checks'))
const Settings = lazy(() => import('./pages/Settings'))

export default [
  { path: '/', element: <Feed /> },
  { path: '/article/:id', element: <Article /> },
  { path: '/checks', element: <Checks /> },
  { path: '/settings', element: <Settings /> },
]
