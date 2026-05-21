"""
Database models for FinPilot AI Backend
"""
from app.models.user import User
from app.models.account import FinancialAccount, AccountType, ConnectionStatus
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.conversation import Conversation, Message
from app.models.recommendation import (
    Recommendation,
    RecommendationType,
    RecommendationPriority,
    RecommendationStatus
)
from app.models.document import Document, DocumentType, ProcessingStatus
from app.models.simulation import FinancialSimulation, SimulationType, SimulationStatus
from app.models.workflow import (
    AutonomousWorkflow,
    WorkflowExecution,
    WorkflowType,
    TriggerType,
    ActionType,
    WorkflowStatus,
    ExecutionStatus
)

__all__ = [
    # User
    "User",
    # Financial Accounts
    "FinancialAccount",
    "AccountType",
    "ConnectionStatus",
    # Transactions
    "Transaction",
    "TransactionType",
    "TransactionCategory",
    # AI Conversations
    "Conversation",
    "Message",
    # Recommendations
    "Recommendation",
    "RecommendationType",
    "RecommendationPriority",
    "RecommendationStatus",
    # Documents
    "Document",
    "DocumentType",
    "ProcessingStatus",
    # Simulations
    "FinancialSimulation",
    "SimulationType",
    "SimulationStatus",
    # Workflows
    "AutonomousWorkflow",
    "WorkflowExecution",
    "WorkflowType",
    "TriggerType",
    "ActionType",
    "WorkflowStatus",
    "ExecutionStatus",
]

# Made with Bob
