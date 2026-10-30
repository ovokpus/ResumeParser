import { useEffect, useRef, useState } from 'react'
import { getHealth, getSamples, parseSample, parseUpload, type Health, type Parsed, type Sample } from './api'

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [samples, setSamples] = useState<Sample[]>([])
  const [result, setResult] = useState<Parsed | null>(null)
  const [history, setHistory] = useState<Parsed[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [drag, setDrag] = useState(false)
  const input = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(e => setError(String(e)))
    getSamples().then(setSamples).catch(() => {})
  }, [])

  const run = async (p: Promise<Parsed>) => {
    setBusy(true); setError(null)
    try {
      const r = await p
      setResult(r)
      setHistory(h => [r, ...h.filter(x => x.filename !== r.filename)].slice(0, 8))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e)); setResult(null)
    } finally { setBusy(false) }
  }
  const onFiles = (files: FileList | null) => { if (files?.[0]) run(parseUpload(files[0])) }

  return (
    <div className="page">
      <header>
        <h1>📄 Resume Parser</h1>
        {health && (
          <span className={`mode ${health.skills_mode}`}>
            {health.llm_enabled ? `Skills: LLM (${health.model})` : 'Skills: offline keyword matching (no OpenAI key)'}
          </span>
        )}
      </header>
      <p className="sub">Upload a PDF or DOCX resume to extract <b>name</b>, <b>email</b> and <b>skills</b>.
        Uploaded files are parsed from a temporary file and not stored.</p>

      <div className="layout">
        <aside>
          <div className={`drop ${drag ? 'drag' : ''}`}
            onClick={() => input.current?.click()}
            onDragOver={e => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={e => { e.preventDefault(); setDrag(false); onFiles(e.dataTransfer.files) }}>
            <div className="big">⬆</div>
            <div>Drop a resume here or <u>browse</u></div>
            <div className="hint">.pdf or .docx, up to 10 MB</div>
            <input ref={input} type="file" accept=".pdf,.docx" hidden onChange={e => onFiles(e.target.files)} />
          </div>

          <h2>Synthetic samples</h2>
          <p className="hint">Fictional people, example.com emails, 555 numbers.</p>
          <ul className="samples">
            {samples.map(s => (
              <li key={s.name}>
                <button disabled={busy} onClick={() => run(parseSample(s.name))}>{s.name}</button>
                <span className="hint">{Math.round(s.size / 1024)} KB</span>
              </li>
            ))}
          </ul>

          {history.length > 0 && <>
            <h2>History</h2>
            <ul className="history">
              {history.map(h => <li key={h.filename} onClick={() => setResult(h)}>{h.name || '(no name)'} · {h.skills.length} skills</li>)}
            </ul>
          </>}
        </aside>

        <main>
          {busy && <div className="card">Parsing…</div>}
          {error && <div className="card error">⚠ {error}</div>}
          {!busy && !error && !result && <div className="card empty">Pick a sample or upload a file to see the parsed result.</div>}
          {result && !busy && (
            <div className="card">
              <div className="file">{result.filename} · {result.parser} · {result.characters} chars · {result.elapsed_ms} ms</div>
              <div className="fields">
                <div><label>Name</label><div className="val">{result.name || '—'}</div></div>
                <div><label>Email</label><div className="val">{result.email || '—'}</div></div>
              </div>
              <label>Skills ({result.skills.length}) <span className={`mode small ${result.skills_mode}`}>{result.skills_mode === 'llm' ? 'LLM' : 'keyword match'}</span></label>
              <div className="chips">{result.skills.map(s => <span key={s} className="chip">{s}</span>)}</div>
              <details open>
                <summary>JSON output</summary>
                <pre>{JSON.stringify({ name: result.name, email: result.email, skills: result.skills }, null, 2)}</pre>
              </details>
              <details>
                <summary>Extracted text (first 1,200 chars)</summary>
                <pre className="text">{result.text_preview}</pre>
              </details>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
