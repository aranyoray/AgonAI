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
  const jumpToConfigBtn = document.getElementById('jumpToConfig');
  let activeAgentKey = null;

  function setProfile(agentKey) {
    const data = agentData[agentKey];
    if (!data) {
      return;
    }
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
    }
    toggleAgent(activeAgentKey, true);
    document.getElementById('configPanel').scrollIntoView({ behavior: 'smooth' });
  });

  jumpToConfigBtn.addEventListener('click', () => {
    document.getElementById('configPanel').scrollIntoView({ behavior: 'smooth' });
  });

  function toggleAgent(agentKey, shouldSelect) {
    const checkbox = document.querySelector(`.agent[value="${agentKey}"]`);
    if (checkbox) {
      checkbox.checked = shouldSelect ?? !checkbox.checked;
    }
  }
});
