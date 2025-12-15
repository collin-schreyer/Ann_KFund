# Platform Demo Script
## Bart & Associates AI Solutions for State Department

**Total Time: 3-4 minutes**

---

## INTRODUCTION (15 seconds)

"Hi, I'm [Name] from Bart & Associates, and I'm excited to show you our secure AI platform built specifically for the Department of State. This platform is hosted on AWS GovCloud, FedRAMP ready, and designed for Impact Level 5 environments. Let me show you what we've built."

**[ACTION: Show homepage - index.html]**

---

## HOMEPAGE OVERVIEW (20 seconds)

"As you can see, we have the State Department seal and Bart & Associates logo here. This platform currently hosts two AI-powered tools that solve real operational challenges for the Department."

**[ACTION: Pause on homepage, gesture to the two main sections]**

"The first is Export Control Compliance Search, and the second is Event Funding Allocation. Let me show you both."

---

## TOOL 1: EXPORT CONTROL SEARCH (60 seconds)

**[ACTION: Click "Export Control Search" button]**

"First, the Export Control Compliance Search. State Department personnel currently spend hours manually researching ITAR, EAR, and internal policies to determine export licensing requirements."

**[ACTION: Scroll down to show example questions]**

"With our AI system, they can simply ask questions in plain English. Let me demonstrate."

**[ACTION: Click example button "Thermal Cameras to Mexico" OR type the question]**

"I'll ask: 'Do I need a license to export thermal imaging cameras with 640x480 resolution to Mexico?'"

**[ACTION: Click "Search Regulations" button]**

**[WAIT: 5-10 seconds for response]**

"In just seconds, the AI searches across all regulations and provides a comprehensive answer."

**[ACTION: Scroll through the answer]**

"Notice it cites specific regulations - ITAR Category XII - and provides the exact thresholds that determine whether a license is needed. It even gives us a confidence level."

**[ACTION: Scroll down to citations]**

"And here are the sources. Watch what happens when I click on one."

**[ACTION: Click to expand a citation accordion]**

"It shows me the exact regulation text that was used to generate this answer. This is the actual chunk retrieved from our vector database. Complete transparency and traceability."

**[ACTION: Collapse citation]**

---

## TOOL 2: EVENT FUNDING ALLOCATION (60 seconds)

**[ACTION: Click "Event Funding" in navigation]**

"Now let me show you the second tool - Event Funding Allocation. This solves a completely different problem."

**[ACTION: Scroll down slightly]**

"When State Department participates in White House events, certifying officers must manually classify every invoice line item to determine if it should be paid by EDCS, Diplomatic Programs, or the Executive Office of the President. This is complex appropriations law."

**[ACTION: Scroll to show upload section]**

"Our AI system analyzes the event documents - invoices, programs, seating charts - and automatically classifies everything. Let me show you with sample data."

**[ACTION: Click "Load Sample Event" button]**

**[WAIT: 2 seconds for data to load]**

"This is a State Dinner for a foreign Prime Minister. Look at the allocation summary."

**[ACTION: Point to the three colored boxes showing EDCS/DP/EOP breakdown]**

"The system has automatically determined that $45,000 goes to EDCS for representational items, $35,000 to Diplomatic Programs for operational costs, and $45,000 to the Executive Office of the President for Presidential hospitality."

**[ACTION: Scroll down to line items table]**

"Here's the detailed breakdown. Each line item is classified with the reasoning. For example, gifts to foreign dignitaries - that's mandatory EDCS funding under 22 U.S.C. 2694."

**[ACTION: Scroll down to legal review section if visible]**

"Items that are unclear get flagged for legal review. And the system generates all the required documentation - certifying officer protection statements and reimbursement memos."

---

## SECURITY & ARCHITECTURE (30 seconds)

**[ACTION: Navigate back to homepage - click logo or Home]**

**[ACTION: Scroll down to "Why AWS GovCloud" section]**

"Now, what makes this secure? Everything runs on AWS GovCloud - that means all data stays within U.S. government boundaries. It's FedRAMP ready, supports Impact Level 5 workloads, and uses FIPS 140-2 encryption."

**[ACTION: Scroll to Technology Stack section]**

"We're using AWS Bedrock for the AI - so no data ever goes to public services like ChatGPT. Everything stays in your secure environment."

---

## CLOSING (15 seconds)

**[ACTION: Scroll back to top of homepage]**

"This platform is ready to deploy to GovCloud and can scale to support additional AI use cases as the Department identifies new opportunities. We've built a secure foundation for AI at State."

**[ACTION: Pause on homepage with both logos visible]**

"Thank you for watching. We're excited to partner with the State Department on this initiative."

---

## TECHNICAL NOTES FOR RECORDING

**Before Recording:**
- [ ] Open homepage (index.html) in browser
- [ ] Make sure API server is running (python api_server.py)
- [ ] Test the search function once to ensure it's working
- [ ] Clear browser cache if needed for clean demo
- [ ] Set browser zoom to 100% or 110% for visibility
- [ ] Close unnecessary browser tabs
- [ ] Disable browser notifications

**Recording Settings:**
- Screen resolution: 1920x1080 or 1280x720
- Frame rate: 30fps minimum
- Audio: Clear microphone, no background noise
- Cursor: Make sure cursor is visible and easy to follow

**Pacing Tips:**
- Speak clearly and at moderate pace
- Pause briefly after clicking buttons to let things load
- Don't rush through the answer text - let viewers see it
- Use cursor to highlight important elements
- Practice the demo 2-3 times before recording

**Backup Plan:**
- If API is slow, have screenshots ready
- If something doesn't load, have a backup browser window open
- Practice the "Load Sample Event" button timing

---

## ALTERNATIVE SHORTER VERSION (2 minutes)

If you need a faster demo, skip:
- Detailed explanation of citations
- Scrolling through all line items in allocation tool
- Technology stack section

Focus on:
- Quick homepage overview
- One search example with answer
- One allocation example with summary
- Security statement
- Close

---

## ALTERNATIVE LONGER VERSION (5 minutes)

If you have more time, add:
- Show multiple search examples
- Demonstrate the accordion expansion for multiple citations
- Show the "EDCS Must Pay" button functionality
- Explain the reimbursement memo generation
- Discuss future use cases
- Show the architecture diagram from docs

---

**Good luck with your recording!**
