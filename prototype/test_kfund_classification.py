"""
Unit Tests for K Fund Classification Rules

Tests the classification logic for determining K Fund allowability
of event line items per 22 U.S.C. § 2671 and related authorities.
"""

import unittest
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LineItem:
    """Represents an event line item."""
    item: str
    cost: float
    description: str = ""


@dataclass
class ClassificationResult:
    """Result of K Fund classification."""
    classification: str  # K_FUND_ALLOWABLE, NOT_ALLOWABLE, LEGAL_REVIEW
    authority: Optional[str] = None
    reason: Optional[str] = None
    confidence: str = "medium"
    proration_required: bool = False


# Classification keywords
ALWAYS_ALLOWABLE_KEYWORDS = [
    'gift', 'present', 'commemorative', 'crystal', 'vase', 'portfolio',
    'dinner', 'lunch', 'breakfast', 'reception', 'catering', 'food', 
    'beverage', 'wine', 'champagne', 'meal', "hors d'oeuvres",
    'floral', 'flowers', 'centerpiece', 'arrangement', 'bouquet',
    'menu', 'program', 'place card', 'invitation', 'printed', 'calligraphy'
]

NEVER_ALLOWABLE_KEYWORDS = [
    'security', 'screening', 'guard', 'protection', 'surveillance',
    'stage construction', 'venue modification', 'permanent installation',
    'staff overtime', 'personnel', 'salary', 'wages', 'labor cost',
    'transportation', 'vehicle', 'car service', 'shuttle', 'airport', 'motorcade'
]

REQUIRES_ANALYSIS_KEYWORDS = [
    'photography', 'photographer', 'photos', 'pictures',
    'entertainment', 'music', 'band', 'orchestra', 'performer', 'quartet',
    'a/v', 'audio', 'visual', 'sound system', 'microphone', 'lighting',
    'décor', 'decoration', 'staging', 'setup', 'breakdown'
]


def classify_line_item(item: LineItem) -> ClassificationResult:
    """
    Classify a line item for K Fund allowability.
    
    Args:
        item: LineItem to classify
        
    Returns:
        ClassificationResult with determination
    """
    item_lower = item.item.lower()
    
    # Check always allowable
    for keyword in ALWAYS_ALLOWABLE_KEYWORDS:
        if keyword in item_lower:
            # Determine specific authority
            if any(k in item_lower for k in ['gift', 'present', 'commemorative', 'crystal', 'vase', 'portfolio']):
                authority = "22 U.S.C. § 2694"
            else:
                authority = "22 U.S.C. § 2671"
            
            return ClassificationResult(
                classification="K_FUND_ALLOWABLE",
                authority=authority,
                confidence="high",
                proration_required='catering' in item_lower or 'food' in item_lower or 'beverage' in item_lower
            )
    
    # Check never allowable
    for keyword in NEVER_ALLOWABLE_KEYWORDS:
        if keyword in item_lower:
            return ClassificationResult(
                classification="NOT_ALLOWABLE",
                reason="Operational expense - not representational",
                confidence="high"
            )
    
    # Check requires analysis
    for keyword in REQUIRES_ANALYSIS_KEYWORDS:
        if keyword in item_lower:
            return ClassificationResult(
                classification="LEGAL_REVIEW",
                reason="Requires analysis of purpose and beneficiary",
                confidence="low"
            )
    
    # Default: requires legal review
    return ClassificationResult(
        classification="LEGAL_REVIEW",
        reason="Does not match established classification rules",
        confidence="low"
    )


def calculate_proration(total_cost: float, foreign_guests: int, total_guests: int) -> float:
    """
    Calculate K Fund allowable amount based on foreign guest proration.
    
    Args:
        total_cost: Total cost of the expense
        foreign_guests: Number of foreign guests
        total_guests: Total number of guests
        
    Returns:
        K Fund allowable amount after proration
    """
    if total_guests == 0:
        return 0.0
    
    foreign_percentage = foreign_guests / total_guests
    return total_cost * foreign_percentage


class TestKFundClassification(unittest.TestCase):
    """Test cases for K Fund classification rules."""
    
    # ==========================================
    # Tests for Always Allowable Items
    # ==========================================
    
    def test_gift_to_foreign_official_is_allowable(self):
        """Gifts to foreign officials are always K Fund allowable per 22 U.S.C. § 2694."""
        item = LineItem(item="Crystal vase gift for Ambassador", cost=2500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
        self.assertEqual(result.authority, "22 U.S.C. § 2694")
        self.assertEqual(result.confidence, "high")
    
    def test_commemorative_item_is_allowable(self):
        """Commemorative items for dignitaries are K Fund allowable."""
        item = LineItem(item="Commemorative portfolio for Prime Minister", cost=1500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
        self.assertEqual(result.authority, "22 U.S.C. § 2694")
    
    def test_catering_is_allowable_with_proration(self):
        """Catering for diplomatic events is allowable but may require proration."""
        item = LineItem(item="Reception catering services", cost=8500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
        self.assertEqual(result.authority, "22 U.S.C. § 2671")
        self.assertTrue(result.proration_required)
    
    def test_food_and_beverage_is_allowable(self):
        """Food and beverage for foreign guests is K Fund allowable."""
        item = LineItem(item="Dinner service with wine pairing", cost=5000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
    
    def test_floral_arrangements_are_allowable(self):
        """Floral arrangements for guest areas are K Fund allowable."""
        item = LineItem(item="Floral centerpieces for dining tables", cost=1200)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
        self.assertEqual(result.authority, "22 U.S.C. § 2671")
    
    def test_printed_programs_are_allowable(self):
        """Printed programs and menus are K Fund allowable."""
        item = LineItem(item="Printed programs and place cards", cost=450)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
    
    def test_invitation_printing_is_allowable(self):
        """Invitation printing is K Fund allowable."""
        item = LineItem(item="Calligraphy invitations for State Dinner", cost=800)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
    
    # ==========================================
    # Tests for Never Allowable Items
    # ==========================================
    
    def test_security_is_not_allowable(self):
        """Security costs are operational and not K Fund allowable."""
        item = LineItem(item="Security screening equipment", cost=3500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
        self.assertIn("Operational", result.reason)
        self.assertEqual(result.confidence, "high")
    
    def test_transportation_is_not_allowable(self):
        """Transportation costs are not K Fund allowable."""
        item = LineItem(item="Airport shuttle service for delegation", cost=2000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
    
    def test_motorcade_is_not_allowable(self):
        """Motorcade costs are not K Fund allowable."""
        item = LineItem(item="Motorcade coordination", cost=5000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
    
    def test_staff_overtime_is_not_allowable(self):
        """Staff overtime is a personnel expense, not K Fund allowable."""
        item = LineItem(item="Staff overtime for event setup", cost=1500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
    
    def test_venue_modification_is_not_allowable(self):
        """Venue modifications are capital expenses, not K Fund allowable."""
        item = LineItem(item="Permanent installation of lighting fixtures", cost=8000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
    
    def test_guard_services_not_allowable(self):
        """Guard services are security/operational, not K Fund allowable."""
        item = LineItem(item="Additional guard services", cost=4000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "NOT_ALLOWABLE")
    
    # ==========================================
    # Tests for Items Requiring Legal Review
    # ==========================================
    
    def test_photography_requires_review(self):
        """Photography requires analysis of purpose."""
        item = LineItem(item="Photography services", cost=1500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "LEGAL_REVIEW")
        self.assertEqual(result.confidence, "low")
    
    def test_entertainment_requires_review(self):
        """Entertainment requires analysis of beneficiary."""
        item = LineItem(item="String quartet entertainment", cost=2000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "LEGAL_REVIEW")
    
    def test_av_equipment_requires_review(self):
        """A/V equipment requires analysis of use."""
        item = LineItem(item="A/V equipment rental", cost=3000)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "LEGAL_REVIEW")
    
    def test_staging_requires_review(self):
        """Staging requires analysis of purpose."""
        item = LineItem(item="Event staging and setup", cost=4500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "LEGAL_REVIEW")
    
    def test_unknown_item_requires_review(self):
        """Unknown items should be routed to legal review."""
        item = LineItem(item="Miscellaneous event supplies", cost=500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "LEGAL_REVIEW")
    
    # ==========================================
    # Tests for Proration Calculation
    # ==========================================
    
    def test_proration_calculation(self):
        """Test proration based on foreign guest percentage."""
        total_cost = 10000
        foreign_guests = 45
        total_guests = 100
        
        result = calculate_proration(total_cost, foreign_guests, total_guests)
        
        self.assertEqual(result, 4500.0)
    
    def test_proration_all_foreign(self):
        """100% foreign guests means full K Fund allowability."""
        total_cost = 5000
        foreign_guests = 50
        total_guests = 50
        
        result = calculate_proration(total_cost, foreign_guests, total_guests)
        
        self.assertEqual(result, 5000.0)
    
    def test_proration_no_foreign(self):
        """0% foreign guests means no K Fund allowability."""
        total_cost = 5000
        foreign_guests = 0
        total_guests = 50
        
        result = calculate_proration(total_cost, foreign_guests, total_guests)
        
        self.assertEqual(result, 0.0)
    
    def test_proration_zero_guests(self):
        """Zero total guests should return 0."""
        total_cost = 5000
        foreign_guests = 0
        total_guests = 0
        
        result = calculate_proration(total_cost, foreign_guests, total_guests)
        
        self.assertEqual(result, 0.0)
    
    # ==========================================
    # Tests for Edge Cases
    # ==========================================
    
    def test_case_insensitive_matching(self):
        """Classification should be case-insensitive."""
        item = LineItem(item="CRYSTAL VASE GIFT", cost=2500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
    
    def test_partial_keyword_match(self):
        """Keywords should match as substrings."""
        item = LineItem(item="Diplomatic gift presentation ceremony", cost=500)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")
    
    def test_multiple_keywords_first_match_wins(self):
        """When multiple keywords match, first applicable rule wins."""
        # "gift" is always allowable, even if "setup" is in the description
        item = LineItem(item="Gift wrapping and setup", cost=200)
        result = classify_line_item(item)
        
        self.assertEqual(result.classification, "K_FUND_ALLOWABLE")


class TestKFundIntegration(unittest.TestCase):
    """Integration tests for K Fund classification workflow."""
    
    def test_full_event_classification(self):
        """Test classification of a complete event's line items."""
        line_items = [
            LineItem(item="Crystal vase gift for Ambassador", cost=2500),
            LineItem(item="Reception catering", cost=8500),
            LineItem(item="Floral centerpieces", cost=1200),
            LineItem(item="Security screening", cost=3500),
            LineItem(item="Photography services", cost=1500),
        ]
        
        results = [classify_line_item(item) for item in line_items]
        
        # Count classifications
        allowable = sum(1 for r in results if r.classification == "K_FUND_ALLOWABLE")
        not_allowable = sum(1 for r in results if r.classification == "NOT_ALLOWABLE")
        legal_review = sum(1 for r in results if r.classification == "LEGAL_REVIEW")
        
        self.assertEqual(allowable, 3)  # gift, catering, floral
        self.assertEqual(not_allowable, 1)  # security
        self.assertEqual(legal_review, 1)  # photography
    
    def test_event_with_proration(self):
        """Test event classification with proration calculation."""
        catering_item = LineItem(item="Dinner catering service", cost=10000)
        result = classify_line_item(catering_item)
        
        self.assertTrue(result.proration_required)
        
        # Calculate prorated amount
        foreign_guests = 30
        total_guests = 100
        prorated_amount = calculate_proration(catering_item.cost, foreign_guests, total_guests)
        
        self.assertEqual(prorated_amount, 3000.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
