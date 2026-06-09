"""
Product Comparison Service
Provides objective, factual product comparisons without recommendations
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.product import Product
from app.core.compliance_responses import ComplianceResponseTemplates


class ComparisonResult:
    """Result of product comparison"""
    
    def __init__(
        self,
        products: List[Product],
        comparison_table: Dict[str, Any],
        criteria: List[str],
        disclaimer: str
    ):
        self.products = products
        self.comparison_table = comparison_table
        self.criteria = criteria
        self.disclaimer = disclaimer
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "products": [p.to_dict() for p in self.products],
            "comparison_table": self.comparison_table,
            "criteria": self.criteria,
            "disclaimer": self.disclaimer,
            "comparison_count": len(self.products)
        }


class ProductComparisonService:
    """Service for objective product comparison (no recommendations)"""
    
    # Standard comparison criteria by product type
    COMPARISON_CRITERIA = {
        "savings": [
            "interest_rate",
            "min_amount",
            "fees",
            "features",
            "eligibility_criteria"
        ],
        "loan": [
            "interest_rate",
            "min_amount",
            "max_amount",
            "fees",
            "terms_and_conditions",
            "eligibility_criteria"
        ],
        "insurance": [
            "min_amount",
            "max_amount",
            "features",
            "eligibility_criteria",
            "terms_and_conditions"
        ],
        "credit_card": [
            "fees",
            "features",
            "eligibility_criteria",
            "interest_rate"
        ]
    }
    
    def __init__(self):
        """Initialize comparison service"""
        self.response_templates = ComplianceResponseTemplates()
    
    async def compare_products(
        self,
        db: AsyncSession,
        product_ids: List[str],
        comparison_criteria: Optional[List[str]] = None
    ) -> ComparisonResult:
        """
        Generate objective side-by-side product comparison
        
        Args:
            db: Database session
            product_ids: List of product IDs to compare
            comparison_criteria: Optional custom criteria (uses defaults if not provided)
            
        Returns:
            ComparisonResult with comparison data
        """
        # Fetch products
        products = await self._fetch_products(db, product_ids)
        
        if not products:
            raise ValueError("No products found for comparison")
        
        if len(products) < 2:
            raise ValueError("At least 2 products required for comparison")
        
        # Determine product type (all must be same type)
        product_types = set(p.product_type for p in products)
        if len(product_types) > 1:
            raise ValueError("Cannot compare products of different types")
        
        product_type = products[0].product_type
        
        # Use default criteria if not provided
        if not comparison_criteria:
            comparison_criteria = self.COMPARISON_CRITERIA.get(
                product_type,
                ["features", "eligibility_criteria", "fees"]
            )
        
        # Build comparison table
        comparison_table = self._build_comparison_table(products, comparison_criteria)
        
        # Get compliance disclaimer
        disclaimer = self.response_templates.format_response_with_disclaimer(
            "",
            "comparison"
        ).strip()
        
        return ComparisonResult(
            products=products,
            comparison_table=comparison_table,
            criteria=comparison_criteria,
            disclaimer=disclaimer
        )
    
    async def _fetch_products(
        self,
        db: AsyncSession,
        product_ids: List[str]
    ) -> List[Product]:
        """Fetch products by IDs"""
        result = await db.execute(
            select(Product).where(
                and_(
                    Product.id.in_(product_ids),
                    Product.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    def _build_comparison_table(
        self,
        products: List[Product],
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Build comparison table with objective data
        
        Returns dictionary with structure:
        {
            "criteria_name": {
                "product_id_1": value,
                "product_id_2": value,
                ...
            }
        }
        """
        comparison = {}
        
        for criterion in criteria:
            comparison[criterion] = {}
            
            for product in products:
                product_id = str(product.id)
                
                # Get value for this criterion
                if criterion == "interest_rate":
                    value = f"{float(product.interest_rate)}%" if product.interest_rate else "N/A"
                
                elif criterion == "min_amount":
                    value = f"${float(product.min_amount):,.2f}" if product.min_amount else "No minimum"
                
                elif criterion == "max_amount":
                    value = f"${float(product.max_amount):,.2f}" if product.max_amount else "No maximum"
                
                elif criterion == "fees":
                    value = product.fees if product.fees else {}
                
                elif criterion == "features":
                    value = product.features if product.features else []
                
                elif criterion == "eligibility_criteria":
                    value = product.eligibility_criteria if product.eligibility_criteria else []
                
                elif criterion == "terms_and_conditions":
                    value = product.terms_and_conditions if product.terms_and_conditions else "See product documentation"
                
                else:
                    # Generic attribute access
                    value = getattr(product, criterion, "N/A")
                
                comparison[criterion][product_id] = value
        
        return comparison
    
    async def get_products_by_type(
        self,
        db: AsyncSession,
        product_type: str,
        limit: int = 50
    ) -> List[Product]:
        """Get all active products of a specific type"""
        result = await db.execute(
            select(Product).where(
                and_(
                    Product.product_type == product_type,
                    Product.is_active == True
                )
            ).order_by(Product.display_order, Product.product_name).limit(limit)
        )
        return list(result.scalars().all())
    
    async def search_products(
        self,
        db: AsyncSession,
        query: str,
        product_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Product]:
        """Search products by name or description"""
        conditions = [Product.is_active == True]
        
        if product_type:
            conditions.append(Product.product_type == product_type)
        
        # Simple text search (in production, use full-text search)
        search_pattern = f"%{query}%"
        conditions.append(
            (Product.product_name.ilike(search_pattern)) |
            (Product.description.ilike(search_pattern))
        )
        
        result = await db.execute(
            select(Product).where(and_(*conditions)).limit(limit)
        )
        return list(result.scalars().all())
    
    def format_comparison_for_display(
        self,
        comparison_result: ComparisonResult
    ) -> str:
        """
        Format comparison result as human-readable text
        
        Returns formatted comparison suitable for AI response
        """
        products = comparison_result.products
        table = comparison_result.comparison_table
        
        # Build header
        output = "# Product Comparison\n\n"
        output += f"Comparing {len(products)} products:\n"
        for i, product in enumerate(products, 1):
            output += f"{i}. **{product.product_name}** ({product.product_code})\n"
        
        output += "\n## Comparison Details\n\n"
        
        # Build comparison table
        for criterion, values in table.items():
            output += f"### {criterion.replace('_', ' ').title()}\n\n"
            
            for product in products:
                product_id = str(product.id)
                value = values.get(product_id, "N/A")
                
                # Format value based on type
                if isinstance(value, list):
                    value_str = "\n  - " + "\n  - ".join(str(v) for v in value) if value else "None"
                elif isinstance(value, dict):
                    value_str = "\n  " + "\n  ".join(f"- {k}: {v}" for k, v in value.items()) if value else "None"
                else:
                    value_str = str(value)
                
                output += f"**{product.product_name}**: {value_str}\n\n"
        
        # Add disclaimer
        output += f"\n---\n\n{comparison_result.disclaimer}\n"
        
        return output
    
    def generate_comparison_summary(
        self,
        comparison_result: ComparisonResult
    ) -> Dict[str, Any]:
        """
        Generate objective summary of comparison
        
        NO subjective ratings or recommendations
        """
        products = comparison_result.products
        table = comparison_result.comparison_table
        
        summary = {
            "product_count": len(products),
            "product_names": [p.product_name for p in products],
            "key_differences": [],
            "common_features": [],
            "note": "This is an objective comparison. Consult a licensed advisor for personalized recommendations."
        }
        
        # Identify key differences (objective facts only)
        if "interest_rate" in table:
            rates = [v for v in table["interest_rate"].values() if v != "N/A"]
            if rates:
                summary["key_differences"].append(f"Interest rates range from {min(rates)} to {max(rates)}")
        
        if "min_amount" in table:
            amounts = [v for v in table["min_amount"].values() if v != "No minimum"]
            if amounts:
                summary["key_differences"].append(f"Minimum amounts vary: {', '.join(amounts)}")
        
        # Identify common features (if all products have same feature)
        if "features" in table:
            all_features = []
            for features in table["features"].values():
                if isinstance(features, list):
                    all_features.extend(features)
            
            # Find features common to all products
            feature_counts = {}
            for feature in all_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            common = [f for f, count in feature_counts.items() if count == len(products)]
            if common:
                summary["common_features"] = common
        
        return summary


# Global comparison service instance
comparison_service = ProductComparisonService()


# Made with Bob - Compliance-First AI Assistant