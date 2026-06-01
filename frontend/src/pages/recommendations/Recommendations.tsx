import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  CheckCircle2,
  Lightbulb,
  RefreshCw,
  Sparkles,
  ThumbsDown,
  Trash2,
} from 'lucide-react';
import MainLayout from '../../components/layout/MainLayout';
import { recommendationService } from '../../services/recommendation.service';
import type { Recommendation } from '../../types';

const recommendationTypes = [
  { value: '', label: 'All focus areas' },
  { value: 'savings', label: 'Savings' },
  { value: 'investment', label: 'Investment' },
  { value: 'debt_reduction', label: 'Debt reduction' },
  { value: 'budget_optimization', label: 'Budget optimization' },
  { value: 'spending_reduction', label: 'Spending reduction' },
  { value: 'emergency_fund', label: 'Emergency fund' },
  { value: 'retirement_planning', label: 'Retirement planning' },
  { value: 'insurance', label: 'Insurance' },
];

const statusOptions = [
  { value: '', label: 'All statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'completed', label: 'Completed' },
  { value: 'rejected', label: 'Rejected' },
];

const priorityColors: Record<string, { bg: string; text: string }> = {
  low: { bg: 'rgb(240 253 244)', text: 'rgb(22 101 52)' },
  medium: { bg: 'rgb(239 246 255)', text: 'rgb(29 78 216)' },
  high: { bg: 'rgb(255 247 237)', text: 'rgb(194 65 12)' },
  critical: { bg: 'rgb(254 242 242)', text: 'rgb(185 28 28)' },
};

const statusColors: Record<string, { bg: string; text: string }> = {
  pending: { bg: 'rgb(254 249 195)', text: 'rgb(133 77 14)' },
  accepted: { bg: 'rgb(219 234 254)', text: 'rgb(30 64 175)' },
  completed: { bg: 'rgb(220 252 231)', text: 'rgb(22 101 52)' },
  rejected: { bg: 'rgb(243 244 246)', text: 'rgb(75 85 99)' },
  expired: { bg: 'rgb(254 242 242)', text: 'rgb(153 27 27)' },
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

const formatLabel = (value: string) => {
  return value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getActionItemText = (item: Record<string, any>, index: number) => {
  if (typeof item === 'string') return item;
  return item.title || item.description || item.action || item.step || `Action item ${index + 1}`;
};

export default function Recommendations() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [generationFocus, setGenerationFocus] = useState('');
  const [generationCount, setGenerationCount] = useState(5);

  const recommendationParams = {
    status: statusFilter,
    type: typeFilter,
    limit: 100,
  };

  const {
    data: recommendations,
    isLoading: recommendationsLoading,
    error: recommendationsError,
  } = useQuery({
    queryKey: ['recommendations', recommendationParams],
    queryFn: () => recommendationService.getRecommendations(recommendationParams),
  });

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useQuery({
    queryKey: ['recommendations-summary'],
    queryFn: recommendationService.getSummary,
  });

  const invalidateRecommendationQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    queryClient.invalidateQueries({ queryKey: ['recommendations-summary'] });
  };

  const generateMutation = useMutation({
    mutationFn: () =>
      recommendationService.generateRecommendations({
        focus_areas: generationFocus ? [generationFocus] : undefined,
        max_recommendations: generationCount,
        include_context: false,
      }),
    onSuccess: invalidateRecommendationQueries,
  });

  const acceptMutation = useMutation({
    mutationFn: recommendationService.acceptRecommendation,
    onSuccess: invalidateRecommendationQueries,
  });

  const rejectMutation = useMutation({
    mutationFn: recommendationService.rejectRecommendation,
    onSuccess: invalidateRecommendationQueries,
  });

  const completeMutation = useMutation({
    mutationFn: recommendationService.completeRecommendation,
    onSuccess: invalidateRecommendationQueries,
  });

  const deleteMutation = useMutation({
    mutationFn: recommendationService.deleteRecommendation,
    onSuccess: invalidateRecommendationQueries,
  });

  const isLoading = recommendationsLoading || summaryLoading;
  const hasError = recommendationsError || summaryError;

  const renderBadge = (label: string, colors: { bg: string; text: string }) => (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.25rem 0.625rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: colors.bg,
        color: colors.text,
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  );

  const renderRecommendation = (recommendation: Recommendation) => {
    const priorityColor = priorityColors[recommendation.priority] || priorityColors.medium;
    const statusColor = statusColors[recommendation.status] || statusColors.pending;
    const actionItems = recommendation.action_items || [];
    const isActionPending =
      acceptMutation.isPending ||
      rejectMutation.isPending ||
      completeMutation.isPending ||
      deleteMutation.isPending;

    return (
      <article key={recommendation.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
              {renderBadge(formatLabel(recommendation.type), { bg: 'rgb(238 242 255)', text: 'rgb(67 56 202)' })}
              {renderBadge(formatLabel(recommendation.priority), priorityColor)}
              {renderBadge(formatLabel(recommendation.status), statusColor)}
            </div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
              {recommendation.title}
            </h3>
            <p style={{ color: 'rgb(55 65 81)', lineHeight: 1.6 }}>
              {recommendation.description}
            </p>
          </div>

          {recommendation.estimated_savings !== undefined && recommendation.estimated_savings !== null && (
            <div
              style={{
                minWidth: '150px',
                padding: '0.75rem',
                border: '1px solid rgb(187 247 208)',
                borderRadius: '0.5rem',
                backgroundColor: 'rgb(240 253 244)',
              }}
            >
              <p style={{ fontSize: '0.75rem', color: 'rgb(22 101 52)', fontWeight: 600, marginBottom: '0.25rem' }}>
                Estimated savings
              </p>
              <p style={{ fontSize: '1.25rem', color: 'rgb(21 128 61)', fontWeight: 800 }}>
                {formatCurrency(recommendation.estimated_savings)}
              </p>
            </div>
          )}
        </div>

        {(recommendation.rationale || recommendation.estimated_time_to_implement || recommendation.confidence_score) && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '1rem',
              padding: '1rem',
              backgroundColor: 'rgb(249 250 251)',
              borderRadius: '0.5rem',
            }}
          >
            {recommendation.rationale && (
              <div>
                <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', fontWeight: 600, marginBottom: '0.25rem' }}>
                  Why this matters
                </p>
                <p style={{ color: 'rgb(55 65 81)', fontSize: '0.875rem', lineHeight: 1.5 }}>
                  {recommendation.rationale}
                </p>
              </div>
            )}
            {recommendation.estimated_time_to_implement && (
              <div>
                <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', fontWeight: 600, marginBottom: '0.25rem' }}>
                  Time to implement
                </p>
                <p style={{ color: 'rgb(17 24 39)', fontWeight: 600 }}>
                  {recommendation.estimated_time_to_implement}
                </p>
              </div>
            )}
            {recommendation.confidence_score !== undefined && recommendation.confidence_score !== null && (
              <div>
                <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', fontWeight: 600, marginBottom: '0.25rem' }}>
                  Confidence
                </p>
                <p style={{ color: 'rgb(17 24 39)', fontWeight: 600 }}>
                  {Math.round(recommendation.confidence_score * 100)}%
                </p>
              </div>
            )}
          </div>
        )}

        {actionItems.length > 0 && (
          <div>
            <p style={{ fontSize: '0.875rem', fontWeight: 700, color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
              Action items
            </p>
            <ol style={{ margin: 0, paddingLeft: '1.25rem', color: 'rgb(55 65 81)' }}>
              {actionItems.slice(0, 4).map((item, index) => (
                <li key={`${recommendation.id}-${index}`} style={{ marginBottom: '0.375rem', lineHeight: 1.5 }}>
                  {getActionItemText(item, index)}
                </li>
              ))}
            </ol>
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', paddingTop: '0.75rem', borderTop: '1px solid rgb(229 231 235)' }}>
          {recommendation.status === 'pending' && (
            <>
              <button
                type="button"
                className="btn-primary"
                disabled={isActionPending}
                onClick={() => acceptMutation.mutate(recommendation.id)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <CheckCircle2 size={16} />
                Accept
              </button>
              <button
                type="button"
                className="btn-secondary"
                disabled={isActionPending}
                onClick={() => rejectMutation.mutate(recommendation.id)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <ThumbsDown size={16} />
                Reject
              </button>
            </>
          )}
          {recommendation.status === 'accepted' && (
            <button
              type="button"
              className="btn-primary"
              disabled={isActionPending}
              onClick={() => completeMutation.mutate(recommendation.id)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <CheckCircle2 size={16} />
              Mark complete
            </button>
          )}
          <button
            type="button"
            className="btn-secondary"
            disabled={isActionPending}
            onClick={() => deleteMutation.mutate(recommendation.id)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginLeft: 'auto' }}
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </article>
    );
  };

  return (
    <MainLayout>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
            Recommendations
          </h2>
          <p style={{ color: 'rgb(107 114 128)' }}>
            Review AI-generated financial actions and track what you decide to do.
          </p>
        </div>
      </div>

      {hasError && (
        <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '2rem' }}>
          <p style={{ color: 'rgb(153 27 27)', fontWeight: 600 }}>
            Failed to load recommendations. Please try refreshing the page.
          </p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card">
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Pending</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'rgb(17 24 39)' }}>{summary?.pending_count ?? 0}</p>
        </div>
        <div className="card">
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Accepted</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'rgb(37 99 235)' }}>{summary?.accepted_count ?? 0}</p>
        </div>
        <div className="card">
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Completed</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'rgb(22 163 74)' }}>{summary?.completed_count ?? 0}</p>
        </div>
        <div className="card">
          <p style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Estimated savings</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'rgb(21 128 61)' }}>
            {formatCurrency(summary?.total_estimated_savings ?? 0)}
          </p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', alignItems: 'end' }}>
          <div>
            <label className="form-label">Status</label>
            <select className="form-input" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Type</label>
            <select className="form-input" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
              {recommendationTypes.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Generation focus</label>
            <select className="form-input" value={generationFocus} onChange={(event) => setGenerationFocus(event.target.value)}>
              {recommendationTypes.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">How many</label>
            <input
              type="number"
              min={1}
              max={20}
              className="form-input"
              value={generationCount}
              onChange={(event) => setGenerationCount(Number(event.target.value))}
            />
          </div>
          <button
            type="button"
            className="btn-primary"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', height: '2.5rem' }}
          >
            {generateMutation.isPending ? <RefreshCw size={16} /> : <Sparkles size={16} />}
            {generateMutation.isPending ? 'Generating...' : 'Generate'}
          </button>
        </div>
        {generateMutation.data && (
          <p style={{ color: 'rgb(22 101 52)', marginTop: '1rem', fontSize: '0.875rem', fontWeight: 600 }}>
            {generateMutation.data.generation_summary}
          </p>
        )}
        {generateMutation.error && (
          <p style={{ color: 'rgb(185 28 28)', marginTop: '1rem', fontSize: '0.875rem', fontWeight: 600 }}>
            Could not generate recommendations right now.
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'rgb(107 114 128)' }}>
          Loading recommendations...
        </div>
      ) : recommendations && recommendations.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
          {recommendations.map(renderRecommendation)}
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <Lightbulb size={48} color="rgb(59 130 246)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>No recommendations yet</h3>
          <p style={{ color: 'rgb(107 114 128)', marginBottom: '1.5rem' }}>
            Generate recommendations after adding accounts and transactions.
          </p>
          <button
            type="button"
            className="btn-primary"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {generateMutation.isPending ? <RefreshCw size={16} /> : <Sparkles size={16} />}
            Generate recommendations
          </button>
        </div>
      )}
    </MainLayout>
  );
}

// Made with Bob
