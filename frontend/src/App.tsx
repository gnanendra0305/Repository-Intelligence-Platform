import React, { useState, useEffect } from 'react';

// =============================================================================
// Interfaces & Type Definitions
// =============================================================================

// M0.2 Repository Metadata Schema
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

// M0.1 Metric Registry Schema
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

// M0.2 Mining Diagnostics & Summary
interface CategoryStats {
  records_count: number;
  pages_fetched: number;
  has_more: boolean;
  status: string;
  error_message?: string | null;
}

interface MiningMetadata {
  repository_full_name: string;
  collection_timestamp: string;
  status: string;
  is_complete: boolean;
  categories: Record<string, CategoryStats>;
  total_records_collected: number;
  pages_fetched_total: number;
  rate_limit?: {
    remaining: number | null;
    limit: number | null;
    reset_time_utc: string | null;
  };
  errors: string[];
  warnings: string[];
}

// M0.3 Indicators & Health Index
interface MetricValue {
  metric_id: string;
  name: string;
  raw_value: number | null;
  formatted_value: string;
  unit: string | null;
  direction: string;
  normalized_score: number | null;
  weight: number;
  chaoss_family: string;
  linaker_area: string;
  status: string;
  notes?: string | null;
}

interface DimensionScore {
  name: string;
  score: number | null;
  metrics_available: number;
  metrics_total: number;
  metrics: MetricValue[];
}

interface HealthIndexResult {
  repository_name: string;
  rhi_score: number | null;
  rhi_grade: string;
  coverage_ratio: number;
  coverage_threshold: number;
  coverage_sufficient: boolean;
  metrics: Record<string, MetricValue>;
  context_variables: Record<string, MetricValue>;
  data_quality_indicators: Record<string, MetricValue>;
  dimensions: Record<string, DimensionScore>;
  missing_metrics: string[];
  calculation_timestamp: string;
}

// M0.4 Survival Analysis
interface SingleRepoSurvival {
  repository_name: string;
  observed_lifespan_days: number;
  observed_lifespan_years: number;
  censoring_status: string;
  is_censored: boolean;
  is_archived: boolean;
  eligible_for_standalone_km: boolean;
  methodological_caveats: string[];
}

interface KaplanMeierPoint {
  time_days: number;
  survival_probability: number;
  at_risk_count: number;
  event_count: number;
  censored_count: number;
  std_error: number;
  ci_lower: number;
  ci_upper: number;
}

interface CoxCovariate {
  name: string;
  coef: number;
  hazard_ratio: number;
  std_err: number;
  z_score: number;
  p_value: number;
  ci_lower: number;
  ci_upper: number;
}

interface SurvivalBenchmarkReport {
  dataset_type: string;
  sample_size: number;
  event_count: number;
  censored_count: number;
  censoring_rate: number;
  kaplan_meier: {
    median_survival_days: number | null;
    points: KaplanMeierPoint[];
  };
  cox_regression?: {
    is_fitted: boolean;
    concordance_index: number | null;
    covariates: CoxCovariate[];
  } | null;
  data_limitations: string[];
}

// M0.5 AI Report
interface ReportStrength {
  dimension: string;
  finding: string;
  evidence_metric: string;
  interpretation: string;
}

interface ReportRisk {
  dimension: string;
  severity: string;
  finding: string;
  evidence_metric: string;
  mitigation_advice: string;
}

interface AdoptionRecommendation {
  verdict: string;
  summary: string;
  key_drivers: string[];
  target_audience_notes: string;
}

interface RepositoryHealthReport {
  repository_name: string;
  generated_at: string;
  provider: string;
  executive_summary: string;
  health_index_summary: {
    rhi_score: number | null;
    rhi_grade: string;
    coverage_ratio: number;
    coverage_sufficient: boolean;
  };
  strengths: ReportStrength[];
  risks_and_bottlenecks: ReportRisk[];
  survival_sustainability_assessment: string;
  adoption_recommendation: AdoptionRecommendation;
  methodological_limitations: string[];
}

interface ApiError {
  code: string;
  message: string;
  details?: string;
}

// Presets
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

function formatNumber(num: number): string {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'k';
  return num.toLocaleString();
}

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

// Unified API fetch helper attempting relative proxy first then direct port 8000
async function apiFetch(endpoint: string, options?: RequestInit): Promise<any> {
  const directEndpoint = `http://127.0.0.1:8000${endpoint}`;
  try {
    const res = await fetch(endpoint, options);
    if (res.ok) return await res.json();
    const resDirect = await fetch(directEndpoint, options);
    return await resDirect.json();
  } catch {
    const resDirect = await fetch(directEndpoint, options);
    return await resDirect.json();
  }
}

// =============================================================================
// Main Component
// =============================================================================

export const App: React.FC = () => {
  // Navigation Tabs
  const [activeTab, setActiveTab] = useState<'analyzer' | 'registry'>('analyzer');
  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'indicators' | 'survival' | 'report' | 'mining'>('overview');

  // Input & Status
  const [inputUrl, setInputUrl] = useState<string>('');
  const [miningMode, setMiningMode] = useState<'rest' | 'graphql'>('rest');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [analysisStep, setAnalysisStep] = useState<string>('');
  const [error, setError] = useState<ApiError | null>(null);

  // M0.2 State
  const [repoData, setRepoData] = useState<RepositoryInfo | null>(null);
  const [miningMetadata, setMiningMetadata] = useState<MiningMetadata | null>(null);
  const [rateLimit, setRateLimit] = useState<{ remaining: number | null; reset: string | null } | null>(null);

  // M0.3 State
  const [indicators, setIndicators] = useState<HealthIndexResult | null>(null);

  // M0.4 State
  const [singleSurvival, setSingleSurvival] = useState<SingleRepoSurvival | null>(null);
  const [benchmarkReport, setBenchmarkReport] = useState<SurvivalBenchmarkReport | null>(null);
  const [survivalLoading, setSurvivalLoading] = useState<boolean>(false);

  // M0.5 State
  const [aiReport, setAiReport] = useState<RepositoryHealthReport | null>(null);

  // Raw Schema Drawer
  const [showRawJson, setShowRawJson] = useState<boolean>(false);

  // M0.1 Metric Registry State
  const [metrics, setMetrics] = useState<MetricDefinition[]>([]);
  const [metricsLoading, setMetricsLoading] = useState<boolean>(false);
  const [metricsError, setMetricsError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [chaossFilter, setChaossFilter] = useState<string>('all');
  const [linakerFilter, setLinakerFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Load Metric Registry (M0.1) on initial mount
  const fetchMetrics = async () => {
    setMetricsLoading(true);
    setMetricsError(null);
    try {
      const data = await apiFetch('/api/metrics');
      if (data && data.success && Array.isArray(data.data)) {
        setMetrics(data.data);
      } else {
        setMetricsError('Could not load Metric Registry. Ensure FastAPI server is running on port 8000.');
      }
    } catch (err: any) {
      setMetricsError(`Connection error: ${err?.message || String(err)}`);
    } finally {
      setMetricsLoading(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      try {
        const data = await apiFetch('/api/metrics');
        if (!ignore && data && data.success && Array.isArray(data.data)) {
          setMetrics(data.data);
        }
      } catch {
        // Fallback
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, []);

  // Full Analysis Pipeline: M0.2 -> M0.3 -> M0.4 -> M0.5
  const runFullPipeline = async (targetUrl: string) => {
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
    setRepoData(null);
    setMiningMetadata(null);
    setIndicators(null);
    setSingleSurvival(null);
    setAiReport(null);

    try {
      // Step 1: M0.2 Mining (REST or GraphQL)
      setAnalysisStep('Mining GitHub repository data (M0.2)...');
      let minedDataContainer: any = null;
      let repoInfoObj: RepositoryInfo | null = null;

      if (miningMode === 'graphql') {
        const gqlRes = await apiFetch('/api/repository/mine/graphql', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: cleanUrl, max_prs: 50, max_issues: 50, max_commits: 50 }),
        });
        if (!gqlRes || !gqlRes.success) {
          const detailErr = gqlRes?.metadata?.errors?.[0] || gqlRes?.message || 'GraphQL mining failed.';
          throw new Error(detailErr);
        }
        minedDataContainer = gqlRes.data;
        repoInfoObj = gqlRes.data?.repository;
        setRepoData(repoInfoObj);
      } else {
        // Default: REST Mining
        const mineRes = await apiFetch('/api/repository/mine', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: cleanUrl, max_pages_per_category: 3, per_page: 100 }),
        });

        if (mineRes && mineRes.success && mineRes.data) {
          minedDataContainer = mineRes.data;
          repoInfoObj = mineRes.data.repository;
          setRepoData(repoInfoObj);
          setMiningMetadata(mineRes.metadata);
          if (mineRes.metadata?.rate_limit) {
            setRateLimit({
              remaining: mineRes.metadata.rate_limit.remaining,
              reset: mineRes.metadata.rate_limit.reset_time_utc,
            });
          }
        } else {
          // Fallback to Phase 1 analyze endpoint
          const p1Res = await apiFetch('/api/repository/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: cleanUrl }),
          });
          if (p1Res && p1Res.success) {
            repoInfoObj = p1Res.data;
            setRepoData(repoInfoObj);
            minedDataContainer = { repository: repoInfoObj, pull_requests: [], issues: [], commits: [], contributors: [] };
          } else {
            throw new Error(mineRes?.message || p1Res?.message || 'Failed to retrieve repository data.');
          }
        }
      }

      if (!repoInfoObj) {
        throw new Error('Repository metadata could not be resolved.');
      }

      // Step 2: M0.3 Indicator Calculation
      setAnalysisStep('Computing Composite Indicators & RHI (M0.3)...');
      let computedIndicators: HealthIndexResult | null = null;
      try {
        const indRes = await apiFetch('/api/indicators/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: cleanUrl, mining_data: minedDataContainer }),
        });
        if (indRes && indRes.success && indRes.data) {
          computedIndicators = indRes.data;
          setIndicators(computedIndicators);
        }
      } catch (indErr) {
        console.warn('Indicator calculation error:', indErr);
      }

      // Step 3: M0.4 Survival Assessment
      setAnalysisStep('Evaluating Repository Lifespan & Right-Censoring (M0.4)...');
      let survivalObj: SingleRepoSurvival | null = null;
      try {
        const survRes = await apiFetch(`/api/survival/repository?url=${encodeURIComponent(cleanUrl)}`);
        if (survRes && survRes.repository_name) {
          survivalObj = survRes;
          setSingleSurvival(survivalObj);
        }
      } catch (survErr) {
        console.warn('Survival assessment error:', survErr);
      }

      // Step 4: M0.5 AI-Assisted Report Generation
      setAnalysisStep('Synthesizing Evidence-Grounded Health Report (M0.5)...');
      try {
        const reportPayload: any = { url: cleanUrl };
        if (computedIndicators) reportPayload.indicators = computedIndicators;
        if (survivalObj) reportPayload.survival = survivalObj;

        const repRes = await apiFetch('/api/report/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reportPayload),
        });
        if (repRes && repRes.success && repRes.data) {
          setAiReport(repRes.data);
        }
      } catch (repErr) {
        console.warn('Report generation error:', repErr);
      }

      // Automatically focus on Overview after successful analysis
      setActiveSubTab('overview');
    } catch (err: any) {
      setError({
        code: 'PIPELINE_ERROR',
        message: err?.message || 'An error occurred during repository analysis.',
        details: miningMode === 'graphql'
          ? 'GitHub GraphQL strictly requires authentication. Please configure GITHUB_TOKEN in backend/.env, or switch the mode dropdown above to REST API Mining (M0.2).'
          : 'Verify repository existence and that FastAPI backend is running on port 8000.',
      });
    } finally {
      setIsLoading(false);
      setAnalysisStep('');
    }
  };

  // Lazy-load Survival Benchmark Report (M0.4)
  const fetchBenchmarkReport = async () => {
    if (benchmarkReport || survivalLoading) return;
    setSurvivalLoading(true);
    try {
      const data = await apiFetch('/api/survival/benchmark');
      if (data && data.dataset_type) {
        setBenchmarkReport(data);
      }
    } catch (err) {
      console.warn('Failed to load survival benchmark:', err);
    } finally {
      setSurvivalLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runFullPipeline(inputUrl);
  };

  const handleSampleClick = (url: string) => {
    setInputUrl(url);
    runFullPipeline(url);
  };

  const handleClear = () => {
    setInputUrl('');
    setError(null);
    setRepoData(null);
    setMiningMetadata(null);
    setIndicators(null);
    setSingleSurvival(null);
    setAiReport(null);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setChaossFilter('all');
    setLinakerFilter('all');
    setTypeFilter('all');
  };

  const createdDate = repoData ? formatDate(repoData.created_at) : null;
  const updatedDate = repoData ? formatDate(repoData.last_updated_at) : null;

  // Filter metrics based on M0.1 controls
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
          Repository Intelligence Platform · Full Decision Pipeline (M0.1 – M0.5)
        </div>
        <h1 className="app-title">AI-Assisted Developer Decision Support</h1>
        <p className="app-subtitle">
          Multi-dimensional OSS health assessment, composite scoring, longitudinal survival analysis, and grounded recommendations.
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
          TAB 1: REPOSITORY ANALYZER (FULL M0.2 - M0.5 PIPELINE)
          ================================================================== */}
      {activeTab === 'analyzer' && (
        <>
          {/* URL Input Form Card */}
          <section className="search-card">
            <div className="input-label-row">
              <label htmlFor="repo-url-input" className="input-label">
                <span>GitHub Repository URL or Shorthand</span>
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className="input-hint">Mode:</span>
                <select
                  className="filter-select"
                  style={{ padding: '0.2rem 0.5rem', fontSize: '0.78rem' }}
                  value={miningMode}
                  onChange={(e) => setMiningMode(e.target.value as 'rest' | 'graphql')}
                >
                  <option value="rest">REST API Mining (M0.2)</option>
                  <option value="graphql">GraphQL API Mining (M0.2)</option>
                </select>
              </div>
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
                    <span>{analysisStep || 'Analyzing...'}</span>
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
                <span className="error-title">Pipeline Error ({error.code})</span>
                <span className="error-message">{error.message}</span>
                {error.details && <span className="error-details">{error.details}</span>}
              </div>
            </section>
          )}

          {/* Loading Pipeline State */}
          {isLoading && (
            <section className="loading-container" aria-live="polite">
              <div className="skeleton-card">
                <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--accent-cyan)' }}>
                  <svg className="spin-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  <p style={{ marginTop: '0.75rem', fontWeight: 600, fontSize: '1rem' }}>{analysisStep}</p>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
                    Fetching metadata, mining event streams, computing composite indicators, and synthesizing AI report.
                  </p>
                </div>
              </div>
            </section>
          )}

          {/* Main Results View */}
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
                      {indicators && (
                        <span
                          className={`badge ${indicators.coverage_sufficient ? 'badge-active' : 'badge-archived'}`}
                          title="Repository Health Index Grade"
                        >
                          RHI Grade: {indicators.rhi_grade} ({indicators.rhi_score !== null ? `${indicators.rhi_score.toFixed(1)}/100` : 'N/A'})
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

              {/* Sub-Navigation for Pipeline Modules */}
              <div className="sub-nav-tabs">
                <button
                  type="button"
                  className={`sub-tab-btn ${activeSubTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveSubTab('overview')}
                >
                  📊 Surface Stats
                </button>
                <button
                  type="button"
                  className={`sub-tab-btn ${activeSubTab === 'indicators' ? 'active' : ''}`}
                  onClick={() => setActiveSubTab('indicators')}
                >
                  📈 M0.3 Health Index (RHI)
                </button>
                <button
                  type="button"
                  className={`sub-tab-btn ${activeSubTab === 'survival' ? 'active' : ''}`}
                  onClick={() => {
                    setActiveSubTab('survival');
                    fetchBenchmarkReport();
                  }}
                >
                  ⏱️ M0.4 Survival Analysis
                </button>
                <button
                  type="button"
                  className={`sub-tab-btn ${activeSubTab === 'report' ? 'active' : ''}`}
                  onClick={() => setActiveSubTab('report')}
                >
                  🤖 M0.5 AI Decision Report
                </button>
                <button
                  type="button"
                  className={`sub-tab-btn ${activeSubTab === 'mining' ? 'active' : ''}`}
                  onClick={() => setActiveSubTab('mining')}
                >
                  📦 M0.2 Mining Diagnostics
                </button>
              </div>

              {/* SUB-VIEW 1: OVERVIEW SURFACE STATS */}
              {activeSubTab === 'overview' && (
                <div className="stats-grid" style={{ marginTop: '1.25rem' }}>
                  {/* Stars */}
                  <div id="stat-stars" className="stat-box">
                    <span className="stat-label">⭐ Stars</span>
                    <span className="stat-value">{formatNumber(repoData.stars)}</span>
                    <span className="stat-sub">{repoData.stars.toLocaleString()} total stargazers</span>
                  </div>

                  {/* Forks */}
                  <div id="stat-forks" className="stat-box">
                    <span className="stat-label">🍴 Forks</span>
                    <span className="stat-value">{formatNumber(repoData.forks)}</span>
                    <span className="stat-sub">{repoData.forks.toLocaleString()} forks</span>
                  </div>

                  {/* Open Issues & PRs */}
                  <div id="stat-issues" className="stat-box">
                    <span className="stat-label">📋 Open Issues</span>
                    <span className="stat-value">{formatNumber(repoData.open_issues_count)}</span>
                    <span className="stat-sub">includes active PRs</span>
                  </div>

                  {/* Primary Language */}
                  <div id="stat-language" className="stat-box">
                    <span className="stat-label">💻 Primary Language</span>
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
                    <span className="stat-label">📅 Created Date</span>
                    <span className="stat-value" style={{ fontSize: '1.15rem' }}>
                      {createdDate?.formatted}
                    </span>
                    <span className="stat-sub">{createdDate?.relative}</span>
                  </div>

                  {/* Last Updated Date */}
                  <div id="stat-updated" className="stat-box">
                    <span className="stat-label">⏱️ Last Updated</span>
                    <span className="stat-value" style={{ fontSize: '1.15rem' }}>
                      {updatedDate?.formatted}
                    </span>
                    <span className="stat-sub">{updatedDate?.relative}</span>
                  </div>
                </div>
              )}

              {/* SUB-VIEW 2: M0.3 COMPOSITE INDICATORS & RHI */}
              {activeSubTab === 'indicators' && (
                <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {indicators ? (
                    <>
                      {/* Health Score Summary Banner */}
                      <div className="metric-card-item" style={{ borderColor: 'var(--border-medium)', background: 'rgba(15, 23, 42, 0.9)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <span className="formula-heading">Repository Health Index (RHI)</span>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem', marginTop: '0.4rem' }}>
                              <span style={{ fontSize: '2.5rem', fontWeight: 800, color: indicators.rhi_score !== null ? 'var(--accent-cyan)' : 'var(--accent-amber)' }}>
                                {indicators.rhi_score !== null ? indicators.rhi_score.toFixed(1) : 'N/A'}
                              </span>
                              <span style={{ fontSize: '1.25rem', color: 'var(--text-muted)' }}>/ 100</span>
                              <span className="status-tag status-implemented" style={{ fontSize: '0.85rem' }}>
                                Grade: {indicators.rhi_grade}
                              </span>
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <span className="meta-detail-label">Metric Coverage</span>
                            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: indicators.coverage_sufficient ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                              {(indicators.coverage_ratio * 100).toFixed(1)}%
                            </div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                              Min threshold: {(indicators.coverage_threshold * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>

                        {!indicators.coverage_sufficient && (
                          <div className="validation-callout" style={{ marginTop: '1rem' }}>
                            <strong>⚠️ Insufficient Data Coverage:</strong> Only {(indicators.coverage_ratio * 100).toFixed(1)}% of required indicators could be extracted. To prevent misleading scores, overall RHI is suppressed until $\ge 40\%$ coverage is achieved.
                          </div>
                        )}
                      </div>

                      {/* Dimensions Breakdown */}
                      <div>
                        <h3 style={{ fontSize: '1.1rem', marginBottom: '0.75rem', color: 'var(--text-main)' }}>Linåker Health Areas (25% Weight Each)</h3>
                        <div className="stats-grid">
                          {Object.entries(indicators.dimensions).map(([key, dim]) => (
                            <div key={key} className="stat-box">
                              <span className="stat-label">{dim.name}</span>
                              <span className="stat-value" style={{ color: dim.score !== null ? 'var(--accent-cyan)' : 'var(--text-dim)' }}>
                                {dim.score !== null ? `${dim.score.toFixed(1)}/100` : 'No Data'}
                              </span>
                              <span className="stat-sub">{dim.metrics_available} of {dim.metrics_total} metrics calculated</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Detailed Metric Scores Table */}
                      <div>
                        <h3 style={{ fontSize: '1.1rem', marginBottom: '0.75rem', color: 'var(--text-main)' }}>Registered Metric Calculations</h3>
                        <div style={{ overflowX: 'auto' }}>
                          <table className="analysis-table">
                            <thead>
                              <tr>
                                <th>ID</th>
                                <th>Metric Name</th>
                                <th>Raw Value</th>
                                <th>Normalized Score</th>
                                <th>Direction</th>
                                <th>Linåker Area</th>
                              </tr>
                            </thead>
                            <tbody>
                              {Object.entries(indicators.metrics).map(([mid, m]) => (
                                <tr key={mid}>
                                  <td><span className="metric-id-pill">{m.metric_id}</span></td>
                                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                                  <td>{m.formatted_value}</td>
                                  <td>
                                    {m.normalized_score !== null ? (
                                      <span style={{ fontWeight: 700, color: m.normalized_score >= 0.7 ? 'var(--accent-emerald)' : m.normalized_score >= 0.4 ? 'var(--accent-amber)' : 'var(--accent-rose)' }}>
                                        {(m.normalized_score * 100).toFixed(1)}%
                                      </span>
                                    ) : 'N/A'}
                                  </td>
                                  <td style={{ textTransform: 'capitalize', fontSize: '0.78rem' }}>{m.direction.replace(/_/g, ' ')}</td>
                                  <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{m.linaker_area}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="empty-registry-state">
                      <p>Indicator calculations not yet available. Click Analyze Repository to compute.</p>
                    </div>
                  )}
                </div>
              )}

              {/* SUB-VIEW 3: M0.4 SURVIVAL ANALYSIS */}
              {activeSubTab === 'survival' && (
                <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {singleSurvival && (
                    <div className="metric-card-item">
                      <div className="metric-top-bar">
                        <div>
                          <span className="formula-heading">Single Repository Lifespan Diagnostic</span>
                          <h3 className="metric-heading" style={{ marginTop: '0.25rem' }}>{singleSurvival.repository_name}</h3>
                        </div>
                        <span className={`status-tag ${singleSurvival.is_censored ? 'status-implemented' : 'status-provisional'}`}>
                          Status: {singleSurvival.censoring_status}
                        </span>
                      </div>
                      <div className="stats-grid" style={{ marginTop: '1rem' }}>
                        <div className="stat-box">
                          <span className="stat-label">Observed Lifespan</span>
                          <span className="stat-value">{singleSurvival.observed_lifespan_years} yrs</span>
                          <span className="stat-sub">{singleSurvival.observed_lifespan_days} total days</span>
                        </div>
                        <div className="stat-box">
                          <span className="stat-label">Right-Censored?</span>
                          <span className="stat-value" style={{ color: singleSurvival.is_censored ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                            {singleSurvival.is_censored ? 'Yes (Active)' : 'No (Archived)'}
                          </span>
                          <span className="stat-sub">Terminal event not yet observed</span>
                        </div>
                      </div>
                      <div className="validation-callout" style={{ marginTop: '1rem' }}>
                        <strong>Methodological Limitation:</strong> A single snapshot observation cannot establish a longitudinal Kaplan-Meier survival curve. Below is our calibrated reference benchmark cohort.
                      </div>
                    </div>
                  )}

                  {/* Benchmark Cohort Section */}
                  <div className="metric-card-item">
                    <div className="metric-top-bar">
                      <div>
                        <span className="formula-heading">Reference Benchmark Cohort</span>
                        <h3 className="metric-heading" style={{ marginTop: '0.25rem' }}>
                          Synthetic Benchmark Survival Analysis (N=150)
                        </h3>
                      </div>
                      <span className="status-tag status-planned">Calibrated Synthetic Baseline</span>
                    </div>

                    {survivalLoading && (
                      <p style={{ padding: '1rem', color: 'var(--text-muted)' }}>Loading survival benchmark...</p>
                    )}

                    {benchmarkReport && (
                      <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div className="stats-grid">
                          <div className="stat-box">
                            <span className="stat-label">Cohort Size</span>
                            <span className="stat-value">{benchmarkReport.sample_size} repos</span>
                            <span className="stat-sub">{benchmarkReport.event_count} events, {benchmarkReport.censored_count} censored</span>
                          </div>
                          <div className="stat-box">
                            <span className="stat-label">Median Survival</span>
                            <span className="stat-value">
                              {benchmarkReport.kaplan_meier.median_survival_days ? `${(benchmarkReport.kaplan_meier.median_survival_days / 365).toFixed(1)} yrs` : '> 10 yrs'}
                            </span>
                            <span className="stat-sub">{benchmarkReport.kaplan_meier.median_survival_days} days</span>
                          </div>
                          <div className="stat-box">
                            <span className="stat-label">Censoring Rate</span>
                            <span className="stat-value">{(benchmarkReport.censoring_rate * 100).toFixed(1)}%</span>
                            <span className="stat-sub">Proportion right-censored</span>
                          </div>
                        </div>

                        {/* Cox Regression Covariates Table */}
                        {benchmarkReport.cox_regression && (
                          <div style={{ marginTop: '0.5rem' }}>
                            <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>
                              Cox Proportional Hazards Model (Harrell's C-index: {benchmarkReport.cox_regression.concordance_index})
                            </h4>
                            <div style={{ overflowX: 'auto' }}>
                              <table className="analysis-table">
                                <thead>
                                  <tr>
                                    <th>Covariate</th>
                                    <th>Coef (β)</th>
                                    <th>Hazard Ratio exp(β)</th>
                                    <th>z-Score</th>
                                    <th>p-Value</th>
                                    <th>Risk Impact</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {benchmarkReport.cox_regression.covariates.map((cov) => (
                                    <tr key={cov.name}>
                                      <td style={{ fontWeight: 600 }}>{cov.name}</td>
                                      <td>{cov.coef.toFixed(3)}</td>
                                      <td style={{ fontWeight: 700, color: cov.hazard_ratio < 1.0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                                        {cov.hazard_ratio.toFixed(3)}
                                      </td>
                                      <td>{cov.z_score.toFixed(2)}</td>
                                      <td>{cov.p_value < 0.001 ? '< 0.001' : cov.p_value.toFixed(3)}</td>
                                      <td style={{ fontSize: '0.78rem' }}>
                                        {cov.hazard_ratio < 1.0 ? '🛡️ Protective (Lowers Hazard)' : '⚠️ Risk Factor (Increases Hazard)'}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* SUB-VIEW 4: M0.5 AI DECISION REPORT */}
              {activeSubTab === 'report' && (
                <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {aiReport ? (
                    <>
                      {/* Adoption Verdict Card */}
                      <div className="metric-card-item" style={{ background: 'rgba(15, 23, 42, 0.95)', borderColor: 'var(--border-medium)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <span className="formula-heading">Adoption Decision Recommendation</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
                              <span
                                className={`badge ${
                                  aiReport.adoption_recommendation.verdict === 'RECOMMENDED'
                                    ? 'badge-active'
                                    : aiReport.adoption_recommendation.verdict === 'RECOMMENDED_WITH_CAUTION'
                                    ? 'status-provisional'
                                    : 'badge-archived'
                                }`}
                                style={{ fontSize: '1rem', padding: '0.35rem 0.85rem' }}
                              >
                                {aiReport.adoption_recommendation.verdict.replace(/_/g, ' ')}
                              </span>
                              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                                Provider: {aiReport.provider}
                              </span>
                            </div>
                          </div>
                        </div>

                        <p style={{ marginTop: '1rem', fontSize: '1rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
                          {aiReport.adoption_recommendation.summary}
                        </p>

                        <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                          <strong>Target Notes:</strong> {aiReport.adoption_recommendation.target_audience_notes}
                        </div>
                      </div>

                      {/* Executive Summary */}
                      <div className="metric-card-item">
                        <span className="formula-heading">Executive Summary</span>
                        <p style={{ marginTop: '0.5rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
                          {aiReport.executive_summary}
                        </p>
                      </div>

                      {/* Strengths & Risks Columns */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                        {/* Strengths */}
                        <div className="metric-card-item">
                          <h4 style={{ color: 'var(--accent-emerald)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>✓</span> Verified Strengths
                          </h4>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.75rem' }}>
                            {aiReport.strengths.map((str, idx) => (
                              <div key={idx} style={{ padding: '0.75rem', background: 'rgba(52, 211, 153, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--accent-emerald)' }}>
                                <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{str.finding}</div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', marginTop: '0.2rem' }}>Proof: {str.evidence_metric}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{str.interpretation}</div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Risks & Bottlenecks */}
                        <div className="metric-card-item">
                          <h4 style={{ color: 'var(--accent-rose)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>⚠️</span> Bottlenecks & Risk Warnings
                          </h4>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.75rem' }}>
                            {aiReport.risks_and_bottlenecks.map((risk, idx) => (
                              <div key={idx} style={{ padding: '0.75rem', background: 'rgba(248, 113, 113, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--accent-rose)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{risk.finding}</span>
                                  <span className={`status-tag status-${risk.severity === 'high' ? 'experimental' : 'provisional'}`} style={{ fontSize: '0.7rem' }}>
                                    {risk.severity} risk
                                  </span>
                                </div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--accent-amber)', marginTop: '0.2rem' }}>Evidence: {risk.evidence_metric}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Advice: {risk.mitigation_advice}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Longitudinal Sustainability */}
                      <div className="metric-card-item">
                        <span className="formula-heading">Longitudinal Survival & Sustainability</span>
                        <p style={{ marginTop: '0.5rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
                          {aiReport.survival_sustainability_assessment}
                        </p>
                      </div>

                      {/* Methodological Limitations */}
                      <div className="metric-card-item">
                        <span className="formula-heading">Methodological Limitations</span>
                        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                          {aiReport.methodological_limitations.map((lim, idx) => (
                            <li key={idx}>{lim}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  ) : (
                    <div className="empty-registry-state">
                      <p>AI Report generation in progress or waiting for analysis.</p>
                    </div>
                  )}
                </div>
              )}

              {/* SUB-VIEW 5: M0.2 MINING DIAGNOSTICS */}
              {activeSubTab === 'mining' && (
                <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  <div className="metric-card-item">
                    <span className="formula-heading">M0.2 Collection Engine Diagnostics</span>
                    <h3 className="metric-heading" style={{ marginTop: '0.25rem' }}>
                      Status: {miningMetadata?.status || 'Active Collection'} ({miningMetadata?.is_complete ? 'Complete' : 'Partial / Capped'})
                    </h3>

                    {miningMetadata && (
                      <div className="stats-grid" style={{ marginTop: '1rem' }}>
                        <div className="stat-box">
                          <span className="stat-label">Total Records</span>
                          <span className="stat-value">{miningMetadata.total_records_collected}</span>
                          <span className="stat-sub">{miningMetadata.pages_fetched_total} total pages fetched</span>
                        </div>
                        {Object.entries(miningMetadata.categories).map(([cat, stats]) => (
                          <div key={cat} className="stat-box">
                            <span className="stat-label" style={{ textTransform: 'capitalize' }}>{cat.replace(/_/g, ' ')}</span>
                            <span className="stat-value">{stats.records_count}</span>
                            <span className="stat-sub">{stats.pages_fetched} pages ({stats.status})</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Raw JSON Schema Drawer */}
              <div className="json-accordion" style={{ marginTop: '1.5rem' }}>
                <button
                  id="raw-json-toggle"
                  type="button"
                  className="json-toggle-btn"
                  onClick={() => setShowRawJson(!showRawJson)}
                >
                  <span>{showRawJson ? '▼ Hide' : '▶ Show'} Complete Backend Schemas (M0.1–M0.5)</span>
                </button>
                {showRawJson && (
                  <pre id="raw-json-viewer" className="json-code-box">
                    {JSON.stringify(
                      {
                        m02_metadata: repoData,
                        m03_indicators: indicators,
                        m04_survival: singleSurvival,
                        m05_report: aiReport,
                      },
                      null,
                      2
                    )}
                  </pre>
                )}
              </div>

              {/* Footer Metadata */}
              <div className="footer-meta">
                <span>Data fetched at: {repoData.fetched_at}</span>
                {rateLimit && (
                  <span className="rate-limit-pill">
                    API Remaining: {rateLimit.remaining ?? 'N/A'} requests
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

                    <p className="metric-desc">{m.description}</p>
                    <div className="metric-op-def">
                      <strong>Operational Definition:</strong> {m.operational_definition}
                    </div>

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

                    <div className="research-ref-text">
                      <strong>Literature Reference:</strong> {m.research_reference}
                    </div>

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
