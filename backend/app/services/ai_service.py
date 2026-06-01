"""
AI Service for Google Gemini integration and conversation management
Handles AI copilot interactions, context management, and response generation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
import asyncio

import httpx

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.account import FinancialAccount
from app.models.transaction import Transaction
from config import settings


class AIService:
    """
    Service for AI-powered features using Google Gemini
    Manages conversations, context, and generates intelligent responses
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required in environment variables")
        
        # Use gemini-pro as default model
        self.model = settings.GOOGLE_GEMINI_MODEL or "gemini-pro"
        self.temperature = settings.OPENAI_TEMPERATURE  # Reuse temperature setting
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

    def _normalize_decimals(self, value: Any) -> Any:
        """Recursively normalize Decimal objects to JSON-friendly types."""
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {k: self._normalize_decimals(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_decimals(v) for v in value]
        return value

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
            total_balance = sum(float(acc.balance) if acc.balance is not None else 0.0 for acc in accounts)
            context["total_balance"] = total_balance
            context["account_count"] = len(accounts)
            context["accounts"] = [
                {
                    "type": acc.account_type.value,
                    "name": acc.account_name,
                    "balance": float(acc.balance) if acc.balance is not None else 0.0,
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
            total_income = sum(float(t.amount) if t.amount is not None else 0.0 for t in transactions if t.is_income)
            total_expenses = sum(float(t.amount) if t.amount is not None else 0.0 for t in transactions if t.is_expense)
            
            context["monthly_income"] = total_income
            context["monthly_expenses"] = total_expenses
            context["net_cash_flow"] = total_income - total_expenses
            context["transaction_count"] = len(transactions)
            
            # Category breakdown
            category_spending = {}
            for t in transactions:
                if t.is_expense and t.amount is not None:
                    category = t.category.value if t.category else "uncategorized"
                    category_spending[category] = category_spending.get(category, 0) + float(t.amount)
            
            context["top_spending_categories"] = dict(
                sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
            )
        
        return self._normalize_decimals(context)
    
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
    
    def _prepare_conversation_text(
        self,
        conversation_history: List[Message],
        new_message: str,
        financial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare conversation text for Gemini API"""
        # Build the full conversation context
        prompt = self._build_system_prompt(financial_context) + "\n\n"
        
        # Add conversation history (limit to recent messages)
        max_history = settings.AI_CONVERSATION_MAX_HISTORY
        recent_history = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
        
        for msg in recent_history:
            role_label = "User" if msg.role == "user" else "Assistant"
            prompt += f"{role_label}: {msg.content}\n\n"
        
        # Add new user message
        prompt += f"User: {new_message}\n\nAssistant:"
        
        return prompt

    async def _call_gemini(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Call Google Gemini API to generate text with retry logic and exponential backoff.
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retry attempts for rate limit errors
            
        Returns:
            Dict containing assistant response and tokens used
            
        Raises:
            ValueError: For quota exceeded or other API errors
        """
        # Use v1beta for experimental models, v1 for stable
        api_version = "v1beta" if "exp" in self.model or "2.0" in self.model or "2.5" in self.model or "3." in self.model else "v1"
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{self.model}:generateContent?key={self.api_key}"
        
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": float(self.temperature),
                "maxOutputTokens": int(self.max_tokens),
            }
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(url, json=body)
                    resp.raise_for_status()
                    data = resp.json()

                # Parse Gemini response
                text = ''
                if isinstance(data, dict):
                    candidates = data.get('candidates', [])
                    if candidates and len(candidates) > 0:
                        content = candidates[0].get('content', {})
                        parts = content.get('parts', [])
                        if parts and len(parts) > 0:
                            text = parts[0].get('text', '')
                    
                    if not text:
                        # Fallback parsing
                        text = data.get('text', '') or data.get('output', '')

                if not text:
                    raise ValueError("No text generated from Gemini API")

                return {"assistant": text, "tokens_used": 0}
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                
                # Parse error response
                try:
                    error_json = json.loads(error_detail)
                    error_code = error_json.get('error', {}).get('code')
                    error_message = error_json.get('error', {}).get('message', '')
                    error_status = error_json.get('error', {}).get('status', '')
                except:
                    error_code = e.response.status_code
                    error_message = error_detail
                    error_status = ''
                
                # Handle retryable errors (429 quota exceeded, 503 service unavailable)
                if error_code == 429 or error_status == 'RESOURCE_EXHAUSTED' or error_code == 503 or error_status == 'UNAVAILABLE':
                    error_type = "quota exceeded" if error_code == 429 else "service unavailable"
                    print(f"Gemini API {error_type} (attempt {attempt + 1}/{max_retries}): {error_message}")
                    
                    # Extract retry delay from error if available
                    retry_delay = 1.0  # Default 1 second
                    try:
                        error_json = json.loads(error_detail)
                        details = error_json.get('error', {}).get('details', [])
                        for detail in details:
                            if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                                retry_str = detail.get('retryDelay', '1s')
                                # Parse delay like "32s" or "32.502468267s"
                                retry_delay = float(retry_str.rstrip('s'))
                                break
                    except:
                        pass
                    
                    # If this is the last attempt, raise a user-friendly error
                    if attempt == max_retries - 1:
                        if error_code == 429 or error_status == 'RESOURCE_EXHAUSTED':
                            raise ValueError(
                                "AI service quota exceeded. The Gemini API free tier limit has been reached. "
                                "Please try again later or upgrade your API plan at https://ai.google.dev/pricing"
                            )
                        else:
                            raise ValueError(
                                "AI service temporarily unavailable due to high demand. "
                                "Please try again in a few moments."
                            )
                    
                    # Exponential backoff with jitter
                    wait_time = min(retry_delay, 2 ** attempt) + (0.1 * attempt)
                    print(f"Retrying after {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                    last_error = e
                    continue
                
                # For other HTTP errors, don't retry
                print(f"Gemini API HTTP error: {error_detail}")
                raise ValueError(f"Gemini API error (HTTP {error_code}): {error_message}")
                
            except Exception as e:
                print(f"Gemini API error: {str(e)}")
                raise ValueError(f"Failed to call Gemini: {str(e)}")
        
        # If we exhausted all retries
        if last_error:
            raise ValueError(
                "AI service temporarily unavailable due to rate limits. Please try again in a few moments."
            )
        
        raise ValueError("Failed to call Gemini API after multiple attempts")
    
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
        
        # Prepare prompt for Gemini
        prompt = self._prepare_conversation_text(history, message, financial_context)
        
        # Call Gemini API
        try:
            result = await self._call_gemini(prompt)
            assistant_message = result.get('assistant', '')
            tokens_used = result.get('tokens_used', 0)
            
            if not assistant_message:
                raise ValueError("Empty response from AI")
            
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
            print(f"Error calling Gemini API: {str(e)}")
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
        analysis_prompt = f"{system_prompt}\n\nUser Query: {query}\n\nProvide a concise analysis with key insights and actionable recommendations.\n\nAssistant:"
        
        try:
            result = await self._call_gemini(analysis_prompt)
            analysis = result.get('assistant', '')
            tokens_used = result.get('tokens_used', 0)
            
            # Parse insights and recommendations from response
            lines = analysis.split('\n')
            insights = []
            recommendations = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    cleaned = line.lstrip('-•* ').strip()
                    if cleaned:
                        if len(insights) < 5:
                            insights.append(cleaned)
                        elif len(recommendations) < 5:
                            recommendations.append(cleaned)
            
            return {
                "analysis": analysis,
                "insights": insights,
                "recommendations": recommendations,
                "tokens_used": tokens_used,
                "financial_context": financial_context
            }
            
        except Exception as e:
            print(f"Error generating quick analysis: {str(e)}")
            raise


# Global AI service instance
ai_service = AIService()


# Made with Bob