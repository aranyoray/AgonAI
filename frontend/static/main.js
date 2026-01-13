async function runSimulation() {
  const agentInputs = Array.from(document.querySelectorAll('.agent'));
  const agents = agentInputs.filter(a => a.checked).map(a => a.value);
  const topic = document.getElementById('topic').value.trim();
  const rounds = parseInt(document.getElementById('rounds').value, 10) || 12;
  const summaryOnly = document.getElementById('summaryOnly').checked;
  const useOllama = document.getElementById('useOllama').checked;
  const baseUrl = document.getElementById('baseUrl').value.trim() || undefined;
  const model = document.getElementById('model').value.trim() || undefined;

  const resultsEl = document.getElementById('results');
  resultsEl.textContent = 'Running...';

  try {
    const resp = await fetch('/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agents, topic, rounds, summaryOnly, useOllama, baseUrl, model })
    });

    const data = await resp.json();
    if (!resp.ok) {
      resultsEl.textContent = JSON.stringify(data, null, 2);
      return;
    }

    resultsEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultsEl.textContent = String(err);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('runBtn').addEventListener('click', runSimulation);
});
