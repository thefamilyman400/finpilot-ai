import { useState, useEffect } from 'react';
import { copilotService, simulationService } from '../../services';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  calculatorData?: any;
}

// Calculator Form Components
function RetirementCalculatorForm({ onSubmit, onCancel }: { onSubmit: (params: any) => void; onCancel: () => void }) {
  const [form, setForm] = useState({
    current_age: 30,
    retirement_age: 65,
    monthly_contribution: 1000,
    annual_return: 7,
    inflation_rate: 3,
    monthly_income: 0,
  });

  return (
    <div style={{ backgroundColor: 'white', padding: '1rem', borderRadius: '0.5rem', border: '1px solid rgb(229 231 235)' }}>
      <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem' }}>🎯 Retirement Calculator</h4>
      <div style={{ display: 'grid', gap: '0.75rem' }}>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Monthly Income/Salary (₹) <span style={{ color: 'rgb(239 68 68)' }}>*</span></label>
          <input type="number" value={form.monthly_income || ''} onChange={(e) => setForm({ ...form, monthly_income: Number(e.target.value) || 0 })} placeholder="Enter your monthly salary" className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Current Age</label>
          <input type="number" value={form.current_age} onChange={(e) => setForm({ ...form, current_age: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Retirement Age</label>
          <input type="number" value={form.retirement_age} onChange={(e) => setForm({ ...form, retirement_age: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div style={{ backgroundColor: 'rgb(243 244 246)', padding: '0.5rem', borderRadius: '0.375rem', fontSize: '0.7rem', color: 'rgb(107 114 128)' }}>
          💡 <strong>Current Savings:</strong> Will be automatically fetched from your investment accounts
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Monthly Contribution (₹)</label>
          <input type="number" value={form.monthly_contribution} onChange={(e) => setForm({ ...form, monthly_contribution: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Annual Return (%)</label>
          <input type="number" step="0.1" value={form.annual_return} onChange={(e) => setForm({ ...form, annual_return: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Inflation Rate (%)</label>
          <input type="number" step="0.1" value={form.inflation_rate} onChange={(e) => setForm({ ...form, inflation_rate: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        <button onClick={() => onSubmit(form)} disabled={!form.monthly_income} style={{ flex: 1, padding: '0.5rem', backgroundColor: form.monthly_income ? 'rgb(59 130 246)' : 'rgb(209 213 219)', color: 'white', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: form.monthly_income ? 'pointer' : 'not-allowed', fontWeight: '500' }}>Calculate</button>
        <button onClick={onCancel} style={{ padding: '0.5rem 1rem', backgroundColor: 'rgb(243 244 246)', color: 'rgb(107 114 128)', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: 'pointer' }}>Cancel</button>
      </div>
    </div>
  );
}

function InvestmentCalculatorForm({ onSubmit, onCancel }: { onSubmit: (params: any) => void; onCancel: () => void }) {
  const [form, setForm] = useState({
    initial_investment: 10000,
    monthly_contribution: 500,
    years: 20,
    annual_return: 8,
    monthly_income: 0,
  });

  return (
    <div style={{ backgroundColor: 'white', padding: '1rem', borderRadius: '0.5rem', border: '1px solid rgb(229 231 235)' }}>
      <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem' }}>📈 Investment Calculator</h4>
      <div style={{ display: 'grid', gap: '0.75rem' }}>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Monthly Income/Salary (₹) <span style={{ color: 'rgb(239 68 68)' }}>*</span></label>
          <input type="number" value={form.monthly_income || ''} onChange={(e) => setForm({ ...form, monthly_income: Number(e.target.value) || 0 })} placeholder="Enter your monthly salary" className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Initial Investment (₹)</label>
          <input type="number" value={form.initial_investment} onChange={(e) => setForm({ ...form, initial_investment: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Monthly Contribution (₹)</label>
          <input type="number" value={form.monthly_contribution} onChange={(e) => setForm({ ...form, monthly_contribution: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Investment Period (Years)</label>
          <input type="number" value={form.years} onChange={(e) => setForm({ ...form, years: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Expected Annual Return (%)</label>
          <input type="number" step="0.1" value={form.annual_return} onChange={(e) => setForm({ ...form, annual_return: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        <button onClick={() => onSubmit(form)} disabled={!form.monthly_income} style={{ flex: 1, padding: '0.5rem', backgroundColor: form.monthly_income ? 'rgb(59 130 246)' : 'rgb(209 213 219)', color: 'white', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: form.monthly_income ? 'pointer' : 'not-allowed', fontWeight: '500' }}>Calculate</button>
        <button onClick={onCancel} style={{ padding: '0.5rem 1rem', backgroundColor: 'rgb(243 244 246)', color: 'rgb(107 114 128)', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: 'pointer' }}>Cancel</button>
      </div>
    </div>
  );
}

function LoanCalculatorForm({ onSubmit, onCancel }: { onSubmit: (params: any) => void; onCancel: () => void }) {
  const [form, setForm] = useState({
    loan_amount: 200000,
    interest_rate: 4.5,
    loan_term_years: 30,
    extra_payment: 0,
    monthly_income: 0,
  });

  return (
    <div style={{ backgroundColor: 'white', padding: '1rem', borderRadius: '0.5rem', border: '1px solid rgb(229 231 235)' }}>
      <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem' }}>🏠 Loan Calculator</h4>
      <div style={{ display: 'grid', gap: '0.75rem' }}>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Monthly Income/Salary (₹) <span style={{ color: 'rgb(239 68 68)' }}>*</span></label>
          <input type="number" value={form.monthly_income || ''} onChange={(e) => setForm({ ...form, monthly_income: Number(e.target.value) || 0 })} placeholder="Enter your monthly salary" className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Loan Amount (₹)</label>
          <input type="number" value={form.loan_amount} onChange={(e) => setForm({ ...form, loan_amount: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Interest Rate (% per year)</label>
          <input type="number" step="0.1" value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Loan Term (Years)</label>
          <input type="number" value={form.loan_term_years} onChange={(e) => setForm({ ...form, loan_term_years: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', fontWeight: '500', color: 'rgb(107 114 128)', display: 'block', marginBottom: '0.25rem' }}>Extra Monthly Payment (₹)</label>
          <input type="number" value={form.extra_payment} onChange={(e) => setForm({ ...form, extra_payment: Number(e.target.value) })} className="form-input" style={{ fontSize: '0.75rem', padding: '0.5rem', width: '100%' }} />
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        <button onClick={() => onSubmit(form)} disabled={!form.monthly_income} style={{ flex: 1, padding: '0.5rem', backgroundColor: form.monthly_income ? 'rgb(59 130 246)' : 'rgb(209 213 219)', color: 'white', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: form.monthly_income ? 'pointer' : 'not-allowed', fontWeight: '500' }}>Calculate</button>
        <button onClick={onCancel} style={{ padding: '0.5rem 1rem', backgroundColor: 'rgb(243 244 246)', color: 'rgb(107 114 128)', border: 'none', borderRadius: '0.375rem', fontSize: '0.75rem', cursor: 'pointer' }}>Cancel</button>
      </div>
    </div>
  );
}

export default function ChatAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hi! I\'m your FinPilot AI assistant. I can help you with:\n\n• **Financial Calculators** - Try "retirement", "investment", or "loan"\n• Transaction analysis\n• Budget recommendations\n• Document insights\n\n**Quick Commands:**\n• Type `retirement` for retirement planning\n• Type `investment` for investment growth\n• Type `loan` for loan amortization\n\nWhat would you like to know?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showCalculator, setShowCalculator] = useState<'retirement' | 'investment' | 'loan' | null>(null);

  // No need to create conversation upfront - the chat endpoint handles it

  const detectCalculatorRequest = (text: string): 'retirement' | 'investment' | 'loan' | null => {
    const lower = text.toLowerCase();
    if (lower.includes('retirement') || lower.includes('retire')) return 'retirement';
    if (lower.includes('investment') || lower.includes('invest')) return 'investment';
    if (lower.includes('loan') || lower.includes('mortgage')) return 'loan';
    return null;
  };

  const runCalculator = async (type: 'retirement' | 'investment' | 'loan', params: any) => {
    setIsLoading(true);
    try {
      // Use the quick simulation endpoints that create and run in one call
      let endpoint = '';
      let requestParams = { ...params };
      
      if (type === 'retirement') {
        endpoint = '/simulations/retirement/quick';
        // Convert percentage to decimal
        requestParams.expected_return = params.annual_return / 100;
        requestParams.inflation_rate = params.inflation_rate / 100;
        delete requestParams.annual_return;
        // Add monthly income if provided
        if (params.monthly_income && params.monthly_income > 0) {
          requestParams.current_monthly_income = params.monthly_income;
        }
      } else if (type === 'investment') {
        endpoint = '/simulations/investment/quick';
        // Convert percentage to decimal
        requestParams.expected_return = params.annual_return / 100;
        delete requestParams.annual_return;
        delete requestParams.compound_frequency; // Not used by backend
      } else if (type === 'loan') {
        endpoint = '/simulations/loan-payoff/quick';
        // Convert percentage to decimal
        requestParams.interest_rate = params.interest_rate / 100;
        // Add monthly income if provided for affordability analysis
        if (params.monthly_income && params.monthly_income > 0) {
          requestParams.current_monthly_income = params.monthly_income;
        }
      }

      console.log('Sending params to backend:', requestParams); // Debug log
      
      const response = await fetch(`http://localhost:8000/api/v1${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(requestParams),
      });

      if (!response.ok) {
        throw new Error('Simulation failed');
      }

      const simulation = await response.json();
      console.log('Received simulation results:', simulation.results); // Debug log

      const resultMessage: ChatMessage = {
        role: 'assistant',
        content: formatCalculatorResults(type, simulation.results),
        timestamp: new Date(),
        calculatorData: simulation.results,
      };
      setMessages((prev) => [...prev, resultMessage]);
      setShowCalculator(null);
    } catch (error) {
      console.error('Calculator error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I couldn\'t run the calculation. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCalculatorResults = (type: string, results: any): string => {
    if (type === 'retirement') {
      const isOnTrack = results.shortfall === 0 || results.surplus > 0;
      let output = `🎯 **Retirement Planning Results**\n\n`;
      
      // Show investment balance used if available
      if (results.spending_data_used && results.spending_data_used.total_investment_balance > 0) {
        output += `💼 **Current Investment Balance:** ₹${results.spending_data_used.total_investment_balance?.toLocaleString()}\n`;
        output += `   _(Auto-fetched from your investment accounts)_\n\n`;
      }
      
      output += `💰 **Projected at Retirement:** ₹${results.projected_savings_at_retirement?.toLocaleString() || 'N/A'}\n` +
        `📊 **Required Savings:** ₹${results.required_savings?.toLocaleString() || 'N/A'}\n` +
        `${results.shortfall > 0 ? `⚠️ **Shortfall:** ₹${results.shortfall?.toLocaleString()}` : `✅ **Surplus:** ₹${results.surplus?.toLocaleString()}`}\n` +
        `💵 **Monthly Needed:** ₹${results.required_monthly_contribution?.toLocaleString() || '0'}\n` +
        `📈 **Success Probability:** ${results.success_probability || 'N/A'}%\n\n` +
        `Based on your inputs, you're ${isOnTrack ? '✅ on track' : '⚠️ behind'} for retirement!`;
      
      // Add spending data if available
      if (results.spending_data_used) {
        const spend = results.spending_data_used;
        output += `\n\n💰 **Monthly Cash Flow Breakdown:**\n`;
        output += `📊 Income: ₹${spend.monthly_income?.toLocaleString() || 'N/A'}\n`;
        output += `➖ Expenses: ₹${spend.monthly_expenses?.toLocaleString() || 'N/A'}\n`;
        output += `➖ Existing Loan EMI: ₹${results.loan_obligations?.total_monthly_emi?.toLocaleString() || '0'}\n`;
        output += `━━━━━━━━━━━━━━━━━━━━\n`;
        output += `✅ **Available for Retirement Savings: ₹${spend.available_for_investment?.toLocaleString() || '0'}**\n\n`;
        
        if (results.loan_obligations && results.loan_obligations.total_monthly_emi > 0) {
          const emiPercent = ((results.loan_obligations.total_monthly_emi / spend.monthly_income) * 100).toFixed(1);
          output += `⚠️ Your EMI (₹${results.loan_obligations.total_monthly_emi?.toLocaleString()}) is ${emiPercent}% of income\n`;
          output += `📋 Active Loans: ${results.loan_obligations.loan_count}\n`;
          
          if (spend.available_for_investment <= 0) {
            output += `\n🚨 **Warning:** Your EMI exceeds your savings capacity!\n`;
            output += `Consider loan restructuring or increasing income.`;
          }
        }
      }
      
      return output;
    } else if (type === 'investment') {
      return `📈 **Investment Growth Results**\n\n` +
        `💰 **Expected Final Value:** ₹${results.expected_final_value?.toLocaleString() || 'N/A'}\n` +
        `📊 **Total Contributions:** ₹${results.total_contributions?.toLocaleString() || 'N/A'}\n` +
        `📈 **Total Gains:** ₹${results.total_gains?.toLocaleString() || 'N/A'}\n` +
        `📊 **Best Case:** ₹${results.best_case_scenario?.toLocaleString() || 'N/A'}\n` +
        `📉 **Worst Case:** ₹${results.worst_case_scenario?.toLocaleString() || 'N/A'}\n\n` +
        `Your investment could grow significantly over time!`;
    } else if (type === 'loan') {
      let output = `🏠 **Loan Amortization Results**\n\n` +
        `💵 **Monthly Payment:** ₹${results.monthly_payment?.toLocaleString() || 'N/A'}\n` +
        `💰 **Total Interest:** ₹${results.total_interest_paid?.toLocaleString() || 'N/A'}\n` +
        `📊 **Total Paid:** ₹${results.total_amount_paid?.toLocaleString() || 'N/A'}\n` +
        `⏱️ **Payoff Time:** ${results.months_to_payoff || 'N/A'} months (${results.years_to_payoff || 'N/A'} years)\n\n` +
        `${results.extra_monthly_payment > 0 ? `✅ Extra payments will save you ₹${results.interest_saved?.toLocaleString() || 0} and ${results.years_saved || 0} years!` : '💡 Consider extra payments to save on interest!'}`;
      
      if (results.existing_monthly_emi > 0) {
        output += `\n\n🏦 **Existing Loan EMI:** ₹${results.existing_monthly_emi?.toLocaleString()}`;
        output += `\n📈 **Combined Monthly EMI:** ₹${results.total_monthly_payment_with_existing_emi?.toLocaleString()}`;
        
        if (results.existing_loan_outstanding > 0) {
          output += `\n🧾 **Existing Outstanding:** ₹${results.existing_loan_outstanding?.toLocaleString()}`;
          output += `\n📊 **Combined Principal:** ₹${results.combined_loan_principal_with_existing?.toLocaleString()}`;
        }
      }
      
      // Add affordability analysis if available
      if (results.affordability_analysis) {
        const afford = results.affordability_analysis;
        output += `\n\n💰 **Affordability Analysis:**\n`;
        output += `📊 Monthly Income: ₹${afford.monthly_income?.toLocaleString()}\n`;
        
        if (afford.existing_emi > 0) {
          output += `🏦 Existing EMI: ₹${afford.existing_emi?.toLocaleString()}\n`;
        }
        
        output += `💳 New EMI: ₹${afford.new_emi?.toLocaleString()}\n`;
        output += `📈 Total EMI Burden: ₹${afford.total_emi_burden?.toLocaleString()} (${afford.emi_to_income_ratio}% of income)\n`;
        output += `💵 Available After EMI: ₹${afford.available_income_after_emi?.toLocaleString()}\n\n`;
        
        // Affordability status with emoji
        const statusEmoji = afford.is_affordable ? '✅' : '⚠️';
        output += `${statusEmoji} **${afford.affordability_status}**\n`;
        
        // Add recommendation if available
        if (afford.recommendation) {
          const rec = afford.recommendation;
          output += `\n💡 **Smart Recommendation:**\n`;
          output += `${rec.message}\n`;
          output += `• Recommended EMI: ₹${rec.recommended_emi?.toLocaleString()}\n`;
          output += `• EMI Reduction: ₹${rec.emi_reduction?.toLocaleString()}/month\n`;
          output += `• Additional Interest: ₹${rec.additional_interest_cost?.toLocaleString()}\n`;
          output += `\n📌 This will reduce your EMI burden and make repayment more comfortable!`;
        }
      } else {
        // Show message when no transaction data
        output += `\n\n💡 **Tip:** Add income transactions to see affordability analysis and get personalized loan tenure recommendations based on your salary!`;
      }
      
      return output;
    }
    return 'Calculation complete!';
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput('');

    const calculatorType = detectCalculatorRequest(userInput);
    if (calculatorType) {
      setShowCalculator(calculatorType);
      const promptMessage: ChatMessage = {
        role: 'assistant',
        content: `Great! Let's set up your ${calculatorType} calculator. Fill in the form below:`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, promptMessage]);
      return;
    }

    // Send to AI using the chat endpoint
    setIsLoading(true);

    try {
      // Use the chat endpoint which handles conversation creation automatically
      const response = await fetch('http://localhost:8000/api/v1/copilot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          message: userInput,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Update conversation ID if this was the first message
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Add assistant's response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.assistant_message.content,
        timestamp: new Date(data.assistant_message.created_at),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (isMinimized) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        style={{
          position: 'fixed',
          right: '1rem',
          bottom: '1rem',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: 'rgb(59 130 246)',
          color: 'white',
          border: 'none',
          fontSize: '1.5rem',
          cursor: 'pointer',
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          transition: 'all 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        💬
      </button>
    );
  }

  return (
    <aside
      style={{
        width: '360px',
        backgroundColor: 'white',
        borderLeft: '1px solid rgb(229 231 235)',
        height: '100vh',
        position: 'fixed',
        right: 0,
        top: 0,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '1rem 1.5rem',
          borderBottom: '1px solid rgb(229 231 235)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'linear-gradient(135deg, rgb(59 130 246) 0%, rgb(147 51 234) 100%)',
          color: 'white',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🤖</span>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: '600', margin: 0 }}>AI Assistant</h3>
            <p style={{ fontSize: '0.75rem', margin: 0, opacity: 0.9 }}>With Calculators</p>
          </div>
        </div>
        <button
          onClick={() => setIsMinimized(true)}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: 'none',
            color: 'white',
            width: '32px',
            height: '32px',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          ➖
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                maxWidth: '85%',
                padding: '0.75rem 1rem',
                borderRadius: '0.75rem',
                backgroundColor: message.role === 'user' ? 'rgb(59 130 246)' : 'rgb(243 244 246)',
                color: message.role === 'user' ? 'white' : 'rgb(31 41 55)',
                fontSize: '0.875rem',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap',
              }}
            >
              {message.content}
            </div>
            <span
              style={{
                fontSize: '0.75rem',
                color: 'rgb(156 163 175)',
                marginTop: '0.25rem',
              }}
            >
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: 'rgb(59 130 246)',
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
            <span style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div
        style={{
          padding: '1rem',
          borderTop: '1px solid rgb(229 231 235)',
          backgroundColor: 'rgb(249 250 251)',
        }}
      >
        {showCalculator ? (
          <div style={{ marginBottom: '0.5rem', maxHeight: '400px', overflowY: 'auto', padding: '0.25rem' }}>
            {showCalculator === 'retirement' && (
              <RetirementCalculatorForm onSubmit={(params) => runCalculator('retirement', params)} onCancel={() => setShowCalculator(null)} />
            )}
            {showCalculator === 'investment' && (
              <InvestmentCalculatorForm onSubmit={(params) => runCalculator('investment', params)} onCancel={() => setShowCalculator(null)} />
            )}
            {showCalculator === 'loan' && (
              <LoanCalculatorForm onSubmit={(params) => runCalculator('loan', params)} onCancel={() => setShowCalculator(null)} />
            )}
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your finances..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  border: '1px solid rgb(209 213 219)',
                  fontSize: '0.875rem',
                  resize: 'none',
                  minHeight: '60px',
                  maxHeight: '120px',
                  fontFamily: 'inherit',
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                style={{
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  backgroundColor: input.trim() && !isLoading ? 'rgb(59 130 246)' : 'rgb(209 213 219)',
                  color: 'white',
                  fontSize: '1.25rem',
                  cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s',
                }}
              >
                ⬆️
              </button>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem', marginBottom: 0 }}>
              Try: "retirement", "investment", or "loan" for calculators
            </p>
          </>
        )}
      </div>
    </aside>
  );
}

// Made with Bob
