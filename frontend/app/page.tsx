import { BackendStatus } from "@/components/BackendStatus";
import Link from "next/link";

export default function Home() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">V</div>
          <div>
            <p className="brand-name">VoxHire</p>
            <p className="brand-caption">LOCAL COACH</p>
          </div>
        </div>

        <nav className="primary-nav" aria-label="Primary navigation">
          <Link className="nav-item nav-item--active" href="/">Overview</Link>
          <a className="nav-item nav-item--disabled" href="#sessions">Sessions</a>
          <a className="nav-item nav-item--disabled" href="#library">Question library</a>
        </nav>

        <div className="sidebar-footer">
          <span className="privacy-badge">Private by default</span>
          <p>Runs on this machine. Your practice data stays local.</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">WORKSPACE / OVERVIEW</p>
            <h1>Interview readiness, at a glance.</h1>
          </div>
          <BackendStatus />
        </header>

        <section className="hero-panel" aria-labelledby="welcome-heading">
          <div className="hero-copy">
            <p className="eyebrow eyebrow--bright">NEXT STEP</p>
            <h2 id="welcome-heading">Build a sharper interview story.</h2>
            <p>Bring your resume and a target role when you are ready. VoxHire will turn them into a focused practice session.</p>
            <button className="primary-button" type="button" disabled>Start a practice session</button>
          </div>
          <div className="signal-graphic" aria-hidden="true">
            <span className="signal-ring signal-ring--outer" />
            <span className="signal-ring signal-ring--inner" />
            <span className="signal-core" />
          </div>
        </section>

        <section className="metric-grid" aria-label="Workspace summary">
          <article className="metric-card">
            <p className="metric-label">PRACTICE SESSIONS</p>
            <p className="metric-value">--</p>
            <p className="metric-note">No sessions yet</p>
          </article>
          <article className="metric-card">
            <p className="metric-label">READINESS SIGNAL</p>
            <p className="metric-value metric-value--muted">Waiting</p>
            <p className="metric-note">Complete a session to see this</p>
          </article>
          <article className="metric-card">
            <p className="metric-label">LOCAL SERVICES</p>
            <p className="metric-value">1 / 1</p>
            <p className="metric-note">Foundation services online</p>
          </article>
        </section>

        <section className="empty-state" id="sessions">
          <div className="empty-state-line" aria-hidden="true" />
          <div>
            <p className="eyebrow">SESSION HISTORY</p>
            <h2>Your practice history will appear here.</h2>
            <p>Milestone 1 is ready for the interview workflow. Your first session will populate this space.</p>
          </div>
        </section>
      </main>
    </div>
  );
}
