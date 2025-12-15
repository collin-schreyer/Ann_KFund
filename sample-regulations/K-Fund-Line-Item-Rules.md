# K Fund Line Item Classification Rules

## Automatic Classification Rules

This document defines the rules for automatically classifying event line items for K Fund allowability.

---

## Rule Set 1: Always Allowable

### Rule 1.1: Gifts to Foreign Officials
**Trigger Words:** gift, present, commemorative, crystal, vase, portfolio, presentation item
**Recipient:** Foreign official, dignitary, ambassador, minister, prime minister
**Classification:** K_FUND_ALLOWABLE
**Authority:** 22 U.S.C. § 2694
**Confidence:** HIGH

**Rationale:** Gifts to foreign officials are a statutory requirement and core representational function.

### Rule 1.2: Food and Beverage for Foreign Guests
**Trigger Words:** dinner, lunch, breakfast, reception, catering, food, beverage, wine, champagne, meal
**Condition:** Foreign officials on guest list
**Classification:** K_FUND_ALLOWABLE (may require proration)
**Authority:** 22 U.S.C. § 2671
**Confidence:** HIGH

**Rationale:** Hospitality extended to foreign officials is a fundamental representational expense.

### Rule 1.3: Floral Arrangements in Guest Areas
**Trigger Words:** floral, flowers, centerpiece, arrangement, bouquet
**Location:** Guest tables, reception areas, dining rooms
**Classification:** K_FUND_ALLOWABLE
**Authority:** 22 U.S.C. § 2671
**Confidence:** HIGH

**Rationale:** Décor that enhances the guest experience is representational.

### Rule 1.4: Printed Programs and Menus
**Trigger Words:** menu, program, place card, invitation, printed, calligraphy
**Purpose:** For guests
**Classification:** K_FUND_ALLOWABLE
**Authority:** 22 U.S.C. § 2671
**Confidence:** HIGH

**Rationale:** Materials provided to guests are part of the representational experience.

---

## Rule Set 2: Never Allowable

### Rule 2.1: Security Costs
**Trigger Words:** security, screening, guard, protection, surveillance
**Classification:** NOT_ALLOWABLE
**Reason:** Operational expense, not representational
**Confidence:** HIGH

**Rationale:** Security enables the event but is not received by guests as hospitality.

### Rule 2.2: Venue Infrastructure
**Trigger Words:** stage construction, venue modification, permanent installation
**Classification:** NOT_ALLOWABLE
**Reason:** Capital expense
**Confidence:** HIGH

**Rationale:** Infrastructure improvements are not representational expenses.

### Rule 2.3: Staff Costs
**Trigger Words:** staff overtime, personnel, salary, wages, labor
**Classification:** NOT_ALLOWABLE
**Reason:** Personnel expense
**Confidence:** HIGH

**Rationale:** Staff costs are operational, not representational.

### Rule 2.4: Transportation
**Trigger Words:** transportation, vehicle, car service, shuttle, airport
**Classification:** NOT_ALLOWABLE
**Reason:** Operational expense
**Confidence:** HIGH

**Rationale:** Transportation is logistical support, not representational.

---

## Rule Set 3: Requires Analysis

### Rule 3.1: Photography Services
**Trigger Words:** photography, photographer, photos, pictures
**Analysis Required:**
- Official diplomatic photos with foreign officials → K_FUND_ALLOWABLE
- General event documentation → NOT_ALLOWABLE
- Mixed purpose → LEGAL_REVIEW
**Confidence:** MEDIUM

**Questions to Ask:**
1. Will photos be presented to foreign officials?
2. Are photos for diplomatic record or general documentation?
3. Who is the primary beneficiary of the photos?

### Rule 3.2: Entertainment
**Trigger Words:** entertainment, music, band, orchestra, performer, quartet
**Analysis Required:**
- Entertainment for foreign guests at representational event → K_FUND_ALLOWABLE
- Background ambiance → LEGAL_REVIEW
- Entertainment for U.S. officials only → NOT_ALLOWABLE
**Confidence:** MEDIUM

**Questions to Ask:**
1. Are foreign officials present during entertainment?
2. Is entertainment part of the official program?
3. Does entertainment serve representational purpose?

### Rule 3.3: Audio/Visual Equipment
**Trigger Words:** A/V, audio, visual, sound system, microphone, screen, projector
**Analysis Required:**
- For toasts/remarks to foreign officials → K_FUND_ALLOWABLE
- For interpretation services → K_FUND_ALLOWABLE
- General event support → NOT_ALLOWABLE
**Confidence:** MEDIUM

**Questions to Ask:**
1. Is A/V used for diplomatic presentations?
2. Does A/V support interpretation for foreign guests?
3. Is A/V purely operational?

### Rule 3.4: Décor and Staging
**Trigger Words:** décor, decoration, staging, lighting, setup
**Analysis Required:**
- Guest-facing décor → K_FUND_ALLOWABLE
- Backstage/operational → NOT_ALLOWABLE
- Mixed areas → Prorate or LEGAL_REVIEW
**Confidence:** MEDIUM

**Questions to Ask:**
1. Is décor in areas where foreign guests will be present?
2. Does décor enhance the representational experience?
3. Is décor purely functional/operational?

### Rule 3.5: Interpretation Services
**Trigger Words:** interpretation, interpreter, translation, translator, language
**Analysis Required:**
- For foreign officials → K_FUND_ALLOWABLE
- For U.S. staff → NOT_ALLOWABLE
- Equipment rental → LEGAL_REVIEW
**Confidence:** MEDIUM

**Questions to Ask:**
1. Who is the primary beneficiary of interpretation?
2. Is interpretation for diplomatic communication?
3. Is this equipment or services?

---

## Rule Set 4: Proration Rules

### Rule 4.1: Mixed Guest Events
**Condition:** Event includes both foreign and domestic guests
**Action:** Prorate based on foreign guest percentage
**Formula:** K Fund Amount = Total × (Foreign Guests ÷ Total Guests)
**Confidence:** HIGH

### Rule 4.2: Shared Hosting
**Condition:** Event co-hosted by multiple entities (e.g., President and Secretary)
**Action:** Allocate based on hosting responsibilities
**Confidence:** MEDIUM (may require LEGAL_REVIEW)

### Rule 4.3: Multi-Purpose Items
**Condition:** Item serves both representational and operational purposes
**Action:** Prorate based on primary purpose or seek LEGAL_REVIEW
**Confidence:** LOW

---

## Confidence Levels

| Level | Meaning | Action |
|-------|---------|--------|
| HIGH | Clear classification based on established rules | Auto-classify |
| MEDIUM | Likely classification but may need verification | Flag for review |
| LOW | Unclear classification | Route to Legal Adviser |

---

## Legal Review Triggers

Route to Legal Adviser when:
1. Confidence level is LOW
2. Item doesn't match any rule
3. Unusual expense type
4. High-value item (>$5,000)
5. Novel situation
6. Disputed classification
