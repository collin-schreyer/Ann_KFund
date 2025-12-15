// Event Funding Allocation Tool - JavaScript

function loadSampleData() {
    document.getElementById('eventName').value = "State Dinner for Prime Minister of Country X";
    document.getElementById('eventDate').value = "2025-12-15";
    
    // Show sample results
    const sampleData = {
        eventName: "State Dinner for Prime Minister of Country X",
        eventDate: "December 15, 2025",
        totalCost: 125000,
        allocations: {
            EDCS: 45000,
            DP: 35000,
            EOP: 45000
        },
        lineItems: [
            {
                item: "Floral arrangements for guest tables",
                cost: 8500,
                classification: "EOP",
                reason: "Presidential hospitality - received by guests at President-hosted dinner",
                confidence: "high"
            },
            {
                item: "Gifts to foreign dignitaries (crystal vases)",
                cost: 12000,
                classification: "EDCS",
                reason: "Mandatory EDCS - gifts to foreign officials per 22 U.S.C. § 2694",
                confidence: "high",
                mandatory: true
            },
            {
                item: "Dinner service (food & beverage)",
                cost: 35000,
                classification: "EOP",
                reason: "Presidential hospitality - President as host",
                confidence: "high"
            },
            {
                item: "Secretary's toast remarks - printed programs",
                cost: 2500,
                classification: "EDCS",
                reason: "Secretary's representational function per 22 U.S.C. § 2671",
                confidence: "high"
            },
            {
                item: "Stage lighting and A/V equipment",
                cost: 15000,
                classification: "DP",
                reason: "Operational infrastructure - not received by guests",
                confidence: "high"
            },
            {
                item: "Security augmentation",
                cost: 12000,
                classification: "DP",
                reason: "Operational support - enables event but not hospitality",
                confidence: "high"
            },
            {
                item: "Interpretation equipment",
                cost: 8000,
                classification: "DP",
                reason: "Operational technology - necessary expense",
                confidence: "high"
            },
            {
                item: "Protocol décor in State Department holding room",
                cost: 4500,
                classification: "EDCS",
                reason: "Secretary's representational space",
                confidence: "medium",
                legalReview: true
            },
            {
                item: "Entertainment (string quartet)",
                cost: 7500,
                classification: "EOP",
                reason: "Presidential hospitality - part of President's event",
                confidence: "high"
            },
            {
                item: "Venue setup and breakdown",
                cost: 10000,
                classification: "DP",
                reason: "Operational logistics",
                confidence: "high"
            },
            {
                item: "Photography services",
                cost: 5000,
                classification: "LEGAL_REVIEW",
                reason: "Unclear - serves both representational and operational purposes",
                confidence: "low",
                legalReview: true
            },
            {
                item: "Commemorative menu cards",
                cost: 5000,
                classification: "LEGAL_REVIEW",
                reason: "Unclear recipient - could be Presidential or Secretary hospitality",
                confidence: "low",
                legalReview: true
            }
        ]
    };
    
    displayResults(sampleData);
}

function processAllocation() {
    const eventName = document.getElementById('eventName').value;
    const eventDate = document.getElementById('eventDate').value;
    
    if (!eventName || !eventDate) {
        alert('Please enter event name and date');
        return;
    }
    
    // In production, this would process uploaded documents
    alert('In production, this would:\n\n1. Extract text from uploaded documents\n2. Identify hosts from program/invitation\n3. Parse invoice line items\n4. Apply classification rules\n5. Generate allocation report\n\nFor now, click "Load Sample Event" to see example results.');
}

function displayResults(data) {
    // Show results container
    document.getElementById('results').classList.add('show');
    
    // Display allocation summary
    const summaryHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
            <div style="background: #e7f6f8; padding: 1.5rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">$${data.allocations.EDCS.toLocaleString()}</div>
                <div style="font-weight: 600; margin-top: 0.5rem;">EDCS (K Fund)</div>
                <div style="font-size: 0.9rem; color: var(--base-dark);">${((data.allocations.EDCS/data.totalCost)*100).toFixed(1)}%</div>
            </div>
            <div style="background: #fef0c8; padding: 1.5rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: #936f38;">$${data.allocations.DP.toLocaleString()}</div>
                <div style="font-weight: 600; margin-top: 0.5rem;">Diplomatic Programs</div>
                <div style="font-size: 0.9rem; color: var(--base-dark);">${((data.allocations.DP/data.totalCost)*100).toFixed(1)}%</div>
            </div>
            <div style="background: #e7f4e4; padding: 1.5rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: var(--success);">$${data.allocations.EOP.toLocaleString()}</div>
                <div style="font-weight: 600; margin-top: 0.5rem;">EOP (White House)</div>
                <div style="font-size: 0.9rem; color: var(--base-dark);">${((data.allocations.EOP/data.totalCost)*100).toFixed(1)}%</div>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: var(--base-lightest); border-radius: 4px;">
            <strong>Total Event Cost:</strong> $${data.totalCost.toLocaleString()}
        </div>
    `;
    document.getElementById('allocationSummary').innerHTML = summaryHTML;
    
    // Display line items table
    const legalItems = data.lineItems.filter(item => item.legalReview);
    const regularItems = data.lineItems.filter(item => !item.legalReview);
    
    let tableHTML = '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse;">';
    tableHTML += '<thead><tr style="background: var(--base-darker); color: white;">';
    tableHTML += '<th style="padding: 0.75rem; text-align: left;">Line Item</th>';
    tableHTML += '<th style="padding: 0.75rem; text-align: right;">Cost</th>';
    tableHTML += '<th style="padding: 0.75rem; text-align: center;">Classification</th>';
    tableHTML += '<th style="padding: 0.75rem; text-align: left;">Reason</th>';
    tableHTML += '</tr></thead><tbody>';
    
    regularItems.forEach((item, index) => {
        const bgColor = index % 2 === 0 ? 'white' : 'var(--base-lightest)';
        const classColor = item.classification === 'EDCS' ? 'var(--primary)' : 
                          item.classification === 'DP' ? '#936f38' : 'var(--success)';
        
        tableHTML += `<tr style="background: ${bgColor};">`;
        tableHTML += `<td style="padding: 0.75rem;">${item.mandatory ? '⭐ ' : ''}${item.item}</td>`;
        tableHTML += `<td style="padding: 0.75rem; text-align: right; font-weight: 600;">$${item.cost.toLocaleString()}</td>`;
        tableHTML += `<td style="padding: 0.75rem; text-align: center;"><span style="background: ${classColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 600; font-size: 0.85rem;">${item.classification}</span></td>`;
        tableHTML += `<td style="padding: 0.75rem; font-size: 0.9rem;">${item.reason}</td>`;
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table></div>';
    document.getElementById('lineItemsTable').innerHTML = tableHTML;
    
    // Display legal review items if any
    if (legalItems.length > 0) {
        document.getElementById('legalReview').style.display = 'block';
        let legalHTML = '';
        legalItems.forEach(item => {
            legalHTML += `
                <div class="citation-item" style="border-left-color: var(--warning);">
                    <div style="font-weight: 700;">${item.item} - $${item.cost.toLocaleString()}</div>
                    <div style="margin-top: 0.5rem; color: var(--base-dark);">${item.reason}</div>
                    <button class="usa-button" style="margin-top: 1rem; font-size: 0.9rem; padding: 0.5rem 1rem;" onclick="markEDCSMustPay('${item.item}')">
                        ⚖️ EDCS Must Pay
                    </button>
                </div>
            `;
        });
        document.getElementById('legalItems').innerHTML = legalHTML;
    }
    
    // Show reimbursement memo if DP items exist
    if (data.allocations.DP > 0) {
        document.getElementById('reimbursementMemo').style.display = 'block';
        const memoHTML = `
            <p><strong>Subject:</strong> Allocation and Reimbursement for Mixed DP/EDCS Event Costs</p>
            <p><strong>Event:</strong> ${data.eventName}</p>
            <p><strong>Date:</strong> ${data.eventDate}</p>
            <p style="margin-top: 1rem;"><strong>Purpose:</strong> This memorandum documents the allocation and reimbursement of expenses associated with the above event, which included both representational and operational components.</p>
            <p style="margin-top: 1rem;"><strong>Allocation Summary:</strong></p>
            <ul style="margin-left: 2rem; line-height: 1.8;">
                <li>EDCS (Representational): $${data.allocations.EDCS.toLocaleString()}</li>
                <li>DP (Operational): $${data.allocations.DP.toLocaleString()}</li>
                <li>EOP (Presidential Hospitality): $${data.allocations.EOP.toLocaleString()}</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Action:</strong> EDCS has paid invoice for its representational portions. DP hereby obligates $${data.allocations.DP.toLocaleString()} for the operational portion attributable to DP and requests an intra-bureau reimbursement to EDCS in the same amount.</p>
            <p style="margin-top: 1rem;"><strong>Authority:</strong> 31 U.S.C. § 1301(a), GAO Reimbursement Doctrine</p>
        `;
        document.getElementById('memoContent').innerHTML = memoHTML;
    }
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function markEDCSMustPay(itemName) {
    const confirmation = confirm(`Legal Determination:\n\n"EDCS must pay for this item pursuant to appropriations requirements. This determination reflects legal interpretation only and does not constitute certification or approval of payment."\n\nThis will:\n✓ Lock classification to EDCS\n✓ Create legal interpretation record\n✓ Prevent reclassification\n\nConfirm?`);
    
    if (confirmation) {
        alert(`✓ Legal determination recorded for: ${itemName}\n\nClassification locked to EDCS.\nCertifying officers are protected under 31 U.S.C. § 3528.`);
    }
}

function downloadAllocation() {
    alert('In production, this would generate a PDF report containing:\n\n✓ Allocation summary\n✓ Line item breakdown\n✓ Legal authorities cited\n✓ Certifying officer statement\n✓ Audit trail');
}

function routeToLegal() {
    alert('In production, this would:\n\n✓ Package flagged items\n✓ Include system logic applied\n✓ Attach source documents\n✓ Reference authorities\n✓ Route to Office of Legal Adviser (L/M)\n\nLegal will review and provide determination under 31 U.S.C. § 3529.');
}

function downloadMemo() {
    alert('In production, this would generate the DP → EDCS reimbursement memo as a Word document with:\n\n✓ Allocation breakdown\n✓ Legal authorities\n✓ Signature blocks\n✓ Accounting references');
}
