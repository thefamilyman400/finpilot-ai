"""
Intent Detection Service
Classifies user intent and detects recommendation requests for compliance
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import re
import httpx
from datetime import datetime

from app.core.compliance_responses import (
    BlockedIntentType,
    ADVISORY_KEYWORDS,
    BLOCKED_PHRASES
)
from config import settings


class IntentCategory(str, Enum):
    """Categories of user intent"""
    # Allowed intents
    PRODUCT_INFORMATION = "product_information"
    POLICY_EXPLANATION = "policy_explanation"
    PRODUCT_COMPARISON = "product_comparison"
    CALCULATION_REQUEST = "calculation_request"
    GENERAL_INQUIRY = "general_inquiry"
    ELIGIBILITY_CHECK = "eligibility_check"
    TERMS_CONDITIONS = "terms_conditions"
    
    # Blocked intents (require non-advisory response)
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PURCHASE_ADVICE = "purchase_advice"
    PERSONALIZED_SUGGESTION = "personalized_suggestion"
    INVESTMENT_ADVICE = "investment_advice"
    BEST_OPTION = "best_option"
    SHOULD_I_BUY = "should_i_buy"
    
    # Special handling
    COMPLAINT = "complaint"
    ESCALATION_NEEDED = "escalation_needed"
    UNCLEAR = "unclear"


class Intent:
    """Represents a classified user intent"""
    
    def __init__(
        self,
        category: IntentCategory,
        confidence: float,
        reasoning: str,
        entities: Optional[Dict[str, Any]] = None,
        should_block: bool = False,
        should_escalate: bool = False
    ):
        self.category = category
        self.confidence = confidence
        self.reasoning = reasoning
        self.entities = entities or {}
        self.should_block = should_block
        self.should_escalate = should_escalate
        self.detected_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "entities": self.entities,
            "should_block": self.should_block,
            "should_escalate": self.should_escalate,
            "detected_at": self.detected_at.isoformat()
        }


class IntentDetectionService:
    """Service for detecting and classifying user intent"""
    
    # Blocked intent categories
    BLOCKED_INTENTS = {
        IntentCategory.PRODUCT_RECOMMENDATION,
        IntentCategory.PURCHASE_ADVICE,
        IntentCategory.PERSONALIZED_SUGGESTION,
        IntentCategory.INVESTMENT_ADVICE,
        IntentCategory.BEST_OPTION,
        IntentCategory.SHOULD_I_BUY
    }
    
    # Allowed intent categories
    ALLOWED_INTENTS = {
        IntentCategory.PRODUCT_INFORMATION,
        IntentCategory.POLICY_EXPLANATION,
        IntentCategory.PRODUCT_COMPARISON,
        IntentCategory.CALCULATION_REQUEST,
        IntentCategory.GENERAL_INQUIRY,
        IntentCategory.ELIGIBILITY_CHECK,
        IntentCategory.TERMS_CONDITIONS
    }
    
    # Keyword patterns for quick detection
    INTENT_PATTERNS = {
        IntentCategory.PRODUCT_RECOMMENDATION: [
            r"recommend.*product",
            r"which.*should.*i.*choose",
            r"what.*should.*i.*buy",
            r"suggest.*product",
            r"best.*for.*me"
        ],
        IntentCategory.PRODUCT_COMPARISON: [
            r"compare.*products?",
            r"difference.*between",
            r"vs\.|versus",
            r"which.*is.*better",
            r"comparison.*of"
        ],
        IntentCategory.CALCULATION_REQUEST: [
            r"calculate",
            r"how.*much.*would",
            r"estimate",
            r"calculator",
            r"compute"
        ],
        IntentCategory.PRODUCT_INFORMATION: [
            r"what.*is",
            r"tell.*me.*about",
            r"explain",
            r"information.*about",
            r"details.*of"
        ],
        IntentCategory.ELIGIBILITY_CHECK: [
            r"am.*i.*eligible",
            r"qualify.*for",
            r"requirements.*for",
            r"can.*i.*apply"
        ]
    }
    
    def __init__(self):
        """Initialize intent detection service"""
        self.api_key = settings.GOOGLE_API_KEY
        self.model = settings.GOOGLE_GEMINI_MODEL or "gemini-pro"
    
    async def classify_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """
        Classify user intent using multiple methods
        
        Args:
            message: User's message
            context: Optional conversation context
            
        Returns:
            Intent object with classification results
        """
        # First, try rule-based detection (fast)
        rule_based_intent = self._rule_based_classification(message)
        
        # If high confidence from rules, use it
        if rule_based_intent.confidence > 0.8:
            return rule_based_intent
        
        # Otherwise, use LLM for more nuanced detection
        try:
            llm_intent = await self._llm_based_classification(message, context)
            return llm_intent
        except Exception as e:
            print(f"LLM classification failed: {e}, falling back to rule-based")
            return rule_based_intent
    
    def _rule_based_classification(self, message: str) -> Intent:
        """
        Fast rule-based intent classification using patterns
        
        Args:
            message: User's message
            
        Returns:
            Intent object
        """
        message_lower = message.lower()
        
        # Check for blocked phrases first (highest priority)
        for phrase in BLOCKED_PHRASES:
            if phrase in message_lower:
                return Intent(
                    category=IntentCategory.PRODUCT_RECOMMENDATION,
                    confidence=0.95,
                    reasoning=f"Detected blocked phrase: '{phrase}'",
                    should_block=True
                )
        
        # Check for advisory keywords
        for keyword in ADVISORY_KEYWORDS:
            if keyword in message_lower:
                return Intent(
                    category=IntentCategory.PRODUCT_RECOMMENDATION,
                    confidence=0.85,
                    reasoning=f"Detected advisory keyword: '{keyword}'",
                    should_block=True
                )
        
        # Check pattern matches
        best_match = None
        best_confidence = 0.0
        
        for intent_category, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    confidence = 0.75  # Pattern match confidence
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_category
        
        if best_match:
            should_block = best_match in self.BLOCKED_INTENTS
            return Intent(
                category=best_match,
                confidence=best_confidence,
                reasoning=f"Pattern match for {best_match.value}",
                should_block=should_block
            )
        
        # Default to general inquiry
        return Intent(
            category=IntentCategory.GENERAL_INQUIRY,
            confidence=0.5,
            reasoning="No specific pattern matched, defaulting to general inquiry",
            should_block=False
        )
    
    async def _llm_based_classification(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Use LLM for nuanced intent classification
        
        Args:
            message: User's message
            context: Optional conversation context
            
        Returns:
            Intent object
        """
        # Build classification prompt
        prompt = self._build_classification_prompt(message, context)
        
        # Call Gemini API
        api_version = "v1beta" if "exp" in self.model or "2.0" in self.model else "v1"
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{self.model}:generateContent?key={self.api_key}"
        
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for consistent classification
                "maxOutputTokens": 500
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
        
        # Parse response
        text = ""
        if isinstance(data, dict):
            candidates = data.get('candidates', [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts and len(parts) > 0:
                    text = parts[0].get('text', '')
        
        # Parse classification result
        return self._parse_llm_response(text, message)
    
    def _build_classification_prompt(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for LLM-based classification"""
        return f"""You are an intent classifier for a banking/insurance chatbot. Your job is to classify user intent and detect if they are asking for financial advice or recommendations.

CRITICAL: We MUST NOT provide financial advice or product recommendations. Detect these intents carefully.

BLOCKED INTENTS (require non-advisory response):
- product_recommendation: User asking which product to choose
- purchase_advice: User asking if they should buy something
- personalized_suggestion: User asking for personalized recommendations
- investment_advice: User asking for investment guidance
- best_option: User asking what's best for them
- should_i_buy: User asking if they should purchase

ALLOWED INTENTS (can provide factual information):
- product_information: User asking about product features
- policy_explanation: User asking about policies
- product_comparison: User asking to compare products objectively
- calculation_request: User asking for calculations
- general_inquiry: General questions
- eligibility_check: Asking about eligibility
- terms_conditions: Asking about terms

User Message: "{message}"

Classify this message. Respond in this exact format:
INTENT: <intent_category>
CONFIDENCE: <0.0-1.0>
SHOULD_BLOCK: <true/false>
REASONING: <brief explanation>

Example:
INTENT: product_recommendation
CONFIDENCE: 0.95
SHOULD_BLOCK: true
REASONING: User is asking which product they should choose, which requires advice.
"""
    
    def _parse_llm_response(self, response: str, original_message: str) -> Intent:
        """Parse LLM classification response"""
        try:
            lines = response.strip().split('\n')
            intent_str = ""
            confidence = 0.7
            should_block = False
            reasoning = "LLM classification"
            
            for line in lines:
                if line.startswith("INTENT:"):
                    intent_str = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence = float(line.split(":", 1)[1].strip())
                elif line.startswith("SHOULD_BLOCK:"):
                    should_block = line.split(":", 1)[1].strip().lower() == "true"
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            # Map string to enum
            try:
                category = IntentCategory(intent_str)
            except ValueError:
                # Fallback to general inquiry if unknown category
                category = IntentCategory.GENERAL_INQUIRY
            
            return Intent(
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                should_block=should_block or (category in self.BLOCKED_INTENTS)
            )
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Fallback to rule-based
            return self._rule_based_classification(original_message)
    
    def should_block(self, intent: Intent) -> bool:
        """
        Determine if an intent should be blocked
        
        Args:
            intent: The classified intent
            
        Returns:
            True if intent should be blocked
        """
        return intent.should_block or intent.category in self.BLOCKED_INTENTS
    
    def should_escalate(self, intent: Intent, message: str) -> bool:
        """
        Determine if an intent should be escalated to human
        
        Args:
            intent: The classified intent
            message: Original message
            
        Returns:
            True if should escalate
        """
        # Escalate if explicitly marked
        if intent.should_escalate:
            return True
        
        # Escalate complaints
        if intent.category == IntentCategory.COMPLAINT:
            return True
        
        # Escalate if unclear with low confidence
        if intent.category == IntentCategory.UNCLEAR and intent.confidence < 0.5:
            return True
        
        # Escalate if message mentions large amounts
        if self._contains_high_value(message):
            return True
        
        return False
    
    def _contains_high_value(self, message: str) -> bool:
        """Check if message mentions high monetary values"""
        # Look for large numbers with currency symbols or words
        patterns = [
            r'\$\s*\d{6,}',  # $100000 or more
            r'₹\s*\d{7,}',   # ₹1000000 or more (10 lakhs)
            r'\d+\s*(lakh|crore|million)',
            r'(hundred|several)\s*thousand'
        ]
        
        message_lower = message.lower()
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def get_blocked_intent_type(self, intent: Intent) -> BlockedIntentType:
        """
        Map intent category to blocked intent type for response templates
        
        Args:
            intent: The classified intent
            
        Returns:
            BlockedIntentType for response template
        """
        mapping = {
            IntentCategory.PRODUCT_RECOMMENDATION: BlockedIntentType.RECOMMENDATION_REQUEST,
            IntentCategory.PURCHASE_ADVICE: BlockedIntentType.PURCHASE_ADVICE,
            IntentCategory.PERSONALIZED_SUGGESTION: BlockedIntentType.PERSONALIZED_SUGGESTION,
            IntentCategory.INVESTMENT_ADVICE: BlockedIntentType.INVESTMENT_ADVICE,
            IntentCategory.BEST_OPTION: BlockedIntentType.BEST_OPTION,
            IntentCategory.SHOULD_I_BUY: BlockedIntentType.SHOULD_I_BUY
        }
        
        return mapping.get(intent.category, BlockedIntentType.RECOMMENDATION_REQUEST)


# Global intent detection service instance
intent_service = IntentDetectionService()


# Made with Bob - Compliance-First AI Assistant