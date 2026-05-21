import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionService } from '../../services/transaction.service';
import { accountService } from '../../services/account.service';
import type { Account } from '../../types';
import MainLayout from '../../components/layout/MainLayout';

export default function Transactions() {
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [filters, setFilters] = useState({
    account_id: '',
    category: '',
    start_date: '',
    end_date: '',
  });
  const [newTransaction, setNewTransaction] = useState({
    account_id: '',
    amount: '',
    transaction_type: 'debit',
    category: '',
    description: '',
    transaction_date: new Date().toISOString().split('T')[0],
    merchant_name: '',
    notes: '',
  });

  // Fetch accounts for filter dropdown
  const { data: accounts } = useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  // Log accounts when they change
  console.log('Accounts:', accounts);

  // Fetch transactions with filters
  const { data: transactionsData, isLoading } = useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionService.getTransactions(filters),
  });

  // Create transaction mutation
  const createMutation = useMutation({
    mutationFn: transactionService.createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setShowAddForm(false);
      setNewTransaction({
        account_id: '',
        amount: '',
        transaction_type: 'debit',
        category: '',
        description: '',
        transaction_date: new Date().toISOString().split('T')[0],
        merchant_name: '',
        notes: '',
      });
      alert('Transaction created successfully!');
    },
    onError: (error: any) => {
      console.error('Transaction creation error:', error.response?.data);
      const errorDetail = error.response?.data?.detail;
      const errorMessage = typeof errorDetail === 'string'
        ? errorDetail
        : JSON.stringify(errorDetail || error.message);
      alert(`Failed to create transaction: ${errorMessage}`);
    },
  });

  const handleCreateTransaction = () => {
    if (!newTransaction.account_id) {
      alert('Please select an account. You need to create an account first if you don\'t have one.');
      return;
    }
    if (!newTransaction.amount || parseFloat(newTransaction.amount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    if (!newTransaction.description) {
      alert('Please enter a description');
      return;
    }
    const payload: any = {
      account_id: newTransaction.account_id,
      transaction_type: newTransaction.transaction_type.toLowerCase(),
      amount: parseFloat(newTransaction.amount),
      description: newTransaction.description,
      transaction_date: newTransaction.transaction_date,
    };
    
    if (newTransaction.category) payload.category = newTransaction.category.toLowerCase();
    if (newTransaction.merchant_name) payload.merchant_name = newTransaction.merchant_name;
    if (newTransaction.notes) payload.notes = newTransaction.notes;
    
    console.log('Creating transaction with payload:', payload);
    createMutation.mutate(payload);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      income: 'rgb(34 197 94)',
      expense: 'rgb(239 68 68)',
      transfer: 'rgb(59 130 246)',
      investment: 'rgb(168 85 247)',
    };
    return colors[category] || 'rgb(107 114 128)';
  };

  return (
    <MainLayout>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
          Transactions
        </h2>
        <p style={{ color: 'rgb(107 114 128)' }}>
          View and manage your financial transactions
        </p>
      </div>

        {/* Add Transaction Button */}
        <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-primary"
          >
            {showAddForm ? 'Cancel' : '+ Add Transaction'}
          </button>
        </div>

        {/* Add Transaction Form */}
        {showAddForm && (
          <div className="card" style={{ marginBottom: '2rem', padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '2rem', borderBottom: '2px solid rgb(229 231 235)', paddingBottom: '1rem' }}>
              Add New Transaction
            </h3>
            
            {/* Primary Fields - 2 Column Layout */}
            <div style={{ marginBottom: '2rem' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(75 85 99)', marginBottom: '1.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Transaction Details
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Account *</label>
                  <select
                    className="form-input"
                    value={newTransaction.account_id}
                    onChange={(e) => setNewTransaction({ ...newTransaction, account_id: e.target.value })}
                  >
                    <option value="">Select Account</option>
                    {accounts?.map((account) => (
                      <option key={account.id} value={account.id}>
                        {account.account_name || `${account.institution_name} - ${account.account_type}`}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Type *</label>
                  <select
                    className="form-input"
                    value={newTransaction.transaction_type}
                    onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value })}
                  >
                    <option value="debit">💸 Debit (Expense)</option>
                    <option value="credit">💰 Credit (Income)</option>
                  </select>
                </div>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Amount *</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-input"
                    placeholder="0.00"
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                    style={{ fontSize: '1rem', fontWeight: '500' }}
                  />
                </div>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Date *</label>
                  <input
                    type="date"
                    className="form-input"
                    value={newTransaction.transaction_date}
                    onChange={(e) => setNewTransaction({ ...newTransaction, transaction_date: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* Secondary Fields - 2 Column Layout */}
            <div style={{ marginBottom: '2rem' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(75 85 99)', marginBottom: '1.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Additional Information
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Description *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., Weekly grocery shopping"
                    value={newTransaction.description}
                    onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Merchant (Optional)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., Walmart, Amazon"
                    value={newTransaction.merchant_name}
                    onChange={(e) => setNewTransaction({ ...newTransaction, merchant_name: e.target.value })}
                  />
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Category</label>
                  <select
                    className="form-input"
                    value={newTransaction.category}
                    onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
                  >
                    <option value="">Select Category</option>
                    <optgroup label="💵 Income">
                      <option value="salary">Salary</option>
                      <option value="freelance">Freelance</option>
                      <option value="investment_income">Investment Income</option>
                      <option value="other_income">Other Income</option>
                    </optgroup>
                    <optgroup label="🏠 Housing">
                      <option value="rent">Rent</option>
                      <option value="mortgage">Mortgage</option>
                      <option value="utilities">Utilities</option>
                      <option value="home_maintenance">Home Maintenance</option>
                    </optgroup>
                    <optgroup label="🚗 Transportation">
                      <option value="gas">Gas</option>
                      <option value="public_transit">Public Transit</option>
                      <option value="car_payment">Car Payment</option>
                      <option value="car_maintenance">Car Maintenance</option>
                      <option value="parking">Parking</option>
                    </optgroup>
                    <optgroup label="🍔 Food">
                      <option value="groceries">Groceries</option>
                      <option value="restaurants">Restaurants</option>
                      <option value="coffee">Coffee</option>
                    </optgroup>
                    <optgroup label="🛍️ Shopping">
                      <option value="clothing">Clothing</option>
                      <option value="electronics">Electronics</option>
                      <option value="general_shopping">General Shopping</option>
                    </optgroup>
                    <optgroup label="🎬 Entertainment">
                      <option value="entertainment">Entertainment</option>
                      <option value="subscriptions">Subscriptions</option>
                      <option value="hobbies">Hobbies</option>
                    </optgroup>
                    <optgroup label="💊 Healthcare">
                      <option value="medical">Medical</option>
                      <option value="pharmacy">Pharmacy</option>
                      <option value="insurance">Insurance</option>
                    </optgroup>
                    <optgroup label="💰 Financial">
                      <option value="savings">Savings</option>
                      <option value="investments">Investments</option>
                      <option value="loan_payment">Loan Payment</option>
                      <option value="credit_card_payment">Credit Card Payment</option>
                      <option value="fees">Fees</option>
                    </optgroup>
                    <optgroup label="📚 Other">
                      <option value="education">Education</option>
                      <option value="gifts">Gifts</option>
                      <option value="charity">Charity</option>
                      <option value="taxes">Taxes</option>
                      <option value="uncategorized">Uncategorized</option>
                    </optgroup>
                  </select>
                </div>
              </div>
              <div>
                <label className="form-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Notes (Optional)</label>
                <textarea
                  className="form-input"
                  rows={3}
                  placeholder="Add any additional notes about this transaction..."
                  value={newTransaction.notes}
                  onChange={(e) => setNewTransaction({ ...newTransaction, notes: e.target.value })}
                  style={{ resize: 'vertical', width: '100%' }}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', paddingTop: '1.5rem', borderTop: '1px solid rgb(229 231 235)' }}>
              <button
                onClick={() => setShowAddForm(false)}
                className="btn-secondary"
                style={{ minWidth: '100px', padding: '0.625rem 1.25rem' }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTransaction}
                className="btn-primary"
                disabled={createMutation.isPending}
                style={{ minWidth: '140px', padding: '0.625rem 1.25rem' }}
              >
                {createMutation.isPending ? 'Creating...' : '✓ Create Transaction'}
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '1rem' }}>
            Filters
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <label className="form-label">Account</label>
              <select
                className="form-input"
                value={filters.account_id}
                onChange={(e) => setFilters({ ...filters, account_id: e.target.value })}
              >
                <option value="">All Accounts</option>
                {accounts?.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_name || `${account.institution_name} - ${account.account_type}`}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="form-label">Category</label>
              <select
                className="form-input"
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              >
                <option value="">All Categories</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
                <option value="transfer">Transfer</option>
                <option value="investment">Investment</option>
              </select>
            </div>
            <div>
              <label className="form-label">Start Date</label>
              <input
                type="date"
                className="form-input"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              />
            </div>
            <div>
              <label className="form-label">End Date</label>
              <input
                type="date"
                className="form-input"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              />
            </div>
          </div>
        </div>

        {/* Transactions List */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)' }}>
              Recent Transactions
            </h3>
            <span style={{ color: 'rgb(107 114 128)', fontSize: '0.875rem' }}>
              {transactionsData?.total || 0} total
            </span>
          </div>

          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'rgb(107 114 128)' }}>
              Loading transactions...
            </div>
          ) : transactionsData?.transactions && transactionsData.transactions.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgb(229 231 235)' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'rgb(107 114 128)' }}>
                      Date
                    </th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'rgb(107 114 128)' }}>
                      Description
                    </th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'rgb(107 114 128)' }}>
                      Category
                    </th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'rgb(107 114 128)' }}>
                      Account
                    </th>
                    <th style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: 'rgb(107 114 128)' }}>
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {transactionsData.transactions.map((transaction) => (
                    <tr key={transaction.id} style={{ borderBottom: '1px solid rgb(229 231 235)' }}>
                      <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'rgb(17 24 39)' }}>
                        {formatDate(transaction.transaction_date)}
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'rgb(17 24 39)' }}>
                        {transaction.description}
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            backgroundColor: `${getCategoryColor(transaction.category)}20`,
                            color: getCategoryColor(transaction.category),
                          }}
                        >
                          {transaction.category}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                        {(() => {
                          const account = accounts?.find(a => a.id === transaction.account_id);
                          return account ? (account.account_name || `${account.institution_name} - ${account.account_type}`) : 'Unknown';
                        })()}
                      </td>
                      <td
                        style={{
                          padding: '0.75rem',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: transaction.transaction_type === 'credit' ? 'rgb(34 197 94)' : 'rgb(239 68 68)',
                        }}
                      >
                        {transaction.transaction_type === 'credit' ? '+' : '-'}{formatCurrency(Math.abs(transaction.amount))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <p style={{ color: 'rgb(107 114 128)', marginBottom: '1rem' }}>
                No transactions found
              </p>
              <p style={{ color: 'rgb(156 163 175)', fontSize: '0.875rem' }}>
                Transactions will appear here once you add them to your accounts
              </p>
            </div>
          )}
        </div>
    </MainLayout>
  );
}

// Made with Bob