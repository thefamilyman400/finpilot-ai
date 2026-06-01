import { useAuthStore } from '../../store/authStore';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountService } from '../../services/account.service';
import { transactionService } from '../../services/transaction.service';
import { recommendationService } from '../../services/recommendation.service';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import MainLayout from '../../components/layout/MainLayout';

export default function Dashboard() {
  const { user } = useAuthStore();

  // Fetch accounts for stats (only active ones)
  const { data: accounts, isLoading: accountsLoading, error: accountsError } = useQuery({
    queryKey: ['accounts', { is_active: true }],
    queryFn: () => accountService.getAccounts({ is_active: true }),
  });

  // Fetch transactions for analytics
  const { data: transactionsData, isLoading: transactionsLoading, error: transactionsError } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionService.getTransactions({}),
  });

  const { data: recommendationSummary } = useQuery({
    queryKey: ['recommendations-summary'],
    queryFn: recommendationService.getSummary,
  });

  const isLoading = accountsLoading || transactionsLoading;
  const hasError = accountsError || transactionsError;

  // Calculate assets (checking, savings, investment)
  const totalAssets = accounts?.filter(acc => ['checking', 'savings', 'investment'].includes(acc.account_type))
    .reduce((sum, acc) => sum + acc.balance, 0) || 0;
  
  // Calculate liabilities (loans use outstanding balance, credit cards use balance)
  const totalLiabilities = (accounts?.filter(acc => acc.account_type === 'loan')
    .reduce((sum, acc) => sum + (acc.loan_outstanding || 0), 0) || 0) +
    (accounts?.filter(acc => acc.account_type === 'credit_card')
    .reduce((sum, acc) => sum + acc.balance, 0) || 0);
  
  const netWorth = totalAssets - totalLiabilities;
  const transactionCount = transactionsData?.total || 0;

  // Calculate spending by category
  const spendingByCategory = transactionsData?.transactions
    ?.filter(t => t.transaction_type === 'debit')
    .reduce((acc, t) => {
      const category = t.category || 'uncategorized';
      acc[category] = (acc[category] || 0) + Math.abs(t.amount);
      return acc;
    }, {} as Record<string, number>) || {};

  const categoryData = Object.entries(spendingByCategory)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6);

  // Calculate account balances for visualization
  const accountBalanceData = accounts?.map(acc => ({
    name: acc.account_name || acc.institution_name,
    balance: acc.balance,
    type: acc.account_type
  })) || [];

  const COLORS = ['#3b82f6', '#22c55e', '#ef4444', '#a855f7', '#f59e0b', '#06b6d4'];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <MainLayout>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
          Welcome back, {user?.full_name}!
        </h2>
        <p style={{ color: 'rgb(107 114 128)' }}>
          Here's your financial overview
        </p>
      </div>

      {/* Error State */}
      {hasError && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '2rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontWeight: '500', marginBottom: '0.5rem' }}>
              ⚠️ Error loading dashboard data
            </p>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>
              {(accountsError as any)?.message || (transactionsError as any)?.message || 'Please try refreshing the page'}
            </p>
          </div>
        )}

      {/* Loading Skeletons */}
      {isLoading ? (
        <>
          {/* Stats Skeleton */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="card" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}>
                  <div style={{ height: '1rem', backgroundColor: 'rgb(229 231 235)', borderRadius: '0.25rem', marginBottom: '0.5rem', width: '60%' }}></div>
                  <div style={{ height: '2rem', backgroundColor: 'rgb(229 231 235)', borderRadius: '0.25rem', marginBottom: '0.5rem' }}></div>
                  <div style={{ height: '0.75rem', backgroundColor: 'rgb(229 231 235)', borderRadius: '0.25rem', width: '80%' }}></div>
                </div>
              ))}
            </div>
            {/* Charts Skeleton */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              {[1, 2].map((i) => (
                <div key={i} className="card">
                  <div style={{ height: '1.5rem', backgroundColor: 'rgb(229 231 235)', borderRadius: '0.25rem', marginBottom: '1rem', width: '40%' }}></div>
                  <div style={{ height: '300px', backgroundColor: 'rgb(243 244 246)', borderRadius: '0.5rem' }}></div>
                </div>
              ))}
            </div>
        </>
      ) : (
        <>
          {/* Quick Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <Link to="/accounts" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                Total Assets
              </h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(34 197 94)' }}>
                {formatCurrency(totalAssets)}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem' }}>
                Checking, Savings & Investments
              </p>
            </div>
          </Link>
          
          <Link to="/accounts" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                Total Liabilities
              </h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(239 68 68)' }}>
                {formatCurrency(totalLiabilities)}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem' }}>
                Loans & Credit Cards
              </p>
            </div>
          </Link>
          
          <Link to="/accounts" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                Net Worth
              </h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)' }}>
                {formatCurrency(netWorth)}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem' }}>
                Assets - Liabilities
              </p>
            </div>
          </Link>
          
          <Link to="/transactions" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                Transactions
              </h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)' }}>
                {transactionCount}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem' }}>
                Total recorded
              </p>
            </div>
          </Link>

          <Link to="/recommendations" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
                Recommendations
              </h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(37 99 235)' }}>
                {recommendationSummary?.pending_count || 0}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem' }}>
                Pending actions
              </p>
            </div>
          </Link>
          
          {/* AI Copilot card removed per request */}
        </div>

        {/* Charts Section */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {/* Spending by Category */}
          {categoryData.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '1rem' }}>
                Spending by Category
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(Number(value ?? 0))} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Account Balances */}
          {accountBalanceData.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '1rem' }}>
                Account Balances
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={accountBalanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(Number(value ?? 0))} />
                  <Bar dataKey="balance" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          </div>
        </>
      )}
    </MainLayout>
  );
}

// Made with Bob
