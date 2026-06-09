"""
Escalation Service
Manages Human-in-the-Loop (HITL) workflows for complex or high-risk queries
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.escalation import Escalation, EscalationPriority, EscalationStatus
from app.models.conversation import Conversation
from app.models.user import User
from app.services.intent_service import Intent, IntentCategory


class EscalationService:
    """Service for managing escalations to human reviewers"""
    
    # Escalation triggers
    ESCALATION_TRIGGERS = {
        "high_risk_query": {
            "description": "Queries about large amounts or high-value decisions",
            "priority": EscalationPriority.HIGH
        },
        "complex_scenario": {
            "description": "Multi-product comparisons or complex financial situations",
            "priority": EscalationPriority.MEDIUM
        },
        "complaint": {
            "description": "Customer complaints or dissatisfaction",
            "priority": EscalationPriority.HIGH
        },
        "regulatory_question": {
            "description": "Questions about regulations or compliance",
            "priority": EscalationPriority.URGENT
        },
        "ambiguous_intent": {
            "description": "Unclear user intent with low confidence",
            "priority": EscalationPriority.MEDIUM
        },
        "repeated_blocked": {
            "description": "User repeatedly asking for recommendations",
            "priority": EscalationPriority.LOW
        },
        "sensitive_topic": {
            "description": "Sensitive topics like bankruptcy, foreclosure",
            "priority": EscalationPriority.HIGH
        }
    }
    
    # High-value thresholds
    HIGH_VALUE_THRESHOLD = 100000  # $100,000
    URGENT_VALUE_THRESHOLD = 500000  # $500,000
    
    def __init__(self):
        """Initialize escalation service"""
        pass
    
    async def should_escalate(
        self,
        intent: Intent,
        message: str,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str], Optional[EscalationPriority]]:
        """
        Determine if a query should be escalated to human review
        
        Args:
            intent: Classified intent
            message: User's message
            conversation_context: Optional conversation context
            
        Returns:
            Tuple of (should_escalate, reason, priority)
        """
        # Check if explicitly marked for escalation
        if intent.should_escalate:
            return True, "Explicit escalation flag", EscalationPriority.MEDIUM
        
        # Check for complaints
        if intent.category == IntentCategory.COMPLAINT:
            return True, "complaint", EscalationPriority.HIGH
        
        # Check for unclear intent with low confidence
        if intent.category == IntentCategory.UNCLEAR and intent.confidence < 0.5:
            return True, "ambiguous_intent", EscalationPriority.MEDIUM
        
        # Check for high-value queries
        value = self._extract_monetary_value(message)
        if value:
            if value >= self.URGENT_VALUE_THRESHOLD:
                return True, "high_risk_query", EscalationPriority.URGENT
            elif value >= self.HIGH_VALUE_THRESHOLD:
                return True, "high_risk_query", EscalationPriority.HIGH
        
        # Check for sensitive topics
        if self._contains_sensitive_topic(message):
            return True, "sensitive_topic", EscalationPriority.HIGH
        
        # Check for regulatory/compliance questions
        if self._is_regulatory_question(message):
            return True, "regulatory_question", EscalationPriority.URGENT
        
        # Check conversation context for repeated blocks
        if conversation_context:
            blocked_count = conversation_context.get("blocked_count", 0)
            if blocked_count >= 3:
                return True, "repeated_blocked", EscalationPriority.LOW
        
        return False, None, None
    
    def _extract_monetary_value(self, message: str) -> Optional[float]:
        """Extract monetary value from message"""
        import re
        
        # Patterns for currency amounts
        patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $100,000.00
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars|USD)',  # 100,000 dollars
            r'₹\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # ₹100,000
            r'(\d+)\s*(?:lakh|lakhs)',  # 10 lakhs
            r'(\d+)\s*(?:crore|crores)',  # 1 crore
            r'(\d+)\s*(?:million)',  # 1 million
        ]
        
        message_lower = message.lower()
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    
                    # Convert lakhs/crores to standard amount
                    if 'lakh' in message_lower:
                        value *= 100000
                    elif 'crore' in message_lower:
                        value *= 10000000
                    elif 'million' in message_lower:
                        value *= 1000000
                    
                    return value
                except ValueError:
                    continue
        
        return None
    
    def _contains_sensitive_topic(self, message: str) -> bool:
        """Check if message contains sensitive topics"""
        sensitive_keywords = [
            'bankruptcy', 'foreclosure', 'default', 'debt collection',
            'lawsuit', 'legal action', 'fraud', 'scam', 'complaint',
            'sue', 'lawyer', 'attorney', 'court'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in sensitive_keywords)
    
    def _is_regulatory_question(self, message: str) -> bool:
        """Check if message is about regulations or compliance"""
        regulatory_keywords = [
            'regulation', 'compliance', 'legal requirement', 'law',
            'regulatory', 'fdic', 'sec', 'finra', 'cfpb',
            'consumer protection', 'privacy policy', 'data protection'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in regulatory_keywords)
    
    async def create_escalation(
        self,
        db: AsyncSession,
        conversation_id: str,
        reason: str,
        priority: Optional[EscalationPriority] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Escalation:
        """
        Create an escalation for human review
        
        Args:
            db: Database session
            conversation_id: ID of conversation to escalate
            reason: Reason for escalation
            priority: Priority level (defaults based on reason)
            context: Additional context
            
        Returns:
            Created Escalation object
        """
        # Determine priority if not provided
        if not priority:
            trigger_info = self.ESCALATION_TRIGGERS.get(reason)
            priority = trigger_info["priority"] if trigger_info else EscalationPriority.MEDIUM
        
        # Create escalation
        escalation = Escalation(
            conversation_id=conversation_id,
            reason=reason,
            priority=priority,
            status=EscalationStatus.PENDING,
            escalation_context=context or {}
        )
        
        db.add(escalation)
        await db.commit()
        await db.refresh(escalation)
        
        # TODO: Send notification to human reviewers
        await self._notify_reviewers(escalation)
        
        return escalation
    
    async def _notify_reviewers(self, escalation: Escalation):
        """Send notification to human reviewers (placeholder)"""
        # In production, this would:
        # - Send email to review team
        # - Create Slack/Teams notification
        # - Update dashboard
        # - Trigger webhook
        print(f"[ESCALATION] New escalation created: {escalation.id}")
        print(f"  Priority: {escalation.priority}")
        print(f"  Reason: {escalation.reason}")
        print(f"  Conversation: {escalation.conversation_id}")
    
    async def assign_escalation(
        self,
        db: AsyncSession,
        escalation_id: str,
        assigned_to: str
    ) -> Escalation:
        """Assign escalation to a reviewer"""
        escalation = await db.get(Escalation, escalation_id)
        if not escalation:
            raise ValueError("Escalation not found")
        
        escalation.assigned_to = assigned_to
        escalation.assigned_at = datetime.utcnow()
        escalation.status = EscalationStatus.IN_REVIEW
        
        await db.commit()
        await db.refresh(escalation)
        
        return escalation
    
    async def resolve_escalation(
        self,
        db: AsyncSession,
        escalation_id: str,
        resolution_notes: str,
        resolution_action: str
    ) -> Escalation:
        """Resolve an escalation"""
        escalation = await db.get(Escalation, escalation_id)
        if not escalation:
            raise ValueError("Escalation not found")
        
        escalation.resolution_notes = resolution_notes
        escalation.resolution_action = resolution_action
        escalation.resolved_at = datetime.utcnow()
        escalation.status = EscalationStatus.RESOLVED
        
        await db.commit()
        await db.refresh(escalation)
        
        return escalation
    
    async def get_pending_escalations(
        self,
        db: AsyncSession,
        priority: Optional[EscalationPriority] = None,
        limit: int = 50
    ) -> List[Escalation]:
        """Get pending escalations for review"""
        query = select(Escalation).where(
            Escalation.status == EscalationStatus.PENDING
        )
        
        if priority:
            query = query.where(Escalation.priority == priority)
        
        query = query.order_by(
            Escalation.priority.desc(),
            Escalation.created_at.asc()
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_escalation_stats(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get escalation statistics"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total escalations
        total_result = await db.execute(
            select(func.count(Escalation.id)).where(
                Escalation.created_at >= cutoff_date
            )
        )
        total = total_result.scalar()
        
        # By status
        status_result = await db.execute(
            select(
                Escalation.status,
                func.count(Escalation.id)
            ).where(
                Escalation.created_at >= cutoff_date
            ).group_by(Escalation.status)
        )
        by_status = {row[0].value: row[1] for row in status_result}
        
        # By priority
        priority_result = await db.execute(
            select(
                Escalation.priority,
                func.count(Escalation.id)
            ).where(
                Escalation.created_at >= cutoff_date
            ).group_by(Escalation.priority)
        )
        by_priority = {row[0].value: row[1] for row in priority_result}
        
        # Average resolution time (in hours)
        resolution_time_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', Escalation.resolved_at - Escalation.created_at) / 3600
                )
            ).where(
                and_(
                    Escalation.created_at >= cutoff_date,
                    Escalation.resolved_at.isnot(None)
                )
            )
        )
        avg_resolution_hours = resolution_time_result.scalar() or 0
        
        return {
            "total_escalations": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "period_days": days
        }


# Global escalation service instance
escalation_service = EscalationService()


# Made with Bob - Compliance-First AI Assistant