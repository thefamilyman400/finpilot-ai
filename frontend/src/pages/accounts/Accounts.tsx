import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountService } from '../../services/account.service';
import type { Account, AccountCreate } from '../../types';
import MainLayout from '../../components/layout/MainLayout';

export default function Accounts() {
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const queryClient = useQueryClient();

  // Fetch accounts (only active ones)
  const { data: accounts, isLoading, error } = useQuery({
    queryKey: ['accounts', { is_active: true }],
    queryFn: () => accountService.getAccounts({ is_active: true }),
  });

  // Delete account mutation
  const deleteMutation = useMutation({
    mutationFn: accountService.deleteAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const handleDelete = async (accountId: string) => {
    if (window.confirm('Are you sure you want to delete this account?')) {
      deleteMutation.mutate(accountId);
    }
  };

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const getAccountTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      checking: 'rgb(59 130 246)',
      savings: 'rgb(34 197 94)',
      credit: 'rgb(239 68 68)',
      investment: 'rgb(168 85 247)',
    };
    return colors[type.toLowerCase()] || 'rgb(107 114 128)';
  };

  if (isLoading) {
    return (
      <MainLayout>
        <p style={{ textAlign: 'center', color: 'rgb(107 114 128)' }}>Loading accounts...</p>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '1rem' }}>
          <p style={{ color: 'rgb(153 27 27)' }}>Error loading accounts. Please try again.</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)' }}>
          Accounts
        </h1>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
        >
          + Add Account
        </button>
      </div>

      {/* Content */}
      <div>
        {/* Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
              Total Assets
            </h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(34 197 94)' }}>
              {formatCurrency(accounts?.filter(acc => ['checking', 'savings', 'investment'].includes(acc.account_type)).reduce((sum, acc) => sum + acc.balance, 0) || 0)}
            </p>
          </div>
          
          <div className="card">
            <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
              Total Liabilities
            </h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(239 68 68)' }}>
              {formatCurrency(
                (accounts ? accounts.filter(acc => acc.account_type === 'loan').reduce((sum, acc) => sum + (acc.loan_outstanding || 0), 0) : 0) +
                (accounts ? accounts.filter(acc => acc.account_type === 'credit_card').reduce((sum, acc) => sum + acc.balance, 0) : 0),
                'INR'
              )}
            </p>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
              Net Worth
            </h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)' }}>
              {formatCurrency(
                (accounts ? accounts.filter(acc => ['checking', 'savings', 'investment'].includes(acc.account_type)).reduce((sum, acc) => sum + acc.balance, 0) : 0) -
                ((accounts ? accounts.filter(acc => acc.account_type === 'loan').reduce((sum, acc) => sum + (acc.loan_outstanding || 0), 0) : 0) +
                (accounts ? accounts.filter(acc => acc.account_type === 'credit_card').reduce((sum, acc) => sum + acc.balance, 0) : 0)),
                'INR'
              )}
            </p>
          </div>
          
          <div className="card">
            <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>
              Total Accounts
            </h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)' }}>
              {accounts?.length || 0}
            </p>
          </div>
        </div>

        {/* Accounts List */}
        {accounts && accounts.length > 0 ? (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {accounts.map((account) => (
              <div 
                key={account.id} 
                className="card"
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <div
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      backgroundColor: getAccountTypeColor(account.account_type)
                    }}
                  />
                  <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)' }}>
                    {account.account_name || account.institution_name}
                  </h3>
                    <span 
                      style={{ 
                        fontSize: '0.75rem', 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '0.25rem', 
                        backgroundColor: 'rgb(243 244 246)', 
                        color: 'rgb(55 65 81)',
                        textTransform: 'capitalize'
                      }}
                    >
                      {account.account_type}
                    </span>
                  </div>
                  
                  {/* Display balance or loan details based on account type */}
                  {account.account_type === 'loan' ? (
                    <div>
                      <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(239 68 68)' }}>
                        Outstanding: {formatCurrency(account.loan_outstanding || 0, account.currency)}
                      </p>
                      {account.emi_amount && (
                        <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>
                          Monthly EMI: {formatCurrency(account.emi_amount, account.currency)}
                        </p>
                      )}
                      {account.loan_principal && (
                        <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                          Original Amount: {formatCurrency(account.loan_principal, account.currency)}
                        </p>
                      )}
                      {account.interest_rate && (
                        <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                          Interest Rate: {account.interest_rate}% per annum
                        </p>
                      )}
                      {account.remaining_tenure_months && (
                        <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                          Remaining: {account.remaining_tenure_months} months
                        </p>
                      )}
                    </div>
                  ) : (
                    <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: account.account_type === 'credit_card' ? 'rgb(239 68 68)' : 'rgb(17 24 39)' }}>
                      {formatCurrency(account.balance, account.currency)}
                    </p>
                  )}
                  
                  <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>
                    Last updated: {new Date(account.updated_at).toLocaleDateString()}
                  </p>
                </div>
                
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    onClick={() => setEditingAccount(account)}
                    className="btn-secondary"
                    style={{ padding: '0.5rem 1rem' }}
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => handleDelete(account.id)}
                    disabled={deleteMutation.isPending}
                    style={{ 
                      padding: '0.5rem 1rem',
                      backgroundColor: 'rgb(254 242 242)',
                      color: 'rgb(153 27 27)',
                      border: '1px solid rgb(252 165 165)',
                      borderRadius: '0.5rem',
                      fontWeight: '500',
                      cursor: deleteMutation.isPending ? 'not-allowed' : 'pointer',
                      opacity: deleteMutation.isPending ? 0.5 : 1
                    }}
                  >
                    {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'rgb(107 114 128)', marginBottom: '1rem' }}>
              No accounts yet. Add your first account to get started!
            </p>
            <button 
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              + Add Account
            </button>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingAccount) && (
        <AccountModal
          account={editingAccount}
          onClose={() => {
            setShowAddModal(false);
            setEditingAccount(null);
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['accounts'] });
            setShowAddModal(false);
            setEditingAccount(null);
          }}
        />
      )}
    </MainLayout>
  );
}

// Account Modal Component
function AccountModal({
  account,
  onClose,
  onSuccess
}: {
  account: Account | null;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [formData, setFormData] = useState<AccountCreate>({
    account_type: account?.account_type || 'checking',
    institution_name: account?.institution_name || '',
    account_name: account?.account_name || '',
    balance: account?.balance || 0,
    currency: 'INR', // Always INR
    loan_principal: account?.loan_principal,
    loan_outstanding: account?.loan_outstanding,
    interest_rate: account?.interest_rate,
    emi_amount: account?.emi_amount,
    loan_tenure_months: account?.loan_tenure_months,
    remaining_tenure_months: account?.remaining_tenure_months,
    loan_start_date: account?.loan_start_date,
    total_interest_paid: account?.total_interest_paid || 0,
    total_principal_paid: account?.total_principal_paid || 0,
  });
  const [error, setError] = useState('');

  // Auto-calculate EMI when loan details change
  const calculateEMI = (principal: number, annualRate: number, months: number): number => {
    if (!principal || !annualRate || !months) return 0;
    const monthlyRate = annualRate / 12 / 100;
    if (monthlyRate === 0) return principal / months;
    const emi = principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
    return Math.round(emi * 100) / 100;
  };

  // Auto-calculate remaining tenure based on start date
  const calculateRemainingTenure = (startDate: string, totalMonths: number): number => {
    if (!startDate || !totalMonths) return 0;
    const start = new Date(startDate);
    const now = new Date();
    const monthsElapsed = (now.getFullYear() - start.getFullYear()) * 12 + (now.getMonth() - start.getMonth());
    const remaining = totalMonths - monthsElapsed;
    return Math.max(0, remaining);
  };

  // Auto-calculate total interest paid
  const calculateInterestPaid = (
    principal: number,
    emi: number,
    startDate: string,
    totalMonths: number,
    outstanding: number
  ): number => {
    if (!principal || !emi || !startDate || !totalMonths) return 0;
    const monthsElapsed = totalMonths - calculateRemainingTenure(startDate, totalMonths);
    if (monthsElapsed <= 0) return 0;
    
    // Calculate total amount paid so far
    const totalPaid = emi * monthsElapsed;
    
    // Calculate principal paid
    const principalPaid = principal - outstanding;
    
    // Interest paid = Total paid - Principal paid
    const interestPaid = totalPaid - principalPaid;
    
    // Ensure non-negative
    return Math.max(0, Math.round(interestPaid * 100) / 100);
  };

  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: account
      ? (data: AccountCreate) => accountService.updateAccount(account.id, data)
      : accountService.createAccount,
    onSuccess: (data) => {
      console.log('Account saved successfully:', data);
      // Invalidate all account-related queries
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      // Force immediate refetch
      queryClient.refetchQueries({ queryKey: ['accounts'] });
      // Small delay to ensure backend has processed
      setTimeout(() => {
        onSuccess();
      }, 100);
    },
    onError: (err: any) => {
      // Handle Pydantic validation errors (422)
      if (err.response?.status === 422 && err.response?.data?.detail) {
        const detail = err.response.data.detail;
        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
          const errorMessages = detail.map((e: any) => {
            const field = e.loc?.join('.') || 'field';
            return `${field}: ${e.msg}`;
          }).join(', ');
          setError(`Validation error: ${errorMessages}`);
        } else if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError('Validation error. Please check all required fields.');
        }
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to save account');
      }
      console.error('Account save error:', err);
      console.error('Error response:', err.response?.data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Prepare data with auto-calculated values
    const dataToSubmit = { ...formData };
    
    // If EMI is auto-calculated, include it
    if (formData.loan_principal && formData.interest_rate && formData.loan_tenure_months) {
      dataToSubmit.emi_amount = calculateEMI(
        formData.loan_principal,
        formData.interest_rate,
        formData.loan_tenure_months
      );
    }
    
    // If remaining tenure is auto-calculated, include it
    if (formData.loan_start_date && formData.loan_tenure_months) {
      dataToSubmit.remaining_tenure_months = calculateRemainingTenure(
        formData.loan_start_date,
        formData.loan_tenure_months
      );
    }
    
    // Auto-calculate outstanding balance if conditions are met
    if (formData.account_type === 'loan' && formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months && formData.interest_rate) {
      const monthsElapsed = formData.loan_tenure_months - calculateRemainingTenure(formData.loan_start_date, formData.loan_tenure_months);
      if (monthsElapsed > 0) {
        const emi = dataToSubmit.emi_amount || calculateEMI(formData.loan_principal, formData.interest_rate, formData.loan_tenure_months);
        const monthlyRate = formData.interest_rate / 12 / 100;
        let outstanding = formData.loan_principal;
        
        for (let i = 0; i < monthsElapsed; i++) {
          const interest = outstanding * monthlyRate;
          const principal = emi - interest;
          outstanding -= principal;
        }
        
        dataToSubmit.loan_outstanding = Math.max(0, Math.round(outstanding * 100) / 100);
      } else {
        dataToSubmit.loan_outstanding = formData.loan_principal;
      }
    }
    
    // Calculate and include interest paid and principal paid for loans
    if (formData.account_type === 'loan' && formData.loan_principal && dataToSubmit.emi_amount && formData.loan_start_date && formData.loan_tenure_months && dataToSubmit.loan_outstanding !== undefined) {
      dataToSubmit.total_principal_paid = Math.max(0, formData.loan_principal - dataToSubmit.loan_outstanding);
      dataToSubmit.total_interest_paid = calculateInterestPaid(
        formData.loan_principal,
        dataToSubmit.emi_amount,
        formData.loan_start_date,
        formData.loan_tenure_months,
        dataToSubmit.loan_outstanding
      );
    }
    
    // Convert loan_start_date to ISO datetime format if present
    if (dataToSubmit.loan_start_date) {
      // If it's just a date string (YYYY-MM-DD), convert to ISO datetime
      if (typeof dataToSubmit.loan_start_date === 'string' && !dataToSubmit.loan_start_date.includes('T')) {
        dataToSubmit.loan_start_date = `${dataToSubmit.loan_start_date}T00:00:00`;
      }
    }
    
    // Clean up form data - remove undefined/null values for update
    const cleanedData: any = {};
    Object.entries(dataToSubmit).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        cleanedData[key] = value;
      }
    });
    
    console.log('Submitting account data:', cleanedData);
    mutation.mutate(cleanedData);
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50,
        padding: '1rem',
        overflowY: 'auto'
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: '28rem',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          margin: 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '1.5rem' }}>
          {account ? 'Edit Account' : 'Add New Account'}
        </h2>

        {error && (
          <div style={{ backgroundColor: 'rgb(254 242 242)', border: '1px solid rgb(252 165 165)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem' }}>
            <p style={{ color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label className="label" htmlFor="institution_name">
              Bank/Institution Name *
            </label>
            <input
              id="institution_name"
              type="text"
              className="input-field"
              value={formData.institution_name}
              onChange={(e) => setFormData({ ...formData, institution_name: e.target.value })}
              required
              placeholder="Chase Bank"
            />
          </div>

          <div>
            <label className="label" htmlFor="account_name">
              Account Nickname (Optional)
            </label>
            <input
              id="account_name"
              type="text"
              className="input-field"
              value={formData.account_name || ''}
              onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
              placeholder="My Checking Account"
            />
          </div>

          <div>
            <label className="label" htmlFor="account_type">
              Account Type
            </label>
            <select
              id="account_type"
              className="input-field"
              value={formData.account_type}
              onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
              required
            >
              <option value="checking">Current Account</option>
              <option value="savings">Savings</option>
              <option value="credit_card">Credit Card</option>
              <option value="investment">Investment</option>
              <option value="loan">Loan</option>
            </select>
          </div>

          {/* Balance field - label changes based on account type */}
          <div>
            <label className="label" htmlFor="balance">
              {formData.account_type === 'credit_card' ? 'Outstanding Balance (Amount Owed)' :
               formData.account_type === 'loan' ? 'Current Balance (Optional)' :
               'Current Balance'} *
            </label>
            <input
              id="balance"
              type="number"
              step="0.01"
              className="input-field"
              value={formData.balance || ''}
              onChange={(e) => setFormData({ ...formData, balance: e.target.value ? parseFloat(e.target.value) : undefined })}
              required={formData.account_type !== 'loan'}
              placeholder={formData.account_type === 'credit_card' ? 'Amount you owe' : 'Current balance'}
            />
            {formData.account_type === 'credit_card' && (
              <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>
                Enter the amount you currently owe on this credit card
              </p>
            )}
          </div>

          {/* Currency is now fixed to INR */}

          {/* Loan-specific fields */}
          {formData.account_type === 'loan' && (
            <>
              <div style={{ borderTop: '1px solid rgb(229 231 235)', paddingTop: '1rem', marginTop: '0.5rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '1rem' }}>
                  Loan Details
                </h3>
              </div>

              <div>
                <label className="label" htmlFor="loan_principal">
                  Original Loan Amount *
                </label>
                <input
                  id="loan_principal"
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={formData.loan_principal || ''}
                  onChange={(e) => setFormData({ ...formData, loan_principal: e.target.value ? parseFloat(e.target.value) : undefined })}
                  required
                  placeholder="50000"
                />
              </div>

              <div>
                <label className="label" htmlFor="loan_outstanding">
                  Outstanding Balance {formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months ? '(Auto-calculated)' : '*'}
                </label>
                <input
                  id="loan_outstanding"
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={
                    formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months
                      ? (() => {
                          const monthsElapsed = formData.loan_tenure_months - calculateRemainingTenure(formData.loan_start_date, formData.loan_tenure_months);
                          if (monthsElapsed <= 0) return formData.loan_principal;
                          
                          const emi = formData.emi_amount || (formData.interest_rate ? calculateEMI(formData.loan_principal, formData.interest_rate, formData.loan_tenure_months) : 0);
                          if (!emi) return formData.loan_principal;
                          
                          // Calculate outstanding using reducing balance method
                          const monthlyRate = (formData.interest_rate || 0) / 12 / 100;
                          let outstanding = formData.loan_principal;
                          
                          for (let i = 0; i < monthsElapsed; i++) {
                            const interest = outstanding * monthlyRate;
                            const principal = emi - interest;
                            outstanding -= principal;
                          }
                          
                          return Math.max(0, Math.round(outstanding * 100) / 100);
                        })()
                      : formData.loan_outstanding || ''
                  }
                  onChange={(e) => setFormData({ ...formData, loan_outstanding: e.target.value ? parseFloat(e.target.value) : undefined })}
                  required
                  placeholder="45000"
                  disabled={!!(formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months && formData.interest_rate)}
                  style={{
                    backgroundColor: formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months && formData.interest_rate ? 'rgb(243 244 246)' : undefined,
                    cursor: formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months && formData.interest_rate ? 'not-allowed' : undefined
                  }}
                />
                {formData.loan_principal && formData.loan_start_date && formData.loan_tenure_months && formData.interest_rate && (
                  <p style={{ fontSize: '0.75rem', color: 'rgb(34 197 94)', marginTop: '0.25rem' }}>
                    ✓ Outstanding balance automatically calculated using reducing balance method
                  </p>
                )}
              </div>

              <div>
                <label className="label" htmlFor="interest_rate">
                  Interest Rate (% per annum) *
                </label>
                <input
                  id="interest_rate"
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={formData.interest_rate || ''}
                  onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value ? parseFloat(e.target.value) : undefined })}
                  required
                  placeholder="8.5"
                />
              </div>

              <div>
                <label className="label" htmlFor="emi_amount">
                  Monthly EMI Amount {formData.loan_principal && formData.interest_rate && formData.loan_tenure_months ? '(Auto-calculated)' : '*'}
                </label>
                <input
                  id="emi_amount"
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={
                    formData.loan_principal && formData.interest_rate && formData.loan_tenure_months
                      ? calculateEMI(formData.loan_principal, formData.interest_rate, formData.loan_tenure_months)
                      : formData.emi_amount || ''
                  }
                  onChange={(e) => setFormData({ ...formData, emi_amount: e.target.value ? parseFloat(e.target.value) : undefined })}
                  required
                  placeholder="2500"
                  disabled={!!(formData.loan_principal && formData.interest_rate && formData.loan_tenure_months)}
                  style={{
                    backgroundColor: formData.loan_principal && formData.interest_rate && formData.loan_tenure_months ? 'rgb(243 244 246)' : undefined,
                    cursor: formData.loan_principal && formData.interest_rate && formData.loan_tenure_months ? 'not-allowed' : undefined
                  }}
                />
                {formData.loan_principal && formData.interest_rate && formData.loan_tenure_months && (
                  <p style={{ fontSize: '0.75rem', color: 'rgb(34 197 94)', marginTop: '0.25rem' }}>
                    ✓ EMI automatically calculated based on loan details
                  </p>
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label className="label" htmlFor="loan_tenure_months">
                    Total Tenure (months) *
                  </label>
                  <input
                    id="loan_tenure_months"
                    type="number"
                    className="input-field"
                    value={formData.loan_tenure_months || ''}
                    onChange={(e) => {
                      const months = e.target.value ? parseInt(e.target.value) : undefined;
                      setFormData({ ...formData, loan_tenure_months: months });
                    }}
                    required
                    placeholder="240"
                  />
                </div>

                <div>
                  <label className="label" htmlFor="remaining_tenure_months">
                    Remaining (months) {formData.loan_start_date && formData.loan_tenure_months ? '(Auto-calculated)' : ''}
                  </label>
                  <input
                    id="remaining_tenure_months"
                    type="number"
                    className="input-field"
                    value={
                      formData.loan_start_date && formData.loan_tenure_months
                        ? calculateRemainingTenure(formData.loan_start_date, formData.loan_tenure_months)
                        : formData.remaining_tenure_months || ''
                    }
                    onChange={(e) => setFormData({ ...formData, remaining_tenure_months: e.target.value ? parseInt(e.target.value) : undefined })}
                    placeholder="180"
                    disabled={!!(formData.loan_start_date && formData.loan_tenure_months)}
                    style={{
                      backgroundColor: formData.loan_start_date && formData.loan_tenure_months ? 'rgb(243 244 246)' : undefined,
                      cursor: formData.loan_start_date && formData.loan_tenure_months ? 'not-allowed' : undefined
                    }}
                  />
                  {formData.loan_start_date && formData.loan_tenure_months && (
                    <p style={{ fontSize: '0.75rem', color: 'rgb(34 197 94)', marginTop: '0.25rem' }}>
                      ✓ Auto-calculated
                    </p>
                  )}
                </div>
              </div>

              <div>
                <label className="label" htmlFor="loan_start_date">
                  Loan Start Date
                </label>
                <input
                  id="loan_start_date"
                  type="date"
                  className="input-field"
                  value={formData.loan_start_date ? formData.loan_start_date.split('T')[0] : ''}
                  onChange={(e) => setFormData({ ...formData, loan_start_date: e.target.value })}
                />
              </div>

              {/* Auto-calculated fields: Interest Paid and Principal Paid */}
              {formData.loan_principal && formData.loan_outstanding && formData.emi_amount && formData.loan_start_date && formData.loan_tenure_months && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  backgroundColor: 'rgb(243 244 246)',
                  borderRadius: '0.5rem',
                  border: '1px solid rgb(209 213 219)'
                }}>
                  <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem', color: 'rgb(55 65 81)' }}>
                    📊 Loan Payment Summary (Auto-calculated)
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>
                        Total Interest Paid
                      </label>
                      <div style={{ fontSize: '1rem', fontWeight: '600', color: 'rgb(239 68 68)' }}>
                        ₹{calculateInterestPaid(
                          formData.loan_principal,
                          formData.emi_amount || calculateEMI(formData.loan_principal, formData.interest_rate || 0, formData.loan_tenure_months),
                          formData.loan_start_date,
                          formData.loan_tenure_months,
                          formData.loan_outstanding || formData.loan_principal
                        ).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                    </div>
                    <div>
                      <label style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>
                        Total Principal Paid
                      </label>
                      <div style={{ fontSize: '1rem', fontWeight: '600', color: 'rgb(34 197 94)' }}>
                        ₹{(formData.loan_principal - (formData.loan_outstanding || 0)).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                    </div>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.75rem', fontStyle: 'italic' }}>
                    💡 These values are calculated based on months elapsed since loan start date
                  </p>
                </div>
              )}
            </>
          )}

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <button
              type="submit"
              className="btn-primary"
              disabled={mutation.isPending}
              style={{ flex: 1 }}
            >
              {mutation.isPending ? 'Saving...' : account ? 'Update Account' : 'Add Account'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={mutation.isPending}
              style={{ flex: 1 }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Made with Bob
