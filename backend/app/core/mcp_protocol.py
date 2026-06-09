"""
Model Context Protocol (MCP) Implementation
Orchestrates policy enforcement, intent detection, and workflow routing
"""
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

from app.services.intent_service import intent_service, Intent, IntentCategory
from app.core.compliance_responses import (
    ComplianceResponseTemplates,
    contains_advisory_language,
    sanitize_response
)


class WorkflowRoute(str, Enum):
    """Workflow routing decisions"""
    RAG_RETRIEVAL = "rag_retrieval"  # Use RAG for factual information
    BLOCKED_INTENT = "blocked_intent"  # Block and provide template response
    ESCALATE_HUMAN = "escalate_human"  # Escalate to human reviewer
    CREATE_TICKET = "create_ticket"  # Create support ticket
    CALCULATOR = "calculator"  # Route to calculator
    STANDARD_CHAT = "standard_chat"  # Standard AI chat (allowed intent)


class PolicyCheckResult:
    """Result of policy enforcement check"""
    
    def __init__(
        self,
        is_compliant: bool,
        violations: list[str],
        corrected_response: Optional[str] = None,
        severity: str = "low"
    ):
        self.is_compliant = is_compliant
        self.violations = violations
        self.corrected_response = corrected_response
        self.severity = severity
        self.checked_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "is_compliant": self.is_compliant,
            "violations": self.violations,
            "corrected_response": self.corrected_response,
            "severity": self.severity,
            "checked_at": self.checked_at.isoformat()
        }


class MCPProtocol:
    """
    Model Context Protocol - Orchestrates compliance-first AI interactions
    
    This is the central coordinator that ensures all AI interactions
    comply with non-advisory policies.
    """
    
    def __init__(self):
        """Initialize MCP protocol"""
        self.intent_service = intent_service
        self.response_templates = ComplianceResponseTemplates()
    
    async def validate_intent(
        self,
        user_message: str,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Intent, WorkflowRoute]:
        """
        Validate user intent and determine workflow routing
        
        Args:
            user_message: The user's message
            conversation_context: Optional conversation context
            
        Returns:
            Tuple of (Intent, WorkflowRoute)
        """
        # Classify intent
        intent = await self.intent_service.classify_intent(user_message, conversation_context)
        
        # Determine workflow route based on intent
        route = self._determine_workflow_route(intent, user_message)
        
        return intent, route
    
    def _determine_workflow_route(self, intent: Intent, message: str) -> WorkflowRoute:
        """
        Determine which workflow to route the request to
        
        Args:
            intent: Classified intent
            message: Original message
            
        Returns:
            WorkflowRoute decision
        """
        # Check if should block (recommendation/advice request)
        if self.intent_service.should_block(intent):
            return WorkflowRoute.BLOCKED_INTENT
        
        # Check if should escalate to human
        if self.intent_service.should_escalate(intent, message):
            return WorkflowRoute.ESCALATE_HUMAN
        
        # Route based on intent category
        if intent.category == IntentCategory.PRODUCT_COMPARISON:
            return WorkflowRoute.RAG_RETRIEVAL
        
        if intent.category == IntentCategory.CALCULATION_REQUEST:
            return WorkflowRoute.CALCULATOR
        
        if intent.category in [
            IntentCategory.PRODUCT_INFORMATION,
            IntentCategory.POLICY_EXPLANATION,
            IntentCategory.ELIGIBILITY_CHECK,
            IntentCategory.TERMS_CONDITIONS
        ]:
            return WorkflowRoute.RAG_RETRIEVAL
        
        if intent.category == IntentCategory.COMPLAINT:
            return WorkflowRoute.CREATE_TICKET
        
        # Default to standard chat for general inquiries
        return WorkflowRoute.STANDARD_CHAT
    
    def enforce_policy(self, response: str, intent: Optional[Intent] = None) -> PolicyCheckResult:
        """
        Enforce policy on AI-generated response
        
        Args:
            response: The AI-generated response
            intent: Optional intent classification
            
        Returns:
            PolicyCheckResult with compliance status
        """
        violations = []
        
        # Check for advisory language
        if contains_advisory_language(response):
            violations.append("Contains advisory language")
        
        # Check for recommendation phrases
        recommendation_phrases = [
            "i recommend",
            "you should buy",
            "best option for you",
            "perfect for your situation",
            "ideal choice"
        ]
        
        response_lower = response.lower()
        for phrase in recommendation_phrases:
            if phrase in response_lower:
                violations.append(f"Contains recommendation phrase: '{phrase}'")
        
        # Determine severity
        severity = "high" if len(violations) > 2 else "medium" if violations else "low"
        
        # If violations found, sanitize response
        if violations:
            corrected = sanitize_response(response)
            # Add disclaimer
            corrected = self.response_templates.format_response_with_disclaimer(
                corrected,
                "general"
            )
            
            return PolicyCheckResult(
                is_compliant=False,
                violations=violations,
                corrected_response=corrected,
                severity=severity
            )
        
        # Response is compliant
        return PolicyCheckResult(
            is_compliant=True,
            violations=[],
            corrected_response=None,
            severity="low"
        )
    
    def get_blocked_response(self, intent: Intent) -> str:
        """
        Get appropriate response for blocked intent
        
        Args:
            intent: The blocked intent
            
        Returns:
            Compliance-safe response
        """
        blocked_type = self.intent_service.get_blocked_intent_type(intent)
        return self.response_templates.build_blocked_response_with_alternatives(
            blocked_type,
            include_alternatives=True
        )
    
    def get_escalation_response(self, reason: str = "complex_query") -> str:
        """
        Get appropriate response for escalated queries
        
        Args:
            reason: Reason for escalation
            
        Returns:
            Escalation message
        """
        return self.response_templates.get_escalation_message(reason)
    
    async def process_message(
        self,
        user_message: str,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point - process user message through MCP
        
        Args:
            user_message: User's message
            conversation_context: Optional conversation context
            
        Returns:
            Dictionary with processing results and routing decision
        """
        # Step 1: Validate intent
        intent, route = await self.validate_intent(user_message, conversation_context)
        
        # Step 2: Prepare response based on route
        result = {
            "intent": intent.to_dict(),
            "route": route.value,
            "should_block": self.intent_service.should_block(intent),
            "should_escalate": self.intent_service.should_escalate(intent, user_message),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Step 3: Add route-specific information
        if route == WorkflowRoute.BLOCKED_INTENT:
            result["blocked_response"] = self.get_blocked_response(intent)
            result["requires_human"] = False
            
        elif route == WorkflowRoute.ESCALATE_HUMAN:
            result["escalation_response"] = self.get_escalation_response()
            result["requires_human"] = True
            result["escalation_reason"] = intent.reasoning
            
        elif route == WorkflowRoute.CREATE_TICKET:
            result["requires_ticket"] = True
            result["ticket_type"] = "complaint" if intent.category == IntentCategory.COMPLAINT else "inquiry"
            
        elif route == WorkflowRoute.RAG_RETRIEVAL:
            result["use_rag"] = True
            result["retrieval_context"] = intent.category.value
            
        elif route == WorkflowRoute.CALCULATOR:
            result["use_calculator"] = True
            result["calculator_type"] = self._detect_calculator_type(user_message)
        
        return result
    
    def _detect_calculator_type(self, message: str) -> str:
        """Detect which calculator is needed"""
        message_lower = message.lower()
        
        if "retirement" in message_lower:
            return "retirement"
        elif "loan" in message_lower or "emi" in message_lower:
            return "loan"
        elif "investment" in message_lower:
            return "investment"
        elif "insurance" in message_lower or "coverage" in message_lower:
            return "insurance"
        else:
            return "general"
    
    def validate_response_before_send(
        self,
        response: str,
        intent: Optional[Intent] = None
    ) -> Tuple[bool, str]:
        """
        Final validation before sending response to user
        
        Args:
            response: The response to validate
            intent: Optional intent classification
            
        Returns:
            Tuple of (is_safe_to_send, final_response)
        """
        # Enforce policy
        policy_check = self.enforce_policy(response, intent)
        
        if not policy_check.is_compliant:
            # Use corrected response or fallback
            corrected = policy_check.corrected_response or response
            return True, corrected
        
        # Add disclaimer to all responses
        final_response = self.response_templates.format_response_with_disclaimer(
            response,
            "general"
        )
        
        return True, final_response
    
    def log_interaction(
        self,
        user_message: str,
        intent: Intent,
        route: WorkflowRoute,
        response: str,
        policy_check: PolicyCheckResult
    ) -> Dict[str, Any]:
        """
        Create log entry for compliance audit
        
        Args:
            user_message: User's message
            intent: Classified intent
            route: Workflow route taken
            response: Final response
            policy_check: Policy check result
            
        Returns:
            Log entry dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "intent": intent.to_dict(),
            "route": route.value,
            "response": response,
            "policy_check": policy_check.to_dict(),
            "was_blocked": intent.should_block,
            "was_escalated": intent.should_escalate
        }


# Global MCP protocol instance
mcp_protocol = MCPProtocol()


# Made with Bob - Compliance-First AI Assistant