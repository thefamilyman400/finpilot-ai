"""
AI Service for OpenAI integration and conversation management
Handles AI copilot interactions, context management, and response generation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json

from openai import AsyncOpenAI

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.account import FinancialAccount
from app.models.transaction import Transaction
from config import settings


class AIService:
    """
    Service for AI-powered features using OpenAI
    Manages conversations, context, and generates intelligent responses
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        
    async def create_conversation(
        self,
        db: AsyncSession,
        user_id: str,
        title: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            context=context or {}
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation
    
    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation by ID"""
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_conversations(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.last_message_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            model=self.model if role == "assistant" else None,
            message_metadata=metadata
        )
        db.add(message)
        
        # Update conversation's last_message_at
        conversation = await db.get(Conversation, conversation_id)
        if conversation:
            conversation.last_message_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(message)
        return message
    
    async def get_conversation_history(
        self,
        db: AsyncSession,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get conversation message history"""
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        if limit:
            # Get the most recent messages
            query = query.order_by(desc(Message.created_at)).limit(limit)
            result = await db.execute(query)
            messages = list(result.scalars().all())
            messages.reverse()  # Reverse to get chronological order
            return messages
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def build_financial_context(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Build financial context for AI from user's data"""
        context = {}
        
        # Get user's accounts
        accounts_result = await db.execute(
            select(FinancialAccount).where(FinancialAccount.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()
        
        if accounts:
            total_balance = sum(acc.balance for acc in accounts)
            context["total_balance"] = total_balance
            context["account_count"] = len(accounts)
            context["accounts"] = [
                {
                    "type": acc.account_type.value,
                    "name": acc.account_name,
                    "balance": acc.balance,
                    "currency": acc.currency
                }
                for acc in accounts
            ]
        
        # Get recent transactions (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        transactions_result = await db.execute(
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= thirty_days_ago
            )
            .order_by(desc(Transaction.transaction_date))
            .limit(50)
        )
        transactions = transactions_result.scalars().all()
        
        if transactions:
            total_income = sum(t.amount for t in transactions if t.is_income)
            total_expenses = sum(t.amount for t in transactions if t.is_expense)
            
            context["monthly_income"] = total_income
            context["monthly_expenses"] = total_expenses
            context["net_cash_flow"] = total_income - total_expenses
            context["transaction_count"] = len(transactions)
            
            # Category breakdown
            category_spending = {}
            for t in transactions:
                if t.is_expense:
                    category = t.category.value if t.category else "uncategorized"
                    category_spending[category] = category_spending.get(category, 0) + t.amount
            
            context["top_spending_categories"] = dict(
                sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
            )
        
        return context
    
    def _build_system_prompt(self, financial_context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt for AI"""
        base_prompt = """You are FinPilot AI, an intelligent financial assistant. You help users manage their finances, 
provide insights, and offer personalized recommendations. You are knowledgeable about:
- Personal finance management
- Budgeting and saving strategies
- Investment basics
- Debt management
- Financial planning

Be helpful, clear, and actionable in your responses. When providing financial advice, always consider the user's 
specific situation and remind them to consult with financial professionals for major decisions."""
        
        if financial_context:
            context_str = f"\n\nUser's Financial Context:\n{json.dumps(financial_context, indent=2)}"
            return base_prompt + context_str
        
        return base_prompt
    
    def _prepare_messages(
        self,
        conversation_history: List[Message],
        new_message: str,
        financial_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API"""
        messages = [
            {"role": "system", "content": self._build_system_prompt(financial_context)}
        ]
        
        # Add conversation history (limit to recent messages to stay within context window)
        max_history = settings.AI_CONVERSATION_MAX_HISTORY
        recent_history = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
        
        for msg in recent_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message
        })
        
        return messages
    
    async def chat(
        self,
        db: AsyncSession,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        include_financial_context: bool = True
    ) -> Dict[str, Any]:
        """
        Main chat function - handles user message and generates AI response
        """
        # Get or create conversation
        if conversation_id:
            conversation = await self.get_conversation(db, conversation_id, user_id)
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            # Create new conversation with title from first message
            title = message[:50] + "..." if len(message) > 50 else message
            conversation = await self.create_conversation(db, user_id, title)
        
        # Build financial context if requested
        financial_context = None
        if include_financial_context:
            financial_context = await self.build_financial_context(db, user_id)
        
        # Get conversation history
        history = await self.get_conversation_history(db, str(conversation.id))
        
        # Prepare messages for OpenAI
        messages = self._prepare_messages(history, message, financial_context)
        
        # Call OpenAI API
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Save user message
            user_msg = await self.add_message(
                db,
                str(conversation.id),
                "user",
                message
            )
            
            # Save assistant message
            assistant_msg = await self.add_message(
                db,
                str(conversation.id),
                "assistant",
                assistant_message,
                tokens_used=tokens_used
            )
            
            return {
                "conversation_id": str(conversation.id),
                "conversation_title": conversation.title,
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "tokens_used": tokens_used
            }
            
        except Exception as e:
            # Log error and raise
            print(f"Error calling OpenAI API: {str(e)}")
            raise
    
    async def generate_quick_analysis(
        self,
        db: AsyncSession,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """Generate a quick financial analysis without creating a conversation"""
        financial_context = await self.build_financial_context(db, user_id)
        
        system_prompt = self._build_system_prompt(financial_context)
        analysis_prompt = f"{query}\n\nProvide a concise analysis with key insights and actionable recommendations."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            analysis = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse insights and recommendations from response
            # This is a simple implementation - could be enhanced with structured output
            lines = analysis.split('\n')
            insights = [line.strip('- ') for line in lines if line.strip().startswith('-')]
            
            return {
                "analysis": analysis,
                "insights": insights[:5],  # Top 5 insights
                "recommendations": insights[5:10] if len(insights) > 5 else [],  # Next 5 as recommendations
                "tokens_used": tokens_used,
                "financial_context": financial_context
            }
            
        except Exception as e:
            print(f"Error generating quick analysis: {str(e)}")
            raise


# Global AI service instance
ai_service = AIService()


# Made with Bob