import React, { useState, useEffect } from 'react';

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

interface MetricDefinition {
  metric_id: string;
  metric_name: string;
  description: string;
  chaoss_family: string;
  linaker_area: string;
  metric_type: string;
  operational_definition: string;
  formula: string | null;
  required_data: string[];
  data_source: string;
  required_api_endpoints: string[];
  required_payload_fields: string[];
  unit: string | null;
  direction: string;
  provenance_class: string;
  research_reference: string;
  implementation_status: string;
  validation_notes: string | null;
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
  const [activeTab, setActiveTab] = useState<'analyzer' | 'registry'>('analyzer');

  // Analyzer States
  const [inputUrl, setInputUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [repoData, setRepoData] = useState<RepositoryInfo | null>(null);
  const [rateLimit, setRateLimit] = useState<{ remaining: number | null; reset: string | null } | null>(null);
  const [showRawJson, setShowRawJson] = useState<boolean>(false);

  // Metric Registry States
  const [metrics, setMetrics] = useState<MetricDefinition[]>([]);
  const [metricsLoading, setMetricsLoading] = useState<boolean>(false);
  const [metricsError, setMetricsError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [chaossFilter, setChaossFilter] = useState<string>('all');
  const [linakerFilter, setLinakerFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Fetch Metric Registry from backend
  const fetchMetrics = async () => {
    setMetricsLoading(true);
    setMetricsError(null);

    const endpoints = [
      '/api/metrics',
      'http://127.0.0.1:8000/api/metrics',
    ];

    let success = false;
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          const json = await response.json();
          if (json.success && Array.isArray(json.data)) {
            setMetrics(json.data);
            success = true;
            break;
          }
        }
      } catch {
        // Fallback to next endpoint
      }
    }

    if (!success) {
      setMetricsError('Unable to load Metric Registry from backend. Ensure FastAPI server is running on port 8000.');
    }
    setMetricsLoading(false);
  };

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      const endpoints = ['/api/metrics', 'http://127.0.0.1:8000/api/metrics'];
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint);
          if (response.ok) {
            const json = await response.json();
            if (!ignore && json.success && Array.isArray(json.data)) {
              setMetrics(json.data);
              return;
            }
          }
        } catch {
          // Fallback
        }
      }
      if (!ignore) {
        setMetricsError('Unable to load Metric Registry from backend. Ensure FastAPI server is running on port 8000.');
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, []);

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

  const handleResetFilters = () => {
    setSearchQuery('');
    setChaossFilter('all');
    setLinakerFilter('all');
    setTypeFilter('all');
  };

  const createdDate = repoData ? formatDate(repoData.created_at) : null;
  const updatedDate = repoData ? formatDate(repoData.last_updated_at) : null;

  // Filter metrics based on controls
  const filteredMetrics = metrics.filter((m) => {
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch =
      query === '' ||
      m.metric_id.toLowerCase().includes(query) ||
      m.metric_name.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      m.research_reference.toLowerCase().includes(query);

    const matchesChaoss =
      chaossFilter === 'all' || m.chaoss_family.toLowerCase() === chaossFilter.toLowerCase();

    const matchesLinaker =
      linakerFilter === 'all' || m.linaker_area.toLowerCase() === linakerFilter.toLowerCase();

    const matchesType =
      typeFilter === 'all' || m.metric_type.toLowerCase() === typeFilter.toLowerCase();

    return matchesSearch && matchesChaoss && matchesLinaker && matchesType;
  });

  return (
    <div className="app-container">
      {/* Header Section */}
      <header className="app-header">
        <div className="phase-tag">
          <span className="phase-dot"></span>
          Repository Intelligence Platform · Decision Support
        </div>
        <h1 className="app-title">AI-Assisted Developer Decision Support</h1>
        <p className="app-subtitle">
          An open-source research framework for multi-dimensional OSS health assessment, risk analysis, and technology selection.
        </p>
        <div className="research-attribution">
          <span>Registered Base Paper:</span>
          <strong>Linåker et al. (2026), Empirical Software Engineering</strong>
        </div>

        {/* Primary Navigation Tabs */}
        <nav className="nav-tabs-container">
          <div className="nav-tabs" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'analyzer'}
              className={`tab-btn ${activeTab === 'analyzer' ? 'active' : ''}`}
              onClick={() => setActiveTab('analyzer')}
            >
              <span>🔍 Repository Analyzer</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'registry'}
              className={`tab-btn ${activeTab === 'registry' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('registry');
                if (metrics.length === 0) fetchMetrics();
              }}
            >
              <span>📊 CHAOSS Metric Registry (M0.1)</span>
              <span className="tab-badge">{metrics.length > 0 ? metrics.length : '14'}</span>
            </button>
          </div>
        </nav>
      </header>

      {/* ==================================================================
          TAB 1: REPOSITORY ANALYZER (PHASE 1)
          ================================================================== */}
      {activeTab === 'analyzer' && (
        <>
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

              {/* Research Link Notice */}
              <div
                className="research-banner"
                style={{ cursor: 'pointer' }}
                onClick={() => setActiveTab('registry')}
                title="Click to view full CHAOSS Metric Registry"
              >
                <div className="research-banner-header">
                  <span>🔬 M0.1 CHAOSS Metric Registry Active</span>
                  <span style={{ color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 600 }}>
                    Explore All {metrics.length > 0 ? metrics.length : 14} Health Metrics →
                  </span>
                </div>
                <p className="research-banner-text">
                  This repository is evaluated against our dual research taxonomy: <strong>CHAOSS Working Group Families</strong> (Evolution, Risk, Value, Common Metrics) and <strong>Linåker et al. (2026) 5 Health Areas</strong>. Click to inspect operational definitions, mathematical formulas, and data requirements.
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
        </>
      )}

      {/* ==================================================================
          TAB 2: CHAOSS METRIC REGISTRY (M0.1)
          ================================================================== */}
      {activeTab === 'registry' && (
        <section className="registry-container">
          {/* Controls & Filter Toolbar */}
          <div className="registry-toolbar">
            <div className="registry-header-row">
              <div className="registry-title-block">
                <h2>
                  <span>📊</span> Canonical Metric Registry
                </h2>
                <p>
                  M0.1: OSS Health & Sustainability Concepts · Primary: CHAOSS Metric Families · Secondary: Linåker et al. (2026) 5 Areas
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="rate-limit-pill" style={{ color: 'var(--accent-cyan)' }}>
                  Showing {filteredMetrics.length} of {metrics.length} metrics
                </span>
                {(searchQuery || chaossFilter !== 'all' || linakerFilter !== 'all' || typeFilter !== 'all') && (
                  <button
                    type="button"
                    onClick={handleResetFilters}
                    className="clear-btn"
                    style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem', border: '1px solid var(--border-subtle)', borderRadius: '6px' }}
                  >
                    Reset Filters
                  </button>
                )}
              </div>
            </div>

            {/* Filters Row */}
            <div className="registry-filters-grid">
              {/* Search Box */}
              <div className="filter-item">
                <label className="filter-label">Search Metrics</label>
                <input
                  type="text"
                  className="registry-search-input"
                  placeholder="Filter by ID, name, or citation..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* CHAOSS Family Filter */}
              <div className="filter-item">
                <label className="filter-label">CHAOSS Metric Family</label>
                <select
                  className="filter-select"
                  value={chaossFilter}
                  onChange={(e) => setChaossFilter(e.target.value)}
                >
                  <option value="all">All CHAOSS Families</option>
                  <option value="Evolution">Evolution</option>
                  <option value="Risk">Risk</option>
                  <option value="Value">Value</option>
                  <option value="Common Metrics">Common Metrics</option>
                  <option value="Diversity, Equity & Inclusion (DEI)">Diversity, Equity & Inclusion (DEI)</option>
                </select>
              </div>

              {/* Linåker Area Filter */}
              <div className="filter-item">
                <label className="filter-label">Linåker Health Area</label>
                <select
                  className="filter-select"
                  value={linakerFilter}
                  onChange={(e) => setLinakerFilter(e.target.value)}
                >
                  <option value="all">All Linåker Areas</option>
                  <option value="Community Productivity">Community Productivity</option>
                  <option value="Community Stability">Community Stability</option>
                  <option value="Orchestration">Orchestration</option>
                  <option value="Production Process">Production Process</option>
                  <option value="Production Output">Production Output</option>
                </select>
              </div>

              {/* Metric Type Filter */}
              <div className="filter-item">
                <label className="filter-label">Metric Type</label>
                <select
                  className="filter-select"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="all">All Metric Types</option>
                  <option value="health">Health Indicator</option>
                  <option value="context">Context Covariate</option>
                  <option value="data_quality">Data Quality Diagnostic</option>
                  <option value="derived">Derived Assessment</option>
                </select>
              </div>
            </div>
          </div>

          {/* Loading State */}
          {metricsLoading && (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <svg className="spin-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <p style={{ marginTop: '0.5rem' }}>Loading Metric Registry from backend...</p>
            </div>
          )}

          {/* Error State */}
          {metricsError && (
            <div className="error-banner" style={{ marginTop: '1.5rem' }}>
              <span className="error-icon">⚠️</span>
              <div className="error-content">
                <span className="error-title">Registry Connection Error</span>
                <span className="error-message">{metricsError}</span>
              </div>
            </div>
          )}

          {/* Metrics Grid */}
          {!metricsLoading && (
            <div className="metrics-grid" style={{ marginTop: '1.5rem' }}>
              {filteredMetrics.length === 0 ? (
                <div className="empty-registry-state">
                  <p style={{ fontSize: '1.1rem', fontWeight: 600 }}>No metrics matched your filter criteria.</p>
                  <p style={{ fontSize: '0.85rem', marginTop: '0.4rem' }}>Try clearing the search query or adjusting the taxonomy dropdowns.</p>
                  <button
                    type="button"
                    className="submit-btn"
                    style={{ marginTop: '1rem', padding: '0.4rem 1.2rem', display: 'inline-flex' }}
                    onClick={handleResetFilters}
                  >
                    Reset All Filters
                  </button>
                </div>
              ) : (
                filteredMetrics.map((m) => (
                  <article key={m.metric_id} className="metric-card-item">
                    {/* Top Identity Row */}
                    <div className="metric-top-bar">
                      <div className="metric-id-title">
                        <span className="metric-id-pill">{m.metric_id}</span>
                        <h3 className="metric-heading">{m.metric_name}</h3>
                      </div>
                      <div className="metric-badges-row">
                        <span className={`status-tag status-${m.implementation_status}`}>
                          {m.implementation_status}
                        </span>
                      </div>
                    </div>

                    {/* Dual Taxonomy & Classification Pills */}
                    <div className="taxonomy-pills">
                      <span className="tax-pill chaoss" title="Primary Classification">
                        CHAOSS: <strong>{m.chaoss_family}</strong>
                      </span>
                      <span className="tax-pill linaker" title="Secondary Research Mapping">
                        Linåker: <strong>{m.linaker_area}</strong>
                      </span>
                      <span className="tax-pill" title="Metric Functional Role">
                        Type: <strong>{m.metric_type}</strong>
                      </span>
                      <span className="tax-pill provenance" title="Literature Provenance">
                        Provenance: <strong>{m.provenance_class}</strong>
                      </span>
                      {m.direction && m.direction !== 'not_applicable' && (
                        <span className="tax-pill" title="Health Direction">
                          Direction: <strong>{m.direction.replace(/_/g, ' ')}</strong>
                        </span>
                      )}
                      {m.unit && (
                        <span className="tax-pill" title="Measurement Unit">
                          Unit: <strong>{m.unit}</strong>
                        </span>
                      )}
                    </div>

                    {/* Description & Operational Definition */}
                    <p className="metric-desc">{m.description}</p>
                    <div className="metric-op-def">
                      <strong>Operational Definition:</strong> {m.operational_definition}
                    </div>

                    {/* Mathematical Formula Card */}
                    <div className="formula-card">
                      <span className="formula-heading">Mathematical Formulation</span>
                      {m.formula ? (
                        <code className="formula-math">{m.formula}</code>
                      ) : (
                        <span className="formula-under-revision">
                          Formula under revision (S2 STA-4 telescoping-sum issue; superseded by A8R relative slope)
                        </span>
                      )}
                    </div>

                    {/* Data Source & Ingestion Payload Dependencies */}
                    <div className="metric-meta-details">
                      <div className="meta-detail-col">
                        <span className="meta-detail-label">API Endpoints Required</span>
                        <span className="meta-detail-val" style={{ color: 'var(--accent-blue)' }}>
                          {m.required_api_endpoints.join(', ') || 'N/A'}
                        </span>
                      </div>
                      <div className="meta-detail-col">
                        <span className="meta-detail-label">Required Payload Fields</span>
                        <div className="fields-chip-list">
                          {m.required_payload_fields.map((field) => (
                            <span key={field} className="field-chip">
                              {field}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Research Citation Reference */}
                    <div className="research-ref-text">
                      <strong>Literature Reference:</strong> {m.research_reference}
                    </div>

                    {/* Validation / Caveat Callout Notice */}
                    {m.validation_notes && (
                      <div className="validation-callout">
                        <strong>Methodological Caveat:</strong> {m.validation_notes}
                      </div>
                    )}
                  </article>
                ))
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default App;
