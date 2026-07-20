import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://crisorafunction-pgammcpdjr.cn-hangzhou.fcapp.run'

const scenarios = [
  'Data Breach (100k User Records Exposed)',
  'Rogue Executive Tweet Flounders Stock',
  'Critical Cloud Infrastructure Outage',
]

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

function formatPercent(value) {
  return `${value}%`
}

function scoreTone(value) {
  if (value >= 80) return 'emerald'
  if (value >= 60) return 'amber'
  return 'rose'
}

function MetricCard({ label, value, hint, accent }) {
  return (
    <div className={`metric-card metric-${accent}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {hint ? <div className="metric-hint">{hint}</div> : null}
    </div>
  )
}

function SpeechCard({ title, tone, text }) {
  return (
    <article className={`speech-card speech-${tone}`}>
      <div className="speech-title">{title}</div>
      <p>{text}</p>
    </article>
  )
}

function App() {
  useEffect(() => {
    document.getElementById('boot-screen')?.remove()
  }, [])

  const [crisisType, setCrisisType] = useState(scenarios[0])
  const [severity, setSeverity] = useState(8)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const utilityGain = result?.delta?.utility_gain ?? 0
  const baselineScore = result?.baseline?.metrics?.overall_utility ?? 0
  const societyScore = result?.society?.metrics?.overall_utility ?? 0
  const consensus = result?.society?.arbitrator?.consensus_status ?? 'PENDING'
  const statusTone = useMemo(() => {
    if (consensus === 'RESOLVED') return 'emerald'
    if (consensus === 'RENEGOTIATE') return 'amber'
    return 'slate'
  }, [consensus])

  async function handleRun() {
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/api/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          crisis_type: crisisType,
          severity,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data?.detail || 'Simulation failed')
      }

      setResult(data)
    } catch (err) {
      setError(err.message || 'Unable to reach the crisis engine')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="shell">
      <div className="bg-orb orb-one" />
      <div className="bg-orb orb-two" />
      <div className="noise" />

      <main className="app-grid">
        <aside className="control-rail glass-panel">
          <div className="eyebrow">Crisis Orchestration</div>
          <h1>Crisora</h1>
          <p className="lede">
            A Crisis Orchestration platform for your Qwen-powered legal, PR, and arbitrator agents.
          </p>

          <div className="control-group">
            <label htmlFor="scenario">Scenario</label>
            <select id="scenario" value={crisisType} onChange={(event) => setCrisisType(event.target.value)}>
              {scenarios.map((scenario) => (
                <option key={scenario} value={scenario}>
                  {scenario}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <div className="control-head">
              <label htmlFor="severity">Panic severity</label>
              <span>{severity}/10</span>
            </div>
            <input
              id="severity"
              type="range"
              min="1"
              max="10"
              value={severity}
              onChange={(event) => setSeverity(Number(event.target.value))}
            />
          </div>

          <button className="run-button" onClick={handleRun} disabled={loading}>
            {loading ? 'Orchestrating...' : 'Execute Simulation Run'}
          </button>

          <div className="status-strip">
            <span>Backend</span>
            {/* <strong>{API_BASE ? API_BASE.replace(/^https?:\/\//, '') : 'localhost:8000'}</strong> */}
            <strong>{API_BASE ? API_BASE.replace(/^https?:\/\//, '') : 'https://crisorafunction-pgammcpdjr.cn-hangzhou.fcapp.run'}</strong>
          </div>

          <div className="mini-grid">
            <div>
              <span>Baseline</span>
              <strong>{formatPercent(baselineScore)}</strong>
            </div>
            <div>
              <span>Society</span>
              <strong>{formatPercent(societyScore)}</strong>
            </div>
            <div>
              <span>Delta</span>
              <strong className={scoreTone(utilityGain)}>{utilityGain > 0 ? `+${utilityGain}` : utilityGain}</strong>
            </div>
          </div>
        </aside>

        <section className="content-stack">
          <header className="hero glass-panel">
            <div className="hero-copy">
              <div className="eyebrow">Agent Society</div>
              <h2>Multi-Agent PR Crisis Matrix</h2>
              <p>
                Instead of a standard chatbot, we are built an asynchronous, multi-agent negotiation playground for the business that faces a massive, sudden crisis (e.g., a data breach, a rogue viral tweet, or a supply chain collapse).
              </p>
            </div>

            <div className={`consensus-badge ${statusTone}`}>
              <span>Consensus</span>
              <strong>{consensus}</strong>
            </div>
          </header>

          {error ? <div className="error-banner glass-panel">{error}</div> : null}

          {!result ? (
            <section className="empty-state glass-panel">
              <div>
                <div className="empty-kicker">Awaiting simulation</div>
                <h3>Launch a crisis to populate the boardroom.</h3>
                <p>
                  You’ll get a baseline response, parallel legal and PR drafts, the arbitrator synthesis, and the final
                  performance delta in a much more premium presentation.
                </p>
              </div>

              <div className="feature-grid">
                <MetricCard label="Phase 1" value="Baseline" hint="Single-agent control sample" accent="slate" />
                <MetricCard label="Phase 2" value="Negotiation" hint="Legal and PR collision" accent="amber" />
                <MetricCard label="Phase 3" value="Resolution" hint="Boardroom synthesis output" accent="emerald" />
              </div>
            </section>
          ) : (
            <>
              <section className="metrics-row">
                <MetricCard
                  label="Baseline single-agent score"
                  value={formatPercent(result.baseline.metrics.overall_utility)}
                  hint="Raw generic assistant output"
                  accent="slate"
                />
                <MetricCard
                  label="Agent society score"
                  value={formatPercent(result.society.metrics.overall_utility)}
                  hint="Negotiated multi-agent result"
                  accent="emerald"
                />
                <MetricCard
                  label="Measured efficiency gain"
                  value={`+${result.delta.utility_gain}%`}
                  hint="Relative lift from orchestration"
                  accent={scoreTone(result.delta.utility_gain)}
                />
              </section>

              <section className="phase-card glass-panel">
                <div className="phase-head">
                  <div>
                    <div className="eyebrow">Phase 1</div>
                    <h3>Single-agent baseline</h3>
                  </div>
                  <span className={`pill ${scoreTone(result.baseline.metrics.overall_utility)}`}>
                    Utility {result.baseline.metrics.overall_utility}
                  </span>
                </div>

                <div className="split-panel">
                  <article className="output-card">
                    <div className="output-label">Baseline agent output</div>
                    <pre>{result.baseline.text}</pre>
                  </article>

                  <article className="gauge-card">
                    <div className="gauge-copy">
                      <div className="output-label">Score profile</div>
                      <strong>{result.baseline.metrics.overall_utility}%</strong>
                      <p>The control case keeps the orchestration story measurable.</p>
                    </div>
                    <div className="gauge-shell">
                      <div className="gauge-track">
                        <div
                          className="gauge-fill gauge-slate"
                          style={{ width: `${result.baseline.metrics.overall_utility}%` }}
                        />
                      </div>
                      <div className="gauge-track">
                        <div
                          className="gauge-fill gauge-emerald"
                          style={{ width: `${result.society.metrics.overall_utility}%` }}
                        />
                      </div>
                    </div>
                  </article>
                </div>
              </section>

              <section className="phase-card glass-panel">
                <div className="phase-head">
                  <div>
                    <div className="eyebrow">Phase 2</div>
                    <h3>Negotiation loop</h3>
                  </div>
                  <span className="pill amber">Parallel drafts</span>
                </div>

                <div className="chat-grid">
                  <SpeechCard title="Legal council" tone="rose" text={result.society.legal_draft} />
                  <SpeechCard title="PR guardian" tone="sky" text={result.society.pr_draft} />
                </div>
              </section>

              <section className="phase-card glass-panel">
                <div className="phase-head">
                  <div>
                    <div className="eyebrow">Phase 2.5</div>
                    <h3>Arbitrator synthesis</h3>
                  </div>
                  <span className={`pill ${statusTone}`}>{result.society.arbitrator.consensus_status}</span>
                </div>

                <div className="arbitrator-card">
                  <div className="output-label">Reasoning</div>
                  <p>{result.society.arbitrator.reasoning || 'No structured reasoning returned by the model.'}</p>
                  <div className="final-statement">
                    <div className="output-label">Final statement</div>
                    <p>{result.society.arbitrator.final_statement}</p>
                  </div>
                </div>
              </section>

              <section className="phase-card glass-panel">
                <div className="phase-head">
                  <div>
                    <div className="eyebrow">Phase 3</div>
                    <h3>Performance delta</h3>
                  </div>
                  <span className={`pill ${scoreTone(result.delta.utility_gain)}`}>+{result.delta.utility_gain}%</span>
                </div>

                <div className="delta-table">
                  <div>
                    <span>Baseline utility</span>
                    <strong>{result.baseline.metrics.overall_utility}%</strong>
                  </div>
                  <div>
                    <span>Society utility</span>
                    <strong>{result.society.metrics.overall_utility}%</strong>
                  </div>
                  <div>
                    <span>Gain</span>
                    <strong className="emerald">+{result.delta.utility_gain}%</strong>
                  </div>
                </div>
              </section>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default App