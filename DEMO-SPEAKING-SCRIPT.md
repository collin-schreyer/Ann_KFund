# Demo Speaking Script
## Bart & Associates AI Solutions for State Department

**Read this script while performing the demo actions**

---



Hi, welcome from Bart & Associates, and we're excited to show you our secure AI platform built specifically for the Department of State. This platform is hosted on AWS GovCloud, FedRAMP ready, and designed for Impact Level 5 environments. Let me show you what we've built.





As you can see, we have the State Department seal and Bart & Associates logo here. This platform currently hosts two AI-powered tools that solve real operational challenges for the Department.

The first is Export Control Compliance Search, and the second is Event Funding Allocation. Let me show you both.





First, the Export Control Compliance Search. State Department personnel currently spend hours manually researching ITAR, EAR, and internal policies to determine export licensing requirements.

With our AI system, they can simply ask questions in plain English. Let me demonstrate.

I'll ask: "Do I need a license to export thermal imaging cameras with 640x480 resolution to Mexico?"

In just seconds, the AI searches across all regulations and provides a comprehensive answer.

Notice it cites specific regulations - ITAR Category XII - and provides the exact thresholds that determine whether a license is needed. It even gives us a confidence level.

And here are the sources. Watch what happens when I click on one.

It shows me the exact regulation text that was used to generate this answer. This is the actual chunk retrieved from our vector database. Complete transparency and traceability.



EVENT FUNDING ALLOCATION

Now let me show you the second tool - Event Funding Allocation. This solves a completely different problem.

When State Department participates in White House events, certifying officers must manually classify every invoice line item to determine if it should be paid by EDCS, Diplomatic Programs, or the Executive Office of the President. This is complex appropriations law.

Our AI system analyzes the event documents - invoices, programs, seating charts - and automatically classifies everything. Let me show you with sample data.

This is a State Dinner for a foreign Prime Minister. Look at the allocation summary.

The system has automatically determined that forty-five thousand dollars goes to EDCS for representational items, thirty-five thousand to Diplomatic Programs for operational costs, and forty-five thousand to the Executive Office of the President for Presidential hospitality.

Here's the detailed breakdown. Each line item is classified with the reasoning. For example, gifts to foreign dignitaries - that's mandatory EDCS funding under 22 U.S.C. 2694.

Items that are unclear get flagged for legal review. And the system generates all the required documentation - certifying officer protection statements and reimbursement memos.





Now, what makes this secure? Everything runs on AWS GovCloud - that means all data stays within U.S. government boundaries. It's FedRAMP ready, supports Impact Level 5 workloads, and uses FIPS 140-2 encryption.

We're using AWS Bedrock for the AI - so no data ever goes to public services like ChatGPT. Everything stays in your secure environment.



CLOSING

This platform is ready to deploy to GovCloud and can scale to support additional AI use cases as the Department identifies new opportunities. We've built a secure foundation for AI at State.

Thank you for watching. We're excited to partner with the State Department on this initiative.

