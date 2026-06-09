"""
Ticket Service
Automated support ticket creation and tracking
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.escalation import SupportTicket, TicketPriority, TicketStatus
from app.models.conversation import Conversation
from app.services.intent_service import Intent, IntentCategory


class TicketService:
    """Service for managing support tickets"""
    
    # Issue type mappings
    ISSUE_TYPES = {
        "complaint": "Customer Complaint",
        "inquiry": "General Inquiry",
        "technical": "Technical Issue",
        "account": "Account Issue",
        "product": "Product Question",
        "billing": "Billing Issue",
        "feedback": "Customer Feedback",
        "other": "Other"
    }
    
    def __init__(self):
        """Initialize ticket service"""
        pass
    
    async def auto_detect_ticket_need(
        self,
        intent: Intent,
        message: str,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Detect if conversation needs ticket creation
        
        Args:
            intent: Classified intent
            message: User's message
            conversation_context: Optional conversation context
            
        Returns:
            Tuple of (needs_ticket, issue_type)
        """
        # Complaints always need tickets
        if intent.category == IntentCategory.COMPLAINT:
            return True, "complaint"
        
        # Check for unresolved issues
        if self._indicates_unresolved_issue(message):
            return True, "inquiry"
        
        # Check for frustration indicators
        if self._indicates_frustration(message):
            return True, "feedback"
        
        # Check for follow-up requests
        if self._requests_follow_up(message):
            return True, "inquiry"
        
        # Check conversation context
        if conversation_context:
            # Multiple blocked intents might need human follow-up
            blocked_count = conversation_context.get("blocked_count", 0)
            if blocked_count >= 5:
                return True, "inquiry"
            
            # Long conversations without resolution
            message_count = conversation_context.get("message_count", 0)
            if message_count >= 20:
                return True, "inquiry"
        
        return False, None
    
    def _indicates_unresolved_issue(self, message: str) -> bool:
        """Check if message indicates an unresolved issue"""
        unresolved_keywords = [
            "still not working", "still have problem", "not resolved",
            "still waiting", "no response", "no answer", "not helping",
            "doesn't work", "can't access", "unable to"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in unresolved_keywords)
    
    def _indicates_frustration(self, message: str) -> bool:
        """Check if message indicates user frustration"""
        frustration_keywords = [
            "frustrated", "annoyed", "disappointed", "unhappy",
            "terrible", "awful", "horrible", "useless", "waste of time",
            "not satisfied", "poor service", "bad experience"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in frustration_keywords)
    
    def _requests_follow_up(self, message: str) -> bool:
        """Check if message requests follow-up"""
        follow_up_keywords = [
            "call me", "contact me", "get back to me", "follow up",
            "speak to someone", "talk to agent", "human help",
            "need assistance", "need help", "can someone"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in follow_up_keywords)
    
    async def create_ticket(
        self,
        db: AsyncSession,
        user_id: Optional[str],
        conversation_id: Optional[str],
        issue_type: str,
        subject: str,
        description: str,
        priority: Optional[TicketPriority] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SupportTicket:
        """
        Create a support ticket
        
        Args:
            db: Database session
            user_id: User ID (optional for anonymous)
            conversation_id: Conversation ID (optional)
            issue_type: Type of issue
            subject: Ticket subject
            description: Detailed description
            priority: Priority level
            metadata: Additional metadata
            
        Returns:
            Created SupportTicket object
        """
        # Generate unique ticket number
        ticket_number = SupportTicket.generate_ticket_number()
        
        # Determine priority if not provided
        if not priority:
            priority = self._determine_priority(issue_type, description)
        
        # Create ticket
        ticket = SupportTicket(
            ticket_number=ticket_number,
            user_id=user_id,
            conversation_id=conversation_id,
            issue_type=issue_type,
            subject=subject,
            description=description,
            priority=priority,
            status=TicketStatus.OPEN,
            ticket_metadata=metadata or {}
        )
        
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        
        # Send notification to support team
        await self._notify_support_team(ticket)
        
        return ticket
    
    def _determine_priority(self, issue_type: str, description: str) -> TicketPriority:
        """Determine ticket priority based on issue type and description"""
        # High priority issue types
        if issue_type in ["complaint", "account", "billing"]:
            return TicketPriority.HIGH
        
        # Check for urgent keywords in description
        urgent_keywords = ["urgent", "emergency", "critical", "immediately", "asap"]
        if any(keyword in description.lower() for keyword in urgent_keywords):
            return TicketPriority.URGENT
        
        # Default to medium
        return TicketPriority.MEDIUM
    
    async def _notify_support_team(self, ticket: SupportTicket):
        """Send notification to support team (placeholder)"""
        # In production, this would:
        # - Send email to support team
        # - Create notification in support dashboard
        # - Trigger webhook to ticketing system
        # - Send SMS for urgent tickets
        print(f"[TICKET] New support ticket created: {ticket.ticket_number}")
        print(f"  Priority: {ticket.priority}")
        print(f"  Issue Type: {ticket.issue_type}")
        print(f"  Subject: {ticket.subject}")
    
    async def update_ticket_status(
        self,
        db: AsyncSession,
        ticket_id: str,
        status: TicketStatus,
        resolution: Optional[str] = None
    ) -> SupportTicket:
        """Update ticket status"""
        ticket = await db.get(SupportTicket, ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        old_status = ticket.status
        ticket.status = status  # type: ignore
        
        # Calculate resolution time if resolving
        if status == TicketStatus.RESOLVED and old_status != TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()  # type: ignore
            if ticket.created_at:
                time_diff = datetime.utcnow() - ticket.created_at
                ticket.resolution_time_minutes = int(time_diff.total_seconds() / 60)  # type: ignore
            
            if resolution:
                ticket.resolution = resolution  # type: ignore
        
        # Set closed timestamp
        if status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.utcnow()  # type: ignore
        
        await db.commit()
        await db.refresh(ticket)
        
        return ticket
    
    async def assign_ticket(
        self,
        db: AsyncSession,
        ticket_id: str,
        assigned_to: str,
        department: Optional[str] = None
    ) -> SupportTicket:
        """Assign ticket to a support agent"""
        ticket = await db.get(SupportTicket, ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.assigned_to = assigned_to  # type: ignore
        ticket.assigned_at = datetime.utcnow()  # type: ignore
        ticket.status = TicketStatus.IN_PROGRESS  # type: ignore
        
        if department:
            ticket.department = department  # type: ignore
        
        await db.commit()
        await db.refresh(ticket)
        
        return ticket
    
    async def get_user_tickets(
        self,
        db: AsyncSession,
        user_id: str,
        status: Optional[TicketStatus] = None,
        limit: int = 50
    ) -> List[SupportTicket]:
        """Get tickets for a specific user"""
        query = select(SupportTicket).where(
            SupportTicket.user_id == user_id
        )
        
        if status:
            query = query.where(SupportTicket.status == status)
        
        query = query.order_by(SupportTicket.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_open_tickets(
        self,
        db: AsyncSession,
        department: Optional[str] = None,
        priority: Optional[TicketPriority] = None,
        limit: int = 100
    ) -> List[SupportTicket]:
        """Get open tickets for support team"""
        query = select(SupportTicket).where(
            SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        )
        
        if department:
            query = query.where(SupportTicket.department == department)
        
        if priority:
            query = query.where(SupportTicket.priority == priority)
        
        query = query.order_by(
            SupportTicket.priority.desc(),
            SupportTicket.created_at.asc()
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_ticket_stats(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get ticket statistics"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total tickets
        total_result = await db.execute(
            select(func.count(SupportTicket.id)).where(
                SupportTicket.created_at >= cutoff_date
            )
        )
        total = total_result.scalar()
        
        # By status
        status_result = await db.execute(
            select(
                SupportTicket.status,
                func.count(SupportTicket.id)
            ).where(
                SupportTicket.created_at >= cutoff_date
            ).group_by(SupportTicket.status)
        )
        by_status = {row[0].value: row[1] for row in status_result}
        
        # By priority
        priority_result = await db.execute(
            select(
                SupportTicket.priority,
                func.count(SupportTicket.id)
            ).where(
                SupportTicket.created_at >= cutoff_date
            ).group_by(SupportTicket.priority)
        )
        by_priority = {row[0].value: row[1] for row in priority_result}
        
        # By issue type
        issue_result = await db.execute(
            select(
                SupportTicket.issue_type,
                func.count(SupportTicket.id)
            ).where(
                SupportTicket.created_at >= cutoff_date
            ).group_by(SupportTicket.issue_type)
        )
        by_issue_type = {row[0]: row[1] for row in issue_result}
        
        # Average resolution time (in minutes)
        resolution_time_result = await db.execute(
            select(
                func.avg(SupportTicket.resolution_time_minutes)
            ).where(
                and_(
                    SupportTicket.created_at >= cutoff_date,
                    SupportTicket.resolution_time_minutes.isnot(None)
                )
            )
        )
        avg_resolution_minutes = resolution_time_result.scalar() or 0
        
        # Resolution rate
        resolved_result = await db.execute(
            select(func.count(SupportTicket.id)).where(
                and_(
                    SupportTicket.created_at >= cutoff_date,
                    SupportTicket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED])
                )
            )
        )
        resolved_count = resolved_result.scalar() or 0
        resolution_rate = (resolved_count / total * 100) if total and total > 0 else 0
        
        return {
            "total_tickets": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_issue_type": by_issue_type,
            "avg_resolution_minutes": round(avg_resolution_minutes, 2),
            "resolution_rate_percent": round(resolution_rate, 2),
            "period_days": days
        }
    
    async def add_ticket_note(
        self,
        db: AsyncSession,
        ticket_id: str,
        note: str,
        added_by: str
    ) -> SupportTicket:
        """Add a note to a ticket"""
        ticket = await db.get(SupportTicket, ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Add note to metadata
        metadata = ticket.ticket_metadata or {}
        if "notes" not in metadata:
            metadata["notes"] = []
        
        metadata["notes"].append({
            "note": note,
            "added_by": added_by,
            "added_at": datetime.utcnow().isoformat()
        })
        
        ticket.ticket_metadata = metadata  # type: ignore
        
        await db.commit()
        await db.refresh(ticket)
        
        return ticket


# Global ticket service instance
ticket_service = TicketService()


# Made with Bob - Compliance-First AI Assistant