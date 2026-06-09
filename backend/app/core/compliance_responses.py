"""
Compliance Response Templates
Provides standardized responses for blocked intents and policy violations
"""
from typing import Dict, List
from enum import Enum


class BlockedIntentType(str, Enum):
    """Types of blocked intents"""
    RECOMMENDATION_REQUEST = "recommendation_request"
    PURCHASE_ADVICE = "purchase_advice"
    PERSONALIZED_SUGGESTION = "personalized_suggestion"
    INVESTMENT_ADVICE = "investment_advice"
    BEST_OPTION = "best_option"
    SHOULD_I_BUY = "should_i_buy"


class ComplianceResponseTemplates:
    """Standardized compliance-safe response templates"""
    
    # Main blocked response templates
    BLOCKED_RESPONSES: Dict[BlockedIntentType, str] = {
        BlockedIntentType.RECOMMENDATION_REQUEST: """
I cannot recommend specific products or provide personalized financial advice. 
However, I can help you compare products objectively based on their features.

Would you like me to:
1. Compare specific products side-by-side
2. Explain product features and terms
3. Connect you with a licensed advisor
""",
        
        BlockedIntentType.PURCHASE_ADVICE: """
I'm not able to advise on purchases or suggest what's best for your situation.
I can provide factual information about our products to help you make an informed decision.

What specific product information can I help you with?
""",
        
        BlockedIntentType.PERSONALIZED_SUGGESTION: """
I cannot provide personalized suggestions or recommendations. 

I can help you by:
- Explaining product features objectively
- Comparing multiple products side-by-side
- Providing factual information about eligibility criteria
- Connecting you with a licensed financial advisor

How would you like to proceed?
""",
        
        BlockedIntentType.INVESTMENT_ADVICE: """
I cannot provide investment advice or recommend specific investment products.

I can offer:
- Factual information about investment product features
- Objective comparisons between products
- General information about investment types
- Contact information for licensed investment advisors

What information would be helpful?
""",
        
        BlockedIntentType.BEST_OPTION: """
I cannot determine which option is "best" for you, as that would constitute financial advice.

Instead, I can:
- Show you an objective comparison of available options
- Explain the features and terms of each option
- Help you understand eligibility requirements
- Connect you with an advisor for personalized guidance

Would any of these be helpful?
""",
        
        BlockedIntentType.SHOULD_I_BUY: """
I cannot advise whether you should purchase a specific product.

I can help by:
- Providing factual information about the product
- Explaining terms, conditions, and fees
- Comparing it with similar products
- Connecting you with a licensed advisor for personalized guidance

What would you like to know about our products?
"""
    }
    
    # Disclaimer templates
    GENERAL_DISCLAIMER = """
**Important:** This information is for educational purposes only and does not constitute financial advice. 
Please consult with a licensed financial advisor for personalized recommendations.
"""
    
    COMPARISON_DISCLAIMER = """
**Disclaimer:** This is an objective comparison based on product features. It does not constitute 
a recommendation. Your individual circumstances should be considered when making financial decisions.
"""
    
    CALCULATOR_DISCLAIMER = """
**Important Notice:** These calculations are estimates for informational purposes only. 
Actual results may vary based on individual circumstances, market conditions, and other factors. 
This does not constitute financial advice. Consult a licensed financial advisor for personalized guidance.
"""
    
    # Escalation messages
    ESCALATION_MESSAGES = {
        "complex_query": """
This appears to be a complex financial question that would benefit from personalized guidance. 
I've created a ticket for our financial advisors to contact you. They can provide the detailed 
assistance you need.

Would you like me to help with anything else in the meantime?
""",
        
        "high_value": """
For financial decisions involving significant amounts, I recommend speaking with one of our 
licensed financial advisors who can provide personalized guidance based on your specific situation.

I've created a request for an advisor to contact you. Is there any general information I can 
provide while you wait?
""",
        
        "regulatory": """
This question involves regulatory or compliance matters that require expert guidance. 
I've escalated your inquiry to our compliance team who will provide accurate information.

Can I help you with any general product information in the meantime?
"""
    }
    
    # Alternative action suggestions
    ALTERNATIVE_ACTIONS: Dict[str, List[str]] = {
        "product_info": [
            "View detailed product information",
            "Compare products side-by-side",
            "Check eligibility requirements",
            "Review terms and conditions"
        ],
        
        "calculations": [
            "Use our retirement calculator",
            "Calculate loan payments",
            "Estimate insurance coverage needs",
            "Project investment growth (informational only)"
        ],
        
        "human_contact": [
            "Schedule a call with an advisor",
            "Request a callback",
            "Visit a branch location",
            "Chat with a licensed representative"
        ],
        
        "self_service": [
            "Browse our FAQ section",
            "Read product guides",
            "Watch educational videos",
            "Download product brochures"
        ]
    }
    
    @classmethod
    def get_blocked_response(cls, intent_type: BlockedIntentType) -> str:
        """Get the appropriate response for a blocked intent"""
        return cls.BLOCKED_RESPONSES.get(
            intent_type,
            cls.BLOCKED_RESPONSES[BlockedIntentType.RECOMMENDATION_REQUEST]
        )
    
    @classmethod
    def get_escalation_message(cls, escalation_type: str) -> str:
        """Get the appropriate escalation message"""
        return cls.ESCALATION_MESSAGES.get(
            escalation_type,
            cls.ESCALATION_MESSAGES["complex_query"]
        )
    
    @classmethod
    def format_response_with_disclaimer(cls, response: str, disclaimer_type: str = "general") -> str:
        """Add appropriate disclaimer to a response"""
        disclaimers = {
            "general": cls.GENERAL_DISCLAIMER,
            "comparison": cls.COMPARISON_DISCLAIMER,
            "calculator": cls.CALCULATOR_DISCLAIMER
        }
        
        disclaimer = disclaimers.get(disclaimer_type, cls.GENERAL_DISCLAIMER)
        return f"{response}\n\n{disclaimer}"
    
    @classmethod
    def get_alternative_actions(cls, category: str) -> List[str]:
        """Get list of alternative actions for a category"""
        return cls.ALTERNATIVE_ACTIONS.get(category, cls.ALTERNATIVE_ACTIONS["product_info"])
    
    @classmethod
    def build_blocked_response_with_alternatives(
        cls,
        intent_type: BlockedIntentType,
        include_alternatives: bool = True
    ) -> str:
        """Build a complete blocked response with alternative actions"""
        response = cls.get_blocked_response(intent_type)
        
        if include_alternatives:
            # Add relevant alternative actions
            alternatives = []
            alternatives.extend(cls.get_alternative_actions("product_info")[:2])
            alternatives.extend(cls.get_alternative_actions("human_contact")[:1])
            
            alternatives_text = "\n\n**You can also:**\n" + "\n".join(
                f"- {action}" for action in alternatives
            )
            response += alternatives_text
        
        return response


# Compliance keywords for detection
ADVISORY_KEYWORDS = [
    "recommend", "suggest", "advise", "should buy", "best for you",
    "you should", "i recommend", "my recommendation", "go with",
    "pick this", "choose this", "this is better", "ideal for you",
    "perfect for", "right choice", "smart move", "good idea to buy"
]

BLOCKED_PHRASES = [
    "you should buy",
    "i recommend buying",
    "best option for you",
    "perfect for your situation",
    "ideal choice",
    "you need this",
    "this is what you should do",
    "go ahead and purchase",
    "definitely get this"
]


def contains_advisory_language(text: str) -> bool:
    """
    Check if text contains advisory language that violates compliance
    
    Args:
        text: The text to check
        
    Returns:
        True if advisory language is detected
    """
    text_lower = text.lower()
    
    # Check for blocked phrases (exact matches)
    for phrase in BLOCKED_PHRASES:
        if phrase in text_lower:
            return True
    
    # Check for advisory keywords
    for keyword in ADVISORY_KEYWORDS:
        if keyword in text_lower:
            return True
    
    return False


def sanitize_response(response: str) -> str:
    """
    Remove or replace advisory language from a response
    
    Args:
        response: The response to sanitize
        
    Returns:
        Sanitized response
    """
    # This is a simple implementation - in production, use more sophisticated NLP
    sanitized = response
    
    replacements = {
        "i recommend": "you might consider",
        "you should": "you could",
        "best option": "one option",
        "perfect for you": "may be suitable",
        "ideal choice": "an option",
        "definitely": "potentially",
        "you need": "you may want"
    }
    
    for original, replacement in replacements.items():
        sanitized = sanitized.replace(original, replacement)
        sanitized = sanitized.replace(original.capitalize(), replacement.capitalize())
    
    return sanitized


# Made with Bob - Compliance-First AI Assistant