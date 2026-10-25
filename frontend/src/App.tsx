import React, { useState } from 'react';

interface RepositoryInfo {
  name: string;
  full_name: string;
  description: string | null;
  stars: number;
  forks: number;
  language: string | null;
  created_at: string;
  last_updated_at: string;
  open_issues_count: number;
  default_branch: string;
  is_archived: boolean;
  owner: string;
  owner_avatar_url: string | null;
  html_url: string;
  license_name: string | null;
  topics: string[];
  watchers_count: number;
  size_kb: number;
  network_count?: number;
  subscribers_count?: number;
  fetched_at: string;
}

interface ApiError {
  code: string;
  message: string;
  details?: string;
}

const SAMPLE_REPOSITORIES = [
  { label: 'fastapi/fastapi', url: 'https://github.com/fastapi/fastapi' },
  { label: 'pallets/flask', url: 'https://github.com/pallets/flask' },
  { label: 'psf/requests', url: 'https://github.com/psf/requests' },
  { label: 'facebook/react', url: 'https://github.com/facebook/react' },
];

const LANGUAGE_COLORS: Record<string, string> = {
  Python: '#3572A5',
  TypeScript: '#3178c6',
  JavaScript: '#f1e05a',
  Go: '#00ADD8',
  Rust: '#dea584',
  'C++': '#f34b7d',
  Java: '#b07219',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Ruby: '#701516',
};

// Helper: Format large numbers
function formatNumber(num: number): string {
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(1) + 'M';
  }
  if (num >= 1_000) {
    return (num / 1_000).toFixed(1) + 'k';
  }
  return num.toLocaleString();
}

// Helper: Format dates
function formatDate(isoStr: string): { formatted: string; relative: string } {
  if (!isoStr) return { formatted: 'N/A', relative: '' };
  try {
    const d = new Date(isoStr);
    const formatted = d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    const diffMs = Date.now() - d.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    let relative = '';
    if (diffDays <= 0) relative = 'today';
    else if (diffDays === 1) relative = 'yesterday';
    else if (diffDays < 30) relative = `${diffDays} days ago`;
    else if (diffDays < 365) relative = `${Math.floor(diffDays / 30)} months ago`;
    else relative = `${Math.floor(diffDays / 365)} years ago`;

    return { formatted, relative };
  } catch {
    return { formatted: isoStr, relative: '' };
  }
}

export const App: React.FC = () => {
  const [inputUrl, setInputUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [repoData, setRepoData] = useState<RepositoryInfo | null>(null);
  const [rateLimit, setRateLimit] = useState<{ remaining: number | null; reset: string | null } | null>(null);
  const [showRawJson, setShowRawJson] = useState<boolean>(false);

  const fetchRepositoryData = async (targetUrl: string) => {
    const cleanUrl = targetUrl.trim();
    if (!cleanUrl) {
      setError({
        code: 'EMPTY_INPUT',
        message: 'Please enter a GitHub repository URL or identifier (e.g. fastapi/fastapi).',
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    // Try relative endpoint via Vite proxy first, then fallback to direct backend URL
    const endpoints = [
      '/api/repository/analyze',
      'http://127.0.0.1:8000/api/repository/analyze',
    ];

    let lastError: ApiError | null = null;
    let fetchedSuccess = false;

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: cleanUrl }),
        });

        const json = await response.json();

        if (response.ok && json.success) {
          setRepoData(json.data);
          setRateLimit({
            remaining: json.rate_limit_remaining ?? null,
            reset: json.rate_limit_reset ?? null,
          });
          fetchedSuccess = true;
          break;
        } else {
          lastError = {
            code: json.error_code || `HTTP_${response.status}`,
            message: json.message || 'Failed to fetch repository information.',
            details: json.details,
          };
          // Don't retry if the backend gave a clean domain error (400, 404, 429)
          if (response.status === 400 || response.status === 404 || response.status === 429) {
            break;
          }
        }
      } catch (err: any) {
        lastError = {
          code: 'CONNECTION_FAILURE',
          message: 'Unable to reach backend service. Please verify that the FastAPI backend is running on port 8000.',
          details: err?.message || String(err),
        };
      }
    }

    if (!fetchedSuccess) {
      setError(lastError || {
        code: 'UNKNOWN_ERROR',
        message: 'An unknown error occurred while retrieving repository data.',
      });
      setRepoData(null);
    }

    setIsLoading(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRepositoryData(inputUrl);
  };

  const handleSampleClick = (url: string) => {
    setInputUrl(url);
    fetchRepositoryData(url);
  };

  const handleClear = () => {
    setInputUrl('');
    setError(null);
    setRepoData(null);
  };

  const createdDate = repoData ? formatDate(repoData.created_at) : null;
  const updatedDate = repoData ? formatDate(repoData.last_updated_at) : null;

  return (
    <div className="app-container">
      {/* Header Section */}
      <header className="app-header">
        <div className="phase-tag">
          <span className="phase-dot"></span>
          Phase 1 — Repository Data Collection
        </div>
        <h1 className="app-title">AI-Assisted Developer Decision Support</h1>
        <p className="app-subtitle">
          Repository Intelligence Platform · An open-source research framework for multi-dimensional health assessment.
        </p>
        <div className="research-attribution">
          <span>Foundation:</span>
          <strong>Revealing the Value of Repository Centrality in Lifespan Prediction (2024)</strong>
        </div>
      </header>

      {/* URL Input Form Card */}
      <section className="search-card">
        <div className="input-label-row">
          <label htmlFor="repo-url-input" className="input-label">
            <span>GitHub Repository URL or Shorthand</span>
          </label>
          <span className="input-hint">Format: https://github.com/owner/repo or owner/repo</span>
        </div>

        <form onSubmit={handleSubmit} className="search-form">
          <div className="input-wrapper">
            <span className="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </span>
            <input
              id="repo-url-input"
              type="text"
              className="repo-input"
              placeholder="e.g. https://github.com/fastapi/fastapi"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              disabled={isLoading}
              autoComplete="off"
              spellCheck="false"
            />
            {inputUrl && !isLoading && (
              <button
                type="button"
                id="clear-btn"
                className="clear-btn"
                onClick={handleClear}
                title="Clear input"
                aria-label="Clear input"
              >
                ✕
              </button>
            )}
          </div>

          <button
            id="analyze-btn"
            type="submit"
            className="submit-btn"
            disabled={isLoading || !inputUrl.trim()}
          >
            {isLoading ? (
              <>
                <svg className="spin-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <span>Collecting Data...</span>
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Analyze Repository</span>
              </>
            )}
          </button>
        </form>

        {/* Quick Sample Presets */}
        <div className="sample-presets">
          <span className="presets-label">Quick Test Repositories:</span>
          {SAMPLE_REPOSITORIES.map((sample) => (
            <button
              key={sample.label}
              id={`sample-${sample.label.split('/')[1]}`}
              type="button"
              className="sample-chip"
              onClick={() => handleSampleClick(sample.url)}
              disabled={isLoading}
            >
              {sample.label}
            </button>
          ))}
        </div>
      </section>

      {/* Error Feedback Banner */}
      {error && (
        <section id="error-banner" className="error-banner" role="alert">
          <span className="error-icon">⚠️</span>
          <div className="error-content">
            <span className="error-title">Data Collection Error ({error.code})</span>
            <span className="error-message">{error.message}</span>
            {error.details && <span className="error-details">{error.details}</span>}
          </div>
        </section>
      )}

      {/* Loading Skeleton State */}
      {isLoading && (
        <section className="loading-container" aria-live="polite">
          <div className="skeleton-card">
            <div className="skeleton-header">
              <div className="skeleton-shimmer skeleton-avatar"></div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div className="skeleton-shimmer skeleton-title"></div>
                <div className="skeleton-shimmer" style={{ width: '150px', height: '16px' }}></div>
              </div>
            </div>
            <div className="skeleton-shimmer skeleton-text"></div>
            <div className="skeleton-shimmer skeleton-text" style={{ width: '70%' }}></div>
            <div className="skeleton-grid">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton-shimmer skeleton-stat"></div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Repository Information Display */}
      {repoData && !isLoading && (
        <section id="repo-card" className="repo-card">
          {/* Card Header & Identity */}
          <div className="repo-header">
            <div className="repo-identity">
              {repoData.owner_avatar_url ? (
                <img
                  src={repoData.owner_avatar_url}
                  alt={`${repoData.owner} avatar`}
                  className="repo-avatar"
                />
              ) : (
                <div className="repo-avatar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  📦
                </div>
              )}
              <div className="repo-naming">
                <h2 id="repo-title" className="repo-full-name">
                  <a href={repoData.html_url} target="_blank" rel="noopener noreferrer">
                    {repoData.full_name}
                  </a>
                  <span className="external-link-icon" title="Open in GitHub">↗</span>
                </h2>
                <div className="repo-badges">
                  {repoData.is_archived ? (
                    <span id="stat-archived" className="badge badge-archived">Archived</span>
                  ) : (
                    <span id="stat-archived" className="badge badge-active">Active</span>
                  )}
                  <span id="stat-branch" className="badge badge-branch" title="Default Branch">
                    branch: {repoData.default_branch}
                  </span>
                  {repoData.license_name && (
                    <span className="badge badge-license" title="Software License">
                      {repoData.license_name}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Repository Description */}
          <div className="repo-description">
            {repoData.description ? (
              <p>{repoData.description}</p>
            ) : (
              <p className="no-description">No description provided for this repository.</p>
            )}
          </div>

          {/* Topics Chips */}
          {repoData.topics && repoData.topics.length > 0 && (
            <div className="topics-row">
              {repoData.topics.map((topic) => (
                <span key={topic} className="topic-chip">
                  #{topic}
                </span>
              ))}
            </div>
          )}

          {/* Phase 1 Stat Grid */}
          <div className="stats-grid">
            {/* Stars */}
            <div id="stat-stars" className="stat-box">
              <span className="stat-label">
                <span>⭐</span> Stars
              </span>
              <span className="stat-value">{formatNumber(repoData.stars)}</span>
              <span className="stat-sub">{repoData.stars.toLocaleString()} total stargazers</span>
            </div>

            {/* Forks */}
            <div id="stat-forks" className="stat-box">
              <span className="stat-label">
                <span>🍴</span> Forks
              </span>
              <span className="stat-value">{formatNumber(repoData.forks)}</span>
              <span className="stat-sub">{repoData.forks.toLocaleString()} forks</span>
            </div>

            {/* Open Issues & PRs */}
            <div id="stat-issues" className="stat-box">
              <span className="stat-label">
                <span>📋</span> Open Issues
              </span>
              <span className="stat-value">{formatNumber(repoData.open_issues_count)}</span>
              <span className="stat-sub">includes active PRs</span>
            </div>

            {/* Primary Language */}
            <div id="stat-language" className="stat-box">
              <span className="stat-label">
                <span>💻</span> Primary Language
              </span>
              <div className="lang-badge">
                <span
                  className="lang-dot"
                  style={{
                    backgroundColor: repoData.language
                      ? LANGUAGE_COLORS[repoData.language] || '#38bdf8'
                      : '#64748b',
                  }}
                ></span>
                <span className="stat-value" style={{ fontSize: '1.25rem' }}>
                  {repoData.language || 'Not Detected'}
                </span>
              </div>
              <span className="stat-sub">detected by GitHub Linguist</span>
            </div>

            {/* Created Date */}
            <div id="stat-created" className="stat-box">
              <span className="stat-label">
                <span>📅</span> Created Date
              </span>
              <span className="stat-value" style={{ fontSize: '1.15rem' }}>
                {createdDate?.formatted}
              </span>
              <span className="stat-sub">{createdDate?.relative}</span>
            </div>

            {/* Last Updated Date */}
            <div id="stat-updated" className="stat-box">
              <span className="stat-label">
                <span>⏱️</span> Last Updated
              </span>
              <span className="stat-value" style={{ fontSize: '1.15rem' }}>
                {updatedDate?.formatted}
              </span>
              <span className="stat-sub">{updatedDate?.relative}</span>
            </div>
          </div>

          {/* Research Roadmap Note */}
          <div className="research-banner">
            <div className="research-banner-header">
              <span>🔬 Research Context Notice</span>
            </div>
            <p className="research-banner-text">
              <strong>Phase 1 Scope:</strong> This live GitHub REST API data collection pipeline captures foundational metadata for repository identity. In subsequent phases, this data will feed into the <strong>Five-Dimension Health Framework</strong>, <strong>HITS Repository Centrality Graph Analysis</strong>, and <strong>Lifespan Evaluation</strong>. Current live API data is not claimed to reproduce the historical offline dataset of the 2024 base paper.
            </p>
          </div>

          {/* Raw JSON Schema Viewer for Verification */}
          <div className="json-accordion">
            <button
              id="raw-json-toggle"
              type="button"
              className="json-toggle-btn"
              onClick={() => setShowRawJson(!showRawJson)}
            >
              <span>{showRawJson ? '▼ Hide' : '▶ Show'} Raw API Response Schema</span>
            </button>
            {showRawJson && (
              <pre id="raw-json-viewer" className="json-code-box">
                {JSON.stringify(repoData, null, 2)}
              </pre>
            )}
          </div>

          {/* Footer Metadata & Rate Limit Status */}
          <div className="footer-meta">
            <span>Data fetched at: {repoData.fetched_at}</span>
            {rateLimit && (
              <span className="rate-limit-pill">
                GitHub API Remaining: {rateLimit.remaining ?? 'N/A'} requests
                {rateLimit.reset && ` (resets ${rateLimit.reset} UTC)`}
              </span>
            )}
          </div>
        </section>
      )}
    </div>
  );
};

export default App;
