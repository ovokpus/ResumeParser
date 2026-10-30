export type Parsed = {
  filename: string; name: string; email: string; skills: string[]
  skills_mode: 'llm' | 'keyword' | string; parser: string | null
  characters: number; text_preview: string; elapsed_ms: number
}
export type Health = { status: string; skills_mode: string; llm_enabled: boolean; model: string | null; formats: string[] }
export type Sample = { name: string; size: number }

async function handle<T>(r: Response): Promise<T> {
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`
    try { msg = (await r.json()).detail ?? msg } catch { /* not json */ }
    throw new Error(msg)
  }
  return r.json()
}
export const getHealth = () => fetch('/health').then(r => handle<Health>(r))
export const getSamples = () => fetch('/api/samples').then(r => handle<Sample[]>(r))
export const parseSample = (name: string) =>
  fetch(`/api/samples/${encodeURIComponent(name)}/parse`, { method: 'POST' }).then(r => handle<Parsed>(r))
export const parseUpload = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return fetch('/api/parse', { method: 'POST', body: fd }).then(r => handle<Parsed>(r))
}
