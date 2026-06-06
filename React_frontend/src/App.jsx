import { useState, useCallback, useRef } from "react";
import API from "./services/api";

// ─── Score ring SVG ────────────────────────────────────────────────────────
function ScoreRing({ score, size = 72 }) {
  const r = 26;
  const circ = 2 * Math.PI * r;
  const fill = Math.max(0, Math.min(score || 0, 100)) / 100 * circ;
  const color = score >= 75 ? "#4ade80" : score >= 50 ? "#fbbf24" : "#f87171";
  return (
    <svg width={size} height={size} viewBox="0 0 60 60" className="shrink-0">
      <circle cx="30" cy="30" r={r} fill="none" stroke="#1e293b" strokeWidth="5" />
      <circle cx="30" cy="30" r={r} fill="none" stroke={color} strokeWidth="5"
        strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 30 30)"
        style={{ transition: "stroke-dasharray 1s cubic-bezier(.4,0,.2,1)" }}
      />
      <text x="30" y="35" textAnchor="middle" fill={color} fontSize="10" fontWeight="800">
        {Math.round(score || 0)}
      </text>
    </svg>
  );
}

// ─── Pill badge ────────────────────────────────────────────────────────────
function Pill({ children, color = "amber" }) {
  const cls = {
    amber: "bg-amber-500/10 text-amber-300 border-amber-500/25",
    red:   "bg-red-500/10   text-red-300   border-red-500/25",
    slate: "bg-slate-700/50 text-slate-300  border-slate-600/30",
    green: "bg-green-500/10 text-green-300  border-green-500/25",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${cls[color]}`}>
      {children}
    </span>
  );
}

// ─── Stat card ─────────────────────────────────────────────────────────────
function StatCard({ label, value, valueClass = "text-white" }) {
  return (
    <div className="bg-slate-900/70 border border-slate-700/40 rounded-2xl p-5">
      <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">{label}</p>
      <p className={`text-4xl font-black tabular-nums ${valueClass}`}>{value}</p>
    </div>
  );
}

// ─── Drag-and-drop upload zone ─────────────────────────────────────────────
function DropZone({ label, hint, multiple, onChange, files }) {
  const inputRef = useRef();
  const [drag, setDrag] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDrag(false);
    const dropped = Array.from(e.dataTransfer.files).filter(f => f.type === "application/pdf");
    if (!dropped.length) return;
    onChange(multiple ? dropped : dropped[0]);
  }, [multiple, onChange]);

  const names = files ? (Array.isArray(files) ? files : [files]) : [];

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={e => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
      className={`relative rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-150
        ${drag ? "border-amber-400 bg-amber-500/5" : "border-slate-700 hover:border-slate-500 bg-slate-800/30"}`}
    >
      <input ref={inputRef} type="file" accept=".pdf" multiple={multiple} className="hidden"
        onChange={e => onChange(multiple ? Array.from(e.target.files) : e.target.files[0])} />

      <div className="flex flex-col items-center gap-3 py-8 px-4 text-center">
        <div className="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-bold text-slate-200">{label}</p>
          <p className="text-xs text-slate-500 mt-0.5">{hint}</p>
        </div>
        {names.length > 0 && (
          <div className="flex flex-wrap gap-1.5 justify-center">
            {names.map((f, i) => <Pill key={i} color="green">✓ {f.name}</Pill>)}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Weight slider (auto-balancing) ────────────────────────────────────────
// When you move one slider, the remaining two share the leftover equally.
function Slider({ label, value, onChange }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-400">{label}</span>
        <span className="text-xs font-bold text-amber-400 tabular-nums w-10 text-right">
          {(value * 100).toFixed(0)}%
        </span>
      </div>
      <input type="range" min={0} max={1} step={0.01} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 rounded-full accent-amber-400 cursor-pointer" />
    </div>
  );
}

// ─── Candidate card ────────────────────────────────────────────────────────
function CandidateCard({ candidate, rank }) {
  const [open, setOpen] = useState(false);
  const score = candidate.analytics?.final_score ?? 0;
  const scoreColor = score >= 75 ? "text-green-400" : score >= 50 ? "text-amber-400" : "text-red-400";
  const insights = candidate.premium_insights;

  return (
    <div className="bg-slate-900/70 border border-slate-700/40 rounded-2xl overflow-hidden">
      {/* summary row */}
      <div onClick={() => setOpen(o => !o)}
        className="flex items-center gap-4 p-5 cursor-pointer hover:bg-slate-800/50 transition-colors">
        <span className="text-xs font-black text-amber-400 w-7 shrink-0 text-center">#{rank}</span>
        <ScoreRing score={score} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-white truncate">{candidate.dossier?.name || "Unknown"}</p>
          <p className="text-xs text-slate-500 mt-0.5">
            GPA <span className="text-slate-300">{candidate.dossier?.gpa || "—"}</span>
            {candidate.dossier?.emails?.[0] && (
              <> · <span className="truncate">{candidate.dossier.emails[0]}</span></>
            )}
          </p>
        </div>
        <span className={`text-2xl font-black tabular-nums shrink-0 ${scoreColor}`}>{score.toFixed(1)}</span>
        <svg className={`w-4 h-4 text-slate-600 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* expanded */}
      {open && (
        <div className="border-t border-slate-800 p-5 grid md:grid-cols-2 gap-6 text-sm">
          {/* left: skills + contact */}
          <div className="space-y-4">
            <div>
              <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">Skills Found</p>
              <div className="flex flex-wrap gap-1.5">
                {candidate.analytics?.skills_found?.length
                  ? candidate.analytics.skills_found.map((s, i) => <Pill key={i} color="amber">{s}</Pill>)
                  : <span className="text-xs text-slate-600">None detected</span>}
              </div>
            </div>

            {candidate.analytics?.missing_skills?.length > 0 && (
              <div>
                <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">Missing Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {candidate.analytics.missing_skills.map((s, i) => <Pill key={i} color="red">{s}</Pill>)}
                </div>
              </div>
            )}

            <div>
              <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">Contact</p>
              {candidate.dossier?.emails?.map((e, i) => <p key={i} className="text-xs text-slate-300">✉ {e}</p>)}
              {candidate.dossier?.phones?.map((p, i) => <p key={i} className="text-xs text-slate-300">📞 {p}</p>)}
            </div>
          </div>

          {/* right: AI insights */}
          {insights && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <p className="text-xs font-bold tracking-widest text-slate-500 uppercase">AI Quality Score</p>
                <span className="text-lg font-black text-amber-400">{insights.quality_score}/100</span>
              </div>

              {insights.suggestions?.length > 0 && (
                <div>
                  <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">Suggestions</p>
                  <ul className="space-y-1.5">
                    {insights.suggestions.map((s, i) => (
                      <li key={i} className="text-xs text-slate-300 flex gap-2">
                        <span className="text-amber-500 shrink-0">→</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {insights.interview_questions?.length > 0 && (
                <div>
                  <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-2">Interview Questions</p>
                  <ol className="space-y-1.5 list-decimal list-inside">
                    {insights.interview_questions.map((q, i) => (
                      <li key={i} className="text-xs text-slate-300">{q}</li>
                    ))}
                  </ol>
                </div>
              )}

              {insights.fraud_alerts?.length > 0 && (
                <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                  <p className="text-xs font-bold text-red-400 mb-1">⚠ Fraud Alerts</p>
                  {insights.fraud_alerts.map((a, i) => (
                    <p key={i} className="text-xs text-red-300">{a}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Rejected row ──────────────────────────────────────────────────────────
function RejectedRow({ candidate }) {
  return (
    <div className="bg-red-950/20 border border-red-900/30 rounded-2xl p-4 flex items-center gap-4">
      <div className="w-8 h-8 rounded-lg bg-red-500/15 flex items-center justify-center shrink-0">
        <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-slate-300 truncate">{candidate.dossier?.name || candidate.filename}</p>
        <p className="text-xs text-red-400">{candidate.reason}</p>
      </div>
      <Pill color="red">GPA {candidate.dossier?.gpa || "—"}</Pill>
    </div>
  );
}

// ─── History panel ─────────────────────────────────────────────────────────
function HistoryPanel({ onLoad }) {
  const [open, setOpen] = useState(false);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await API.get("/api/history");
      setRecords(res.data.analyses || []);
    } catch {
      alert("Cannot connect to Node backend. Make sure it is running on port 3000.");
    } finally {
      setLoading(false);
    }
  }

  async function loadOne(id) {
    try {
      const res = await API.get(`/api/history/${id}`);
      onLoad(res.data);
      setOpen(false);
    } catch {
      alert("Failed to load record.");
    }
  }

  async function deleteOne(e, id) {
    e.stopPropagation();
    if (!confirm("Delete this record?")) return;
    await API.delete(`/api/history/${id}`);
    setRecords(r => r.filter(x => x._id !== id));
  }

  return (
    <div className="relative">
      <button
        onClick={() => { setOpen(o => !o); if (!open) load(); }}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold text-slate-300 hover:bg-slate-700 transition-colors"
      >
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        History
      </button>

      {open && (
        <div className="absolute right-0 top-11 z-50 w-80 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800">
            <p className="text-xs font-bold tracking-widest text-slate-500 uppercase">Past Analyses</p>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {loading && <p className="text-xs text-slate-500 text-center py-6">Loading…</p>}
            {!loading && !records.length && <p className="text-xs text-slate-600 text-center py-6">No history yet.</p>}
            {records.map(r => (
              <div key={r._id}
                onClick={() => loadOne(r._id)}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-800 cursor-pointer border-b border-slate-800/50 last:border-0"
              >
                <div>
                  <p className="text-xs font-semibold text-slate-300">
                    {r.batch_info?.total_processed || 0} candidates · {r.batch_info?.successful || 0} passed
                  </p>
                  <p className="text-xs text-slate-600">
                    GPA cutoff {r.gpa_cutoff_applied} · {new Date(r.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <button onClick={e => deleteOne(e, r._id)}
                  className="text-slate-600 hover:text-red-400 transition-colors ml-2 shrink-0">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── App ───────────────────────────────────────────────────────────────────
export default function App() {
  const [jd, setJd] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [weights, setWeights] = useState({ gpa: 0.3, tech: 0.5, sem: 0.2 });
  const [demo, setDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [tab, setTab] = useState("shortlisted");
  const resultsRef = useRef();

  // Move one slider → others auto-adjust proportionally so sum always = 1.0
  function changeWeight(key, newVal) {
    const clamped = Math.min(0.98, Math.max(0.01, parseFloat(newVal.toFixed(2))));
    const others = Object.keys(weights).filter(k => k !== key);
    const remaining = parseFloat((1 - clamped).toFixed(2));
    const prevTotal = others.reduce((s, k) => s + weights[k], 0);
    const next = { ...weights, [key]: clamped };
    if (prevTotal < 0.01) {
      others.forEach(k => { next[k] = parseFloat((remaining / others.length).toFixed(2)); });
    } else {
      others.forEach(k => { next[k] = parseFloat(((weights[k] / prevTotal) * remaining).toFixed(2)); });
    }
    // Fix floating-point drift
    const drift = parseFloat((1 - Object.values(next).reduce((a, b) => a + b, 0)).toFixed(2));
    const biggest = others.reduce((a, b) => next[a] >= next[b] ? a : b);
    next[biggest] = parseFloat((next[biggest] + drift).toFixed(2));
    setWeights(next);
  }

  async function run() {
    if (!demo && (!jd || !resumes.length)) {
      alert("Please upload a JD and at least one resume.");
      return;
    }

    const fd = new FormData();
    fd.append("w_gpa",  weights.gpa);
    fd.append("w_tech", weights.tech);
    fd.append("w_sem",  weights.sem);
    fd.append("demo_mode", demo ? "true" : "false");

    if (demo) {
      fd.append("jd_pdf",  new Blob(["demo"], { type: "application/pdf" }), "demo_jd.pdf");
      fd.append("resumes", new Blob(["demo"], { type: "application/pdf" }), "demo_resume.pdf");
    } else {
      fd.append("jd_pdf", jd);
      resumes.forEach(r => fd.append("resumes", r));
    }

    try {
      setLoading(true);
      setResults(null);
      const res = await API.post("/api/proxy/analyze", fd);
      setResults(res.data);
      setTab("shortlisted");
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (err) {
      alert("Error: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  }

  const shortlisted = results?.ranked_candidates || [];
  const rejected    = results?.rejected_candidates || [];
  const errors      = results?.errors || [];

  return (
    <div className="min-h-screen bg-[#060c18] text-white">
      {/* grid bg */}
      <div className="fixed inset-0 pointer-events-none"
        style={{ backgroundImage: "linear-gradient(#1e293b44 1px,transparent 1px),linear-gradient(to right,#1e293b44 1px,transparent 1px)", backgroundSize: "48px 48px" }} />

      {/* header */}
      <header className="sticky top-0 z-40 bg-[#060c18]/80 backdrop-blur-xl border-b border-slate-800/60">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-black" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
              </svg>
            </div>
            <span className="text-sm font-black tracking-tight">RecruitAI</span>
            <span className="hidden sm:inline text-xs text-slate-600 border-l border-slate-800 pl-2.5">
              Llama 3.3 · BERT · MongoDB
            </span>
          </div>
          <HistoryPanel onLoad={d => { setResults(d); setTab("shortlisted"); setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth" }), 100); }} />
        </div>
      </header>

      <main className="relative max-w-4xl mx-auto px-6 py-14 space-y-10">

        {/* hero */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-400 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            AI Recruitment Pipeline
          </div>
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight leading-[1.05]">
            Screen smarter.<br /><span className="text-amber-400">Hire faster.</span>
          </h1>
          <p className="text-slate-400 max-w-md mx-auto">
            Upload a Job Description + up to 10 resumes. Our hybrid NLP + LLM pipeline extracts, scores, and ranks every candidate instantly.
          </p>
        </div>

        {/* upload + config */}
        <div className="bg-slate-900/50 border border-slate-700/40 rounded-3xl p-6 sm:p-8 space-y-6 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-black">Upload Center</h2>
            <label className="flex items-center gap-2 cursor-pointer">
              <span className="text-xs text-slate-500">Demo mode</span>
              <button onClick={() => setDemo(d => !d)}
                className={`relative w-9 h-5 rounded-full transition-colors ${demo ? "bg-amber-500" : "bg-slate-700"}`}>
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${demo ? "translate-x-4" : ""}`} />
              </button>
            </label>
          </div>

          {!demo ? (
            <div className="grid sm:grid-cols-2 gap-4">
              <DropZone label="Job Description" hint="PDF only · drag & drop or click"
                multiple={false} onChange={setJd} files={jd} />
              <DropZone label="Resumes (up to 10)" hint="PDF only · drag & drop or click"
                multiple onChange={setResumes} files={resumes.length ? resumes : null} />
            </div>
          ) : (
            <div className="rounded-xl bg-amber-500/8 border border-amber-500/20 p-4 text-center text-xs text-amber-300">
              Demo mode — sample results will be returned without uploading real files.
            </div>
          )}

          {/* weight sliders */}
          <div className="space-y-3 pt-1">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-bold tracking-widest text-slate-500 uppercase">Scoring Weights</p>
              <span className="text-xs text-slate-500 italic">drag any slider — others auto-adjust</span>
            </div>
            <Slider label="GPA"            value={weights.gpa}  onChange={v => changeWeight("gpa",  v)} />
            <Slider label="Tech Skills"    value={weights.tech} onChange={v => changeWeight("tech", v)} />
            <Slider label="Semantic Match" value={weights.sem}  onChange={v => changeWeight("sem",  v)} />
          </div>

          <button onClick={run}
            disabled={loading || (!demo && (!jd || !resumes.length))}
            className="w-full py-4 rounded-2xl font-black text-sm tracking-wide uppercase transition-all
              bg-amber-500 text-black hover:bg-amber-400 active:scale-[0.98]
              disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  Running AI Pipeline…
                </span>
              : "Analyze Candidates →"}
          </button>
        </div>

        {/* results */}
        {results && (
          <div ref={resultsRef} className="space-y-6">
            {/* stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <StatCard label="Processed"  value={results.batch_info?.total_processed ?? 0} />
              <StatCard label="Shortlisted" value={results.batch_info?.successful ?? 0} valueClass="text-green-400" />
              <StatCard label="Rejected"   value={results.batch_info?.rejected ?? 0}   valueClass="text-red-400" />
              <StatCard label="GPA Cutoff" value={results.gpa_cutoff_applied ?? "—"}   valueClass="text-amber-400" />
            </div>

            {/* tabs */}
            <div className="flex gap-1 bg-slate-900/60 border border-slate-800 rounded-xl p-1 w-fit">
              {[
                { key: "shortlisted", label: `Shortlisted (${shortlisted.length})` },
                { key: "rejected",    label: `Rejected (${rejected.length})` },
                ...(errors.length ? [{ key: "errors", label: `Errors (${errors.length})` }] : []),
              ].map(({ key, label }) => (
                <button key={key} onClick={() => setTab(key)}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all
                    ${tab === key ? "bg-amber-500 text-black" : "text-slate-400 hover:text-slate-200"}`}>
                  {label}
                </button>
              ))}
            </div>

            {tab === "shortlisted" && (
              <div className="space-y-3">
                {!shortlisted.length && <p className="text-center text-slate-600 py-12 text-sm">No candidates passed the cutoff.</p>}
                {shortlisted.map((c, i) => <CandidateCard key={i} candidate={c} rank={i + 1} />)}
              </div>
            )}

            {tab === "rejected" && (
              <div className="space-y-3">
                {!rejected.length && <p className="text-center text-slate-600 py-12 text-sm">No rejections.</p>}
                {rejected.map((c, i) => <RejectedRow key={i} candidate={c} />)}
              </div>
            )}

            {tab === "errors" && (
              <div className="space-y-3">
                {errors.map((e, i) => (
                  <div key={i} className="bg-red-950/20 border border-red-900/30 rounded-2xl p-4">
                    <p className="text-sm font-bold text-red-300">{e.filename}</p>
                    <p className="text-xs text-red-400 mt-1">{e.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800/40 py-6 text-center text-xs text-slate-700 mt-10">
        RecruitAI · FastAPI + Node.js + MongoDB + Groq Llama 3.3
      </footer>
    </div>
  );
}
