/* AgonAI Frontend - Chat-based debate interface */

const AGENT_COLORS = {
  'Adolf Hitler': '#e11d48',
  'Mahatma Gandhi': '#22c55e',
  'Muhammad Ali Jinnah': '#38bdf8',
  'Rational Agent': '#8b5cf6',
  'Rational-A': '#8b5cf6',
  'Rational-B': '#a78bfa',
  'Empathetic Agent': '#f59e0b',
  'Empathetic-A': '#f59e0b',
  'Empathetic-B': '#fbbf24',
  'Low-Empathy': '#ef4444',
  'High-Empathy': '#10b981',
  'Rational': '#8b5cf6',
  'Empathetic': '#f59e0b',
};

function getAgentColor(name) {
  return AGENT_COLORS[name] || '#6366f1';
}

function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
}

function renderChatMessages(container, messages) {
  container.innerHTML = '';
  messages.forEach((msg) => {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    const color = getAgentColor(msg.speaker);
    bubble.innerHTML = `
      <div class="chat-avatar" style="background:${color}">${getInitials(msg.speaker)}</div>
      <div class="chat-body">
        <div class="chat-speaker" style="color:${color}">${msg.speaker} <span class="chat-round">Round ${msg.round}</span></div>
        <div class="chat-text">${msg.content.replace(/\n/g, '<br>')}</div>
      </div>
    `;
    container.appendChild(bubble);
  });
  container.scrollTop = container.scrollHeight;
}

function renderStats(container, data) {
  const empathyHtml = data.empathyRatios
    ? Object.entries(data.empathyRatios).map(([name, val]) =>
        `<span class="stat-chip"><b>${name}</b> empathy: ${val}</span>`
      ).join('')
    : '';
  container.innerHTML = `
    <div class="stats-row">
      <span class="stat-chip status-${data.status}">${data.status}</span>
      <span class="stat-chip">Consensus: ${data.consensusScore}</span>
      <span class="stat-chip">Rounds: ${data.rounds}</span>
      <span class="stat-chip">Duration: ${data.durationMinutes}m</span>
      ${empathyHtml}
    </div>
  `;
}

function renderPolicyScores(container, scores) {
  if (!scores) { container.style.display = 'none'; return; }
  container.style.display = '';
  let html = '';
  for (const [name, card] of Object.entries(scores)) {
    const color = getAgentColor(name);
    const cs = card.cumulative_scores || {};
    html += `
      <div class="score-card">
        <h3 style="color:${color}">${name}</h3>
        <div class="score-dims">
          ${renderDim('Political', cs.political)}
          ${renderDim('Economic', cs.economic)}
          ${renderDim('Social', cs.social)}
        </div>
        <div class="score-meta">
          <span>Objective: <b>${card.final_objective}</b></span>
          <span>Fatigue: ${card.fatigue}</span>
          <span>Empathy bonus: ${card.empathy_bonus}</span>
          <span>Penalties: ${card.penalties}</span>
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

function renderDim(label, dim) {
  if (!dim) return '';
  const netClass = dim.net >= 0 ? 'positive' : 'negative';
  return `
    <div class="dim">
      <span class="dim-label">${label}</span>
      <span class="dim-bar">
        <span class="bar-benefit" style="width:${Math.min(dim.benefit, 100)}%"></span>
        <span class="bar-cost" style="width:${Math.min(dim.cost, 100)}%"></span>
      </span>
      <span class="dim-net ${netClass}">${dim.net > 0 ? '+' : ''}${dim.net}</span>
    </div>
  `;
}

async function runSimulation() {
  const agentInputs = Array.from(document.querySelectorAll('.agent'));
  const agents = agentInputs.filter(a => a.checked).map(a => a.value);
  const topicSelect = document.getElementById('topicSelect').value;
  const topicInput = document.getElementById('topic').value.trim();
  const topic = topicSelect === 'custom' ? topicInput : topicSelect;
  const rounds = parseInt(document.getElementById('rounds').value, 10) || 12;
  const summaryOnly = document.getElementById('summaryOnly').checked;
  const useOllama = document.getElementById('useOllama').checked;
  const baseUrl = document.getElementById('baseUrl').value.trim() || undefined;
  const model = document.getElementById('model').value.trim() || undefined;
  const sessionId = window.localStorage.getItem('sessionId') || undefined;

  const resultsEl = document.getElementById('results');
  const chatPanel = document.getElementById('chatPanel');
  const chatContainer = document.getElementById('chatContainer');
  const chatStats = document.getElementById('chatStats');
  const scoresPanel = document.getElementById('scoresPanel');
  const scoresGrid = document.getElementById('scoresGrid');

  resultsEl.textContent = 'Running...';
  chatPanel.style.display = 'none';
  scoresPanel.style.display = 'none';

  if (agents.length < 2) {
    resultsEl.textContent = 'Error: Select at least 2 agents.';
    return;
  }

  try {
    const resp = await fetch('/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agents, topic, rounds, summaryOnly, useOllama, baseUrl, model, sessionId })
    });

    const data = await resp.json();
    if (!resp.ok) {
      resultsEl.textContent = JSON.stringify(data, null, 2);
      return;
    }

    if (data.sessionId) {
      window.localStorage.setItem('sessionId', data.sessionId);
    }

    // Show chat interface
    if (data.chatMessages && data.chatMessages.length > 0) {
      chatPanel.style.display = '';
      renderChatMessages(chatContainer, data.chatMessages);
      renderStats(chatStats, data);
    }

    // Show policy scores
    if (data.policyScores) {
      scoresPanel.style.display = '';
      renderPolicyScores(scoresGrid, data.policyScores);
    }

    resultsEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultsEl.textContent = String(err);
  }
}

async function runExperiment() {
  const expId = parseInt(document.getElementById('expSelect').value, 10);
  const topic = document.getElementById('expTopic').value;
  const maxRounds = parseInt(document.getElementById('expRounds').value, 10) || 15;
  const histAgents = Array.from(document.querySelectorAll('.exp-agent'))
    .filter(a => a.checked).map(a => a.value);

  const expResults = document.getElementById('expResults');
  const expStats = document.getElementById('expStats');
  const expChat = document.getElementById('expChat');
  const expJson = document.getElementById('expJson');

  expResults.style.display = 'none';
  expJson.textContent = 'Running experiment...';
  expResults.style.display = '';

  try {
    const resp = await fetch('/experiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        experimentId: expId,
        topic,
        maxRounds,
        historicalAgents: histAgents,
      })
    });
    const data = await resp.json();

    // Stats
    expStats.innerHTML = `
      <div class="stats-row">
        <span class="stat-chip">${data.experiment}</span>
        <span class="stat-chip status-${data.status}">${data.status}</span>
        <span class="stat-chip">Consensus: ${data.consensus_score}</span>
        <span class="stat-chip">Rounds: ${data.rounds_played}</span>
        ${data.convergence_round ? `<span class="stat-chip">Converged: Round ${data.convergence_round}</span>` : ''}
        ${Object.entries(data.empathy_ratios || {}).map(([n, v]) =>
          `<span class="stat-chip"><b>${n}</b> empathy: ${v}</span>`
        ).join('')}
      </div>
    `;

    // Judge verdict
    if (data.judge_verdict) {
      const jv = data.judge_verdict;
      let judgeHtml = '<div class="judge-verdict">';
      judgeHtml += '<h4>Judge Verdict</h4>';
      judgeHtml += `<p><b>Winner:</b> ${jv.winner || 'No clear winner'} (margin: ${jv.margin})</p>`;
      judgeHtml += `<p><b>Convergence:</b> ${jv.convergence_round ? 'Round ' + jv.convergence_round : 'None'} (metric: ${jv.convergence_metric})</p>`;
      if (jv.recommendations) {
        judgeHtml += '<ul>' + jv.recommendations.map(r => `<li>${r}</li>`).join('') + '</ul>';
      }
      judgeHtml += '</div>';
      expChat.innerHTML = judgeHtml;
    } else {
      expChat.innerHTML = '';
    }

    expJson.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    expJson.textContent = String(err);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('runBtn').addEventListener('click', runSimulation);
  document.getElementById('runExpBtn').addEventListener('click', runExperiment);

  // Topic select sync
  document.getElementById('topicSelect').addEventListener('change', (e) => {
    if (e.target.value !== 'custom') {
      document.getElementById('topic').value = e.target.value;
    }
  });

  // Jump buttons
  document.getElementById('jumpToConfig').addEventListener('click', () => {
    document.getElementById('configPanel').scrollIntoView({ behavior: 'smooth' });
  });
  document.getElementById('jumpToExperiments').addEventListener('click', () => {
    document.getElementById('experimentPanel').scrollIntoView({ behavior: 'smooth' });
  });

  // Agent profile on map
  const agentData = {
    hitler: {
      name: 'Adolf Hitler',
      origin: 'Germany',
      bio: 'Authoritarian nationalist persona with low cooperativeness and rigid red lines on territorial control.',
      tags: ['Dominance: High', 'Cooperativeness: Low', 'Ideology: Fascism'],
      avatarClass: 'avatar-hitler',
      initials: 'AH',
      focusPrompt: 'Begin with a guarded, high-stakes negotiation framing about sovereignty.'
    },
    gandhi: {
      name: 'Mahatma Gandhi',
      origin: 'India',
      bio: 'Nonviolent negotiator emphasizing moral appeals, empathy-weighted memory, and consensus building.',
      tags: ['Justice: High', 'Cooperativeness: High', 'Ideology: Nonviolence'],
      avatarClass: 'avatar-gandhi',
      initials: 'MG',
      focusPrompt: 'Open with a compassion-forward dialogue on shared humanitarian goals.'
    },
    jinnah: {
      name: 'Muhammad Ali Jinnah',
      origin: 'Pakistan',
      bio: 'Strategic constitutionalist balancing pragmatism with assertive negotiation over autonomy and rights.',
      tags: ['Assertiveness: High', 'Pragmatism: Medium', 'Ideology: Muslim Nationalism'],
      avatarClass: 'avatar-jinnah',
      initials: 'MJ',
      focusPrompt: 'Frame a legalistic discussion about self-determination and governance safeguards.'
    }
  };

  const profileName = document.getElementById('profileName');
  const profileOrigin = document.getElementById('profileOrigin');
  const profileBio = document.getElementById('profileBio');
  const profileTags = document.getElementById('profileTags');
  const profileAvatar = document.getElementById('profileAvatar');
  const addToDebateBtn = document.getElementById('addToDebate');
  const focusChatBtn = document.getElementById('focusChat');
  let activeAgentKey = null;

  function setProfile(agentKey) {
    const data = agentData[agentKey];
    if (!data) return;
    activeAgentKey = agentKey;
    profileName.textContent = data.name;
    profileOrigin.textContent = `Origin: ${data.origin}`;
    profileBio.textContent = data.bio;
    profileAvatar.className = `avatar ${data.avatarClass}`;
    profileAvatar.textContent = data.initials;
    profileTags.innerHTML = '';
    data.tags.forEach(tag => {
      const chip = document.createElement('span');
      chip.textContent = tag;
      profileTags.appendChild(chip);
    });
    addToDebateBtn.disabled = false;
    focusChatBtn.disabled = false;
  }

  document.querySelectorAll('.agent-marker').forEach(marker => {
    const agentKey = marker.dataset.agent;
    marker.addEventListener('mouseenter', () => setProfile(agentKey));
    marker.addEventListener('focus', () => setProfile(agentKey));
    marker.addEventListener('click', () => {
      setProfile(agentKey);
      toggleAgent(agentKey, true);
    });
  });

  addToDebateBtn.addEventListener('click', () => {
    if (!activeAgentKey) return;
    toggleAgent(activeAgentKey, true);
    document.getElementById('configPanel').scrollIntoView({ behavior: 'smooth' });
  });

  focusChatBtn.addEventListener('click', () => {
    if (!activeAgentKey) return;
    const prompt = agentData[activeAgentKey]?.focusPrompt;
    if (prompt) {
      document.getElementById('topic').value = prompt;
      document.getElementById('topicSelect').value = 'custom';
    }
    toggleAgent(activeAgentKey, true);
    document.getElementById('configPanel').scrollIntoView({ behavior: 'smooth' });
  });

  function toggleAgent(agentKey, shouldSelect) {
    const checkbox = document.querySelector(`.agent[value="${agentKey}"]`);
    if (checkbox) {
      checkbox.checked = shouldSelect ?? !checkbox.checked;
    }
  }
});
