import ky from 'ky'
import { z } from 'zod'

/** Base HTTP client */
const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE,
  timeout: 30000,
})

/* =======================
   Schemas & exported types
   ======================= */
export const Span = z.object({
  start: z.number(),
  end: z.number(),
  weight: z.number().optional(),
})

export const ClassifyOut = z.object({
  hate_prob: z.number(),
  misinfo_prob: z.number(),
  spans: z.array(Span),
})
export type TClassifyOut = z.infer<typeof ClassifyOut>

export const VerifyOut = z.object({
  cred_score: z.number(),
  agree_score: z.number(),
  references: z.array(z.object({ title: z.string(), url: z.string() })),
})
export type TVerifyOut = z.infer<typeof VerifyOut>

export const IngestOut = z.object({
  ok: z.boolean(),
  id: z.string(),
})
export type TIngestOut = z.infer<typeof IngestOut>

export const MemeOut = z.object({
  clip_delta: z.number(),
  heatmap: z.string().optional(),
})
export type TMemeOut = z.infer<typeof MemeOut>

export const Article = z.object({
  id: z.string(),
  title: z.string(),
  source: z.string().nullable().optional(),
  url: z.string().nullable().optional(),
  text: z.string(),
})
export type TArticle = z.infer<typeof Article>

/* =============
   API functions
   ============= */

export async function classify(text: string, lang = 'auto') {
  const res = await api.post('classify', { json: { text, lang } }).json()
  return ClassifyOut.parse(res)
}

export async function verify(text: string, url?: string) {
  const res = await api.post('verify', { json: { text, url } }).json()
  return VerifyOut.parse(res)
}

export async function ingest(payload: { url?: string; text?: string; img_url?: string; lang?: string }) {
  const res = await api.post('ingest', { json: payload }).json()
  return IngestOut.parse(res)
}

export async function memeCheck(file: File, caption?: string) {
  const fd = new FormData()
  fd.append('img', file)
  if (caption) fd.append('caption', caption)
  const res = await api.post('meme-check', { body: fd }).json()
  return MemeOut.parse(res)
}

export async function getArticle(id: string) {
  const res = await api.get(`article/${id}`).json()
  return Article.parse(res)
}

/* =========
   Utilities
   ========= */

export function factShieldScore(m: number, h: number, cred: number, agree: number) {
  const score = 100 - (50 * m + 30 * h + 10 * (1 - cred) + 10 * (1 - agree))
  return Math.max(0, Math.min(100, score))
}
