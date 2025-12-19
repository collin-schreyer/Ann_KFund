// K Fund Event Allocation Tool - JavaScript

const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8002'
    : '';

function addLineItem() {
    const container = document.getElementById('lineItemsInput');
    const row = document.createElement('div');
    row.className = 'line-item-row';
    row.style.cssText = 'display: flex; gap: 0.5rem; margin-bottom: 0.5rem;';
    row.innerHTML = `
        <input type="text" class="usa-textarea line-item-desc" style="min-height: auto; flex: 3;" placeholder="Description">
        <input type="number" class="usa-textarea line-item-cost" style="min-height: auto; flex: 1;" placeholder="Cost ($)">
        <button class="usa-button usa-button-secondary" style="padding: 0.5rem;" onclick="removeLineItem(this)">✕</button>
    `;
    container.appendChild(row);
}

function removeLineItem(btn) {
    const rows = document.querySelectorAll('.line-item-row');
    if (rows.length > 1) btn.parentElement.remove();
}

function getLineItems() {
    const rows = document.querySelectorAll('.line-item-row');
    const items = [];
    rows.forEach(row => {
        const desc = row.querySelector('.line-item-desc').value.trim();
        const cost = parseFloat(row.querySelector('.line-item-cost').value) || 0;
        if (desc && cost > 0) items.push({ item: desc, cost: cost });
    });
    return items;
}

async function processAllocation() {
    const eventName = document.getElementById('eventName').value.trim();
    const foreignGuests = parseInt(document.getElementById('foreignGuests').value) || 0;
    const totalGuests = parseInt(document.getElementById('totalGuests').value) || 0;
    const lineItems = getLineItems();

    if (!eventName) { alert('Please enter event name'); return; }
    if (lineItems.length === 0) { alert('Please add at least one line item'); return; }
    if (totalGuests === 0) { alert('Please enter total guests'); return; }

    const loadingText = document.querySelector('#loadingIndicator p');
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('processBtn').disabled = true;
    document.getElementById('results').classList.remove('show');

    try {
        // Stepped Loading Animation
        loadingText.textContent = "🔍 Scanning line items...";
        await new Promise(r => setTimeout(r, 800));

        loadingText.textContent = "📚 Checking K Fund regulations (22 U.S.C. § 2671)...";
        const fetchPromise = fetch(`${API_URL}/api/v1/classify-batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_name: eventName, foreign_guests: foreignGuests, total_guests: totalGuests, line_items: lineItems })
        });

        await new Promise(r => setTimeout(r, 1000)); // Minimum wait for readability
        loadingText.textContent = "💰 Calculating per-person cost caps...";

        const response = await fetchPromise;

        loadingText.textContent = "✨ Finalizing payer allocation...";
        await new Promise(r => setTimeout(r, 600));

        if (!response.ok) throw new Error((await response.json()).detail || 'Failed');
        displayResults(transformApiResponse(await response.json()));
    } catch (error) {
        let msg = error.message;
        if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
            msg = 'Cannot connect to AI server. Please run "sh prototype/start_api.sh" in your terminal to start the backend.';
        }
        alert('Error: ' + msg);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('processBtn').disabled = false;
    }
}

function transformApiResponse(data) {
    return {
        eventName: data.event_name,
        foreignGuests: data.foreign_guests,
        totalGuests: data.total_guests,
        foreignPercentage: data.foreign_percentage.toFixed(0),
        lineItems: data.line_items.map(item => ({
            item: item.item, cost: item.cost, kFundAmount: item.k_fund_amount,
            classification: item.classification, authority: item.authority,
            rationale: item.rationale, regulationText: item.regulation_text,
            confidence: item.confidence, prorated: item.prorated,
            legalReview: item.classification === 'LEGAL_REVIEW',
            questions: item.questions, sources: item.sources_consulted,
            payer: item.payer, flagged: item.flagged, flagReason: item.flag_reason,
            perPersonCost: item.per_person_cost
        })),
        allocations: { kFund: data.totals.k_fund, notAllowable: data.totals.not_allowable, legalReview: data.totals.legal_review },
        totalCost: data.totals.total
    };
}

function loadSampleData() {
    document.getElementById('eventName').value = "Reception for Ambassador of Franconia";
    document.getElementById('foreignGuests').value = "45";
    document.getElementById('totalGuests').value = "100";
    const container = document.getElementById('lineItemsInput');
    container.innerHTML = '';
    [
        { desc: "Crystal vase gift for Ambassador", cost: 2500 },
        { desc: "Reception catering", cost: 16000 }, // High cost to trigger cap
        { desc: "Floral centerpieces", cost: 1200 },
        { desc: "Printed programs", cost: 450 },
        { desc: "Luxury Yacht Rental", cost: 5000 }, // Prohibited item
        { desc: "Photography services", cost: 1500 },
        { desc: "String quartet", cost: 2000 }
    ].forEach(item => {
        const row = document.createElement('div');
        row.className = 'line-item-row';
        row.style.cssText = 'display: flex; gap: 0.5rem; margin-bottom: 0.5rem;';
        row.innerHTML = `<input type="text" class="usa-textarea line-item-desc" style="min-height: auto; flex: 3;" value="${item.desc}"><input type="number" class="usa-textarea line-item-cost" style="min-height: auto; flex: 1;" value="${item.cost}"><button class="usa-button usa-button-secondary" style="padding: 0.5rem;" onclick="removeLineItem(this)">✕</button>`;
        container.appendChild(row);
    });
}

function displayResults(data) {
    document.getElementById('results').classList.add('show');
    document.getElementById('allocationSummary').innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
            <div style="background: #e7f6f8; padding: 1.5rem; border-radius: 8px; text-align: center; border: 2px solid var(--primary);"><div style="font-size: 2rem; font-weight: 700; color: var(--primary);">$${data.allocations.kFund.toLocaleString()}</div><div style="font-weight: 600;">K Fund Allowable</div><div style="font-size: 0.9rem;">${((data.allocations.kFund / data.totalCost) * 100).toFixed(1)}%</div></div>
            <div style="background: #fce4e4; padding: 1.5rem; border-radius: 8px; text-align: center;"><div style="font-size: 2rem; font-weight: 700; color: #b50909;">$${data.allocations.notAllowable.toLocaleString()}</div><div style="font-weight: 600;">Not Allowable</div><div style="font-size: 0.9rem;">${((data.allocations.notAllowable / data.totalCost) * 100).toFixed(1)}%</div></div>
            <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; text-align: center;"><div style="font-size: 2rem; font-weight: 700; color: #936f38;">$${data.allocations.legalReview.toLocaleString()}</div><div style="font-weight: 600;">Legal Review</div><div style="font-size: 0.9rem;">${((data.allocations.legalReview / data.totalCost) * 100).toFixed(1)}%</div></div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: var(--base-lightest); border-radius: 4px;"><strong>Event:</strong> ${data.eventName} | <strong>Foreign Guests:</strong> ${data.foreignGuests}/${data.totalGuests} (${data.foreignPercentage}%) | <strong>Total:</strong> $${data.totalCost.toLocaleString()}</div>`;

    window.currentLineItems = data.lineItems;
    let tableHTML = '<table style="width: 100%; border-collapse: collapse;"><thead><tr style="background: var(--base-darker); color: white;"><th style="padding: 0.75rem; text-align: left;">Item</th><th style="padding: 0.75rem; text-align: right;">Cost</th><th style="padding: 0.75rem; text-align: left;">Who Pays?</th><th style="padding: 0.75rem; text-align: right;">K Fund</th><th style="padding: 0.75rem; text-align: center;">Status</th></tr></thead><tbody>';
    data.lineItems.forEach((item, i) => {
        const bg = i % 2 === 0 ? 'white' : 'var(--base-lightest)';
        const color = item.classification === 'K_FUND_ALLOWABLE' ? 'var(--primary)' : item.classification === 'NOT_ALLOWABLE' ? '#b50909' : '#936f38';
        const text = item.classification === 'K_FUND_ALLOWABLE' ? 'K Fund ✓' : item.classification === 'NOT_ALLOWABLE' ? 'Not Allowable' : 'Legal Review';
        const kf = item.classification === 'K_FUND_ALLOWABLE' ? `$${item.kFundAmount.toLocaleString()}${item.prorated ? '*' : ''}` : '-';

        let payerCell = `<span style="font-weight:600; color: #333;">${item.payer}</span>`;
        if (item.flagged) {
            payerCell += `<div style="color: #d54309; font-size: 0.8rem; margin-top: 0.2rem;">⚠️ ${item.flagReason}</div>`;
        }

        tableHTML += `<tr class="clickable-row" style="background: ${bg};" onclick="showAllowableModal(${i})"><td style="padding: 0.75rem;">${item.item}${item.sources ? `<br><small style="color: #666;">Sources: ${item.sources.join(', ')}</small>` : ''}</td><td style="padding: 0.75rem; text-align: right;">$${item.cost.toLocaleString()}</td><td style="padding: 0.75rem;">${payerCell}</td><td style="padding: 0.75rem; text-align: right; font-weight: 600;">${kf}</td><td style="padding: 0.75rem; text-align: center;"><span style="background: ${color}; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem;">${text}</span></td></tr>`;
    });
    tableHTML += '</tbody></table><p style="font-size: 0.85rem; color: var(--base-dark); margin-top: 0.5rem;">* Prorated based on foreign guest %</p>';
    document.getElementById('lineItemsTable').innerHTML = tableHTML;

    const legalItems = data.lineItems.filter(i => i.legalReview);
    if (legalItems.length > 0) {
        document.getElementById('legalReview').style.display = 'block';
        document.getElementById('legalItems').innerHTML = legalItems.map(item => `<div class="citation-item" style="border-left-color: var(--warning);"><div style="font-weight: 700;">${item.item} - $${item.cost.toLocaleString()}</div><div style="margin-top: 0.5rem;">${item.rationale}</div>${item.questions?.length ? `<ul style="margin-top: 0.5rem;">${item.questions.map(q => `<li>${q}</li>`).join('')}</ul>` : ''}</div>`).join('');
    } else {
        document.getElementById('legalReview').style.display = 'none';
    }
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function showAllowableModal(index) {
    const item = window.currentLineItems[index];
    const modal = document.getElementById('allowableModal');
    let title, body;
    if (item.classification === 'K_FUND_ALLOWABLE') {
        title = '✓ Why This Is K Fund Allowable';
        body = `<p><strong>Item:</strong> ${item.item}</p><p><strong>Amount:</strong> $${item.cost.toLocaleString()}${item.prorated ? ` (K Fund: $${item.kFundAmount.toLocaleString()})` : ''}</p><p><strong>Authority:</strong> ${item.authority}</p><p><strong>Confidence:</strong> ${item.confidence.toUpperCase()}</p><h4 style="margin-top: 1.5rem; color: var(--primary);">AI Analysis</h4><p>${item.rationale}</p>${item.regulationText ? `<div class="regulation-text">${item.regulationText}</div>` : ''}`;
    } else if (item.classification === 'NOT_ALLOWABLE') {
        title = '✗ Why This Is NOT Allowable';
        body = `<p><strong>Item:</strong> ${item.item}</p><p><strong>Amount:</strong> $${item.cost.toLocaleString()}</p><p><strong>Confidence:</strong> ${item.confidence.toUpperCase()}</p><h4 style="margin-top: 1.5rem; color: #b50909;">AI Analysis</h4><p>${item.rationale}</p>${item.regulationText ? `<div class="regulation-text" style="border-left-color: #b50909;">${item.regulationText}</div>` : ''}`;
    } else {
        title = '⚖️ Requires Legal Review';
        body = `<p><strong>Item:</strong> ${item.item}</p><p><strong>Amount:</strong> $${item.cost.toLocaleString()}</p><h4 style="margin-top: 1.5rem; color: #936f38;">AI Analysis</h4><p>${item.rationale}</p>${item.questions?.length ? `<h4>Questions to Resolve</h4><ul>${item.questions.map(q => `<li>${q}</li>`).join('')}</ul>` : ''}`;
    }
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = body;
    modal.style.display = 'flex';
}

function closeModal() { document.getElementById('allowableModal').style.display = 'none'; }
window.onclick = function (e) { if (e.target === document.getElementById('allowableModal')) closeModal(); }
function downloadAllocation() { alert('Download feature - would generate PDF report'); }
function routeToLegal() { alert('Route to Legal Adviser (L/M)'); }
