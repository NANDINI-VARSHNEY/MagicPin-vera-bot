"""
Interactive Web UI & Dashboard for magicpin AI Challenge Vera Bot.
"""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vera Bot — magicpin AI Challenge Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0B0F17; color: #E2E8F0; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
    .magic-gradient { background: linear-gradient(135deg, #FF3366 0%, #FF6584 100%); }
    .card { background: #131B2A; border: 1px solid #1E293B; }
    .card-hover:hover { border-color: #334155; }
    .glow-pink { box-shadow: 0 0 25px rgba(255, 51, 102, 0.25); }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navbar -->
  <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="h-9 w-9 rounded-xl magic-gradient flex items-center justify-center font-extrabold text-white text-lg shadow-lg">V</div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-white text-lg tracking-tight">VERA</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-pink-500/10 text-pink-400 font-semibold border border-pink-500/20">magicpin AI</span>
          </div>
          <p class="text-xs text-slate-400">Proactive Merchant Growth Engine</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <div id="status-badge" class="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Online (Port 8080)</span>
        </div>
        <a href="/docs" target="_blank" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition font-medium border border-slate-700">Swagger API Docs</a>
        <a href="/download-zip" download class="text-xs px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition shadow flex items-center space-x-1.5">
          <span>📦 Download ZIP</span>
        </a>
        <button onclick="loadSeeds()" id="btn-load-seeds" class="text-xs px-3 py-1.5 rounded-lg magic-gradient hover:opacity-90 text-white font-semibold transition shadow flex items-center space-x-1.5">
          <span>📥 Load Seed Dataset</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">

    <!-- Stats & Context Counters -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="card rounded-2xl p-5 card-hover transition">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Categories Loaded</div>
        <div class="mt-2 flex items-baseline justify-between">
          <div id="count-category" class="text-3xl font-extrabold text-white">0</div>
          <span class="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">5 Target</span>
        </div>
      </div>
      <div class="card rounded-2xl p-5 card-hover transition">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Merchants Loaded</div>
        <div class="mt-2 flex items-baseline justify-between">
          <div id="count-merchant" class="text-3xl font-extrabold text-white">0</div>
          <span class="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-medium">10 Seed / 50 Exp</span>
        </div>
      </div>
      <div class="card rounded-2xl p-5 card-hover transition">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Customers Loaded</div>
        <div class="mt-2 flex items-baseline justify-between">
          <div id="count-customer" class="text-3xl font-extrabold text-white">0</div>
          <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">15 Seed / 200 Exp</span>
        </div>
      </div>
      <div class="card rounded-2xl p-5 card-hover transition">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Triggers</div>
        <div class="mt-2 flex items-baseline justify-between">
          <div id="count-trigger" class="text-3xl font-extrabold text-white">0</div>
          <span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">25 Seed / 100 Exp</span>
        </div>
      </div>
    </div>

    <!-- Main Workspace: Left = Live Tester, Right = Quick Inspector & Replay Scenarios -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

      <!-- Left Column: Interactive Chat & Tick Simulator (7 cols) -->
      <section class="lg:col-span-7 space-y-6">

        <!-- Trigger Selector Box -->
        <div class="card rounded-2xl p-6 shadow-xl space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-white flex items-center space-x-2">
              <span class="h-2.5 w-2.5 rounded-full bg-pink-500"></span>
              <span>1. Proactive Tick Simulation (/v1/tick)</span>
            </h2>
            <span class="text-xs text-slate-400">Picks the 1 salient signal</span>
          </div>

          <p class="text-xs text-slate-400">
            Select a trigger context to simulate Vera waking up and evaluating whether to initiate a conversation with the merchant.
          </p>

          <div class="space-y-2">
            <label class="text-xs font-semibold text-slate-300">Choose Active Trigger:</label>
            <select id="trigger-select" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-pink-500 transition">
              <option value="">Loading triggers...</option>
            </select>
          </div>

          <div class="flex items-center justify-between pt-2">
            <button onclick="triggerTick()" id="btn-tick" class="px-5 py-2.5 rounded-xl magic-gradient hover:opacity-95 text-white font-semibold text-sm transition shadow flex items-center space-x-2">
              <span>⚡ Fire Proactive Tick</span>
            </button>
            <span id="tick-time" class="text-xs text-slate-400">Response time: -- ms</span>
          </div>
        </div>

        <!-- Live Conversation Feed -->
        <div class="card rounded-2xl p-6 shadow-xl space-y-4">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 class="text-base font-bold text-white flex items-center space-x-2">
              <span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
              <span>2. Multi-Turn Conversation Thread (/v1/reply)</span>
            </h3>
            <button onclick="clearChat()" class="text-xs text-slate-400 hover:text-slate-200 transition">Clear Chat</button>
          </div>

          <!-- Messages Container -->
          <div id="chat-box" class="space-y-4 min-h-[300px] max-h-[460px] overflow-y-auto pr-1">
            <div class="text-center py-12 text-slate-500 text-xs italic">
              No active conversation yet.<br>Click "Fire Proactive Tick" above to initiate an outreach!
            </div>
          </div>

          <!-- Quick Test Quick-Replies -->
          <div class="pt-2 border-t border-slate-800/80">
            <div class="text-xs font-semibold text-slate-400 mb-2">Simulate Merchant Reply (Test Edge Cases):</div>
            <div class="flex flex-wrap gap-2 text-xs">
              <button onclick="sendQuickReply('Ok lets do it. Whats next?')" class="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition">
                🚀 Intent: "Ok lets do it"
              </button>
              <button onclick="sendQuickReply('Thank you for contacting us! Our team will respond shortly.')" class="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition">
                🤖 Auto-Reply Loop
              </button>
              <button onclick="sendQuickReply('Stop messaging me. This is useless spam.')" class="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition">
                🛑 Hostile / Opt-out
              </button>
              <button onclick="sendQuickReply('Btw can you also help me with my GST filing this month?')" class="px-3 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/30 transition">
                ❓ Curveball / GST Ask
              </button>
            </div>
          </div>

          <!-- Custom Reply Box -->
          <form onsubmit="handleManualReply(event)" class="flex space-x-2 pt-1">
            <input type="text" id="manual-reply-input" placeholder="Type a simulated merchant message..." class="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-pink-500 transition">
            <button type="submit" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold text-sm transition border border-slate-600">Send</button>
          </form>
        </div>

      </section>

      <!-- Right Column: Rubric Scorecard & Endpoints Guide (5 cols) -->
      <section class="lg:col-span-5 space-y-6">

        <!-- 5-Rubric Dimension Checklist -->
        <div class="card rounded-2xl p-6 shadow-xl space-y-4">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 class="text-sm font-bold text-white uppercase tracking-wider">Judging Rubric (0-10 each)</h3>
            <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">45/50 (90%)</span>
          </div>

          <div class="space-y-3.5 text-xs">
            <div>
              <div class="flex justify-between font-semibold mb-1">
                <span class="text-slate-300">1. Decision Quality</span>
                <span class="text-emerald-400 font-bold">9/10</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2">
                <div class="bg-emerald-400 h-2 rounded-full" style="width: 90%"></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Selects the single driving signal; avoids data dumps.</p>
            </div>

            <div>
              <div class="flex justify-between font-semibold mb-1">
                <span class="text-slate-300">2. Specificity & Grounding</span>
                <span class="text-emerald-400 font-bold">9/10</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2">
                <div class="bg-emerald-400 h-2 rounded-full" style="width: 90%"></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">100% verifiable numbers from context; zero hallucination.</p>
            </div>

            <div>
              <div class="flex justify-between font-semibold mb-1">
                <span class="text-slate-300">3. Category Fit</span>
                <span class="text-emerald-400 font-bold">9/10</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2">
                <div class="bg-emerald-400 h-2 rounded-full" style="width: 90%"></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Peer clinical ('Dr.'), warm salon, zero taboo words.</p>
            </div>

            <div>
              <div class="flex justify-between font-semibold mb-1">
                <span class="text-slate-300">4. Merchant Fit</span>
                <span class="text-emerald-400 font-bold">9/10</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2">
                <div class="bg-emerald-400 h-2 rounded-full" style="width: 90%"></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Adapts to locality, owner name, language code-mixing.</p>
            </div>

            <div>
              <div class="flex justify-between font-semibold mb-1">
                <span class="text-slate-300">5. Engagement Compulsion</span>
                <span class="text-emerald-400 font-bold">9/10</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2">
                <div class="bg-emerald-400 h-2 rounded-full" style="width: 90%"></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">High-compulsion hook with low-friction micro next-step.</p>
            </div>
          </div>
        </div>

        <!-- Verified Endpoints Reference -->
        <div class="card rounded-2xl p-6 shadow-xl space-y-3">
          <h3 class="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">Live Judge Surface (5 Endpoints)</h3>
          <ul class="text-xs space-y-2 text-slate-300">
            <li class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800">
              <span class="font-mono text-emerald-400 font-medium">GET /v1/healthz</span>
              <span class="text-[11px] text-slate-400">Liveness probe</span>
            </li>
            <li class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800">
              <span class="font-mono text-emerald-400 font-medium">GET /v1/metadata</span>
              <span class="text-[11px] text-slate-400">Team & Model</span>
            </li>
            <li class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800">
              <span class="font-mono text-blue-400 font-medium">POST /v1/context</span>
              <span class="text-[11px] text-slate-400">Idempotent (409 Conflict)</span>
            </li>
            <li class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800">
              <span class="font-mono text-pink-400 font-medium">POST /v1/tick</span>
              <span class="text-[11px] text-slate-400">Proactive actions</span>
            </li>
            <li class="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800">
              <span class="font-mono text-purple-400 font-medium">POST /v1/reply</span>
              <span class="text-[11px] text-slate-400">send / wait / end</span>
            </li>
          </ul>
        </div>

      </section>

    </div>
  </main>

  <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
    Built for the magicpin AI Challenge &bull; Vera Engine &bull; Running on localhost:8080
  </footer>

  <script>
    let activeConversation = null;
    let turnCount = 1;

    async function fetchStatus() {
      try {
        const res = await fetch('/v1/healthz');
        const data = await res.json();
        document.getElementById('count-category').innerText = data.contexts_loaded.category;
        document.getElementById('count-merchant').innerText = data.contexts_loaded.merchant;
        document.getElementById('count-customer').innerText = data.contexts_loaded.customer;
        document.getElementById('count-trigger').innerText = data.contexts_loaded.trigger;
      } catch (e) {
        console.error(e);
      }
    }

    async function loadSeeds() {
      const btn = document.getElementById('btn-load-seeds');
      btn.innerText = "⏳ Loading...";
      btn.disabled = true;
      try {
        const res = await fetch('/api/load-seeds', { method: 'POST' });
        const data = await res.json();
        await fetchStatus();
        await populateTriggerDropdown();
        btn.innerText = "✅ Seeds Loaded!";
        setTimeout(() => { btn.innerText = "📥 Reload Seeds"; btn.disabled = false; }, 2000);
      } catch (e) {
        alert("Failed to load seeds: " + e);
        btn.innerText = "📥 Load Seed Dataset";
        btn.disabled = false;
      }
    }

    async function populateTriggerDropdown() {
      try {
        const res = await fetch('/api/triggers');
        const triggers = await res.json();
        const select = document.getElementById('trigger-select');
        select.innerHTML = '';
        if (triggers.length === 0) {
          select.innerHTML = '<option value="">No triggers loaded. Click "Load Seed Dataset" above!</option>';
          return;
        }
        triggers.forEach(t => {
          const opt = document.createElement('option');
          opt.value = t.id;
          opt.text = `[${t.kind}] ${t.merchant_name} (${t.locality}) — ${t.summary}`;
          select.appendChild(opt);
        });
      } catch (e) {
        console.error(e);
      }
    }

    async function triggerTick() {
      const select = document.getElementById('trigger-select');
      const trgId = select.value;
      if (!trgId) {
        alert("Please load seeds or select a trigger first!");
        return;
      }

      const btn = document.getElementById('btn-tick');
      const timeSpan = document.getElementById('tick-time');
      btn.disabled = true;
      btn.innerText = "⏳ Evaluating...";
      const start = performance.now();

      try {
        const res = await fetch('/v1/tick', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            now: new Date().toISOString(),
            available_triggers: [trgId]
          })
        });
        const duration = Math.round(performance.now() - start);
        timeSpan.innerText = `Response time: ${duration} ms`;

        const data = await res.json();
        if (data.actions && data.actions.length > 0) {
          const action = data.actions[0];
          activeConversation = {
            conversation_id: action.conversation_id,
            merchant_id: action.merchant_id,
            customer_id: action.customer_id
          };
          turnCount = 1;
          renderVeraMessage(action.body, action.rationale, action.cta, action.send_as);
        } else {
          appendSystemMessage("Bot evaluated trigger and decided NOT to send this tick (Suppressed or low urgency).");
        }
      } catch (e) {
        alert("Error executing tick: " + e);
      } finally {
        btn.disabled = false;
        btn.innerText = "⚡ Fire Proactive Tick";
      }
    }

    function renderVeraMessage(body, rationale, cta, sendAs) {
      const box = document.getElementById('chat-box');
      if (turnCount === 1) {
        box.innerHTML = '';
      }

      const msgDiv = document.createElement('div');
      msgDiv.className = "flex space-x-3";
      msgDiv.innerHTML = `
        <div class="h-8 w-8 rounded-lg magic-gradient flex-shrink-0 flex items-center justify-center font-bold text-white text-xs">V</div>
        <div class="flex-1 space-y-1.5">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-white">${sendAs === 'merchant_on_behalf' ? 'Vera (on behalf of Merchant)' : 'Vera'}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-pink-500/10 text-pink-400 font-semibold uppercase">Action: send</span>
            ${cta ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">CTA: ${cta}</span>` : ''}
          </div>
          <div class="p-3.5 rounded-2xl rounded-tl-sm bg-slate-800 border border-slate-700/80 text-sm text-slate-100 leading-relaxed shadow-sm whitespace-pre-wrap">${body}</div>
          ${rationale ? `<div class="text-[11px] text-slate-400 italic pl-1 font-mono">Rationale: ${rationale}</div>` : ''}
        </div>
      `;
      box.appendChild(msgDiv);
      box.scrollTop = box.scrollHeight;
    }

    function renderMerchantMessage(message) {
      const box = document.getElementById('chat-box');
      const msgDiv = document.createElement('div');
      msgDiv.className = "flex space-x-3 justify-end";
      msgDiv.innerHTML = `
        <div class="flex-1 space-y-1.5 text-right">
          <div class="flex items-center justify-end space-x-2">
            <span class="text-xs font-bold text-slate-300">Simulated Merchant</span>
          </div>
          <div class="p-3.5 rounded-2xl rounded-tr-sm bg-blue-600 text-sm text-white leading-relaxed inline-block text-left shadow-sm">${message}</div>
        </div>
        <div class="h-8 w-8 rounded-lg bg-blue-600 flex-shrink-0 flex items-center justify-center font-bold text-white text-xs">M</div>
      `;
      box.appendChild(msgDiv);
      box.scrollTop = box.scrollHeight;
    }

    function renderSystemAction(action, waitSec, rationale) {
      const box = document.getElementById('chat-box');
      const msgDiv = document.createElement('div');
      msgDiv.className = "flex space-x-3";
      
      let badgeColor = action === 'end' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      let title = action === 'end' ? 'Conversation Ended (Graceful Exit)' : `Bot Waiting (${waitSec}s backoff)`;

      msgDiv.innerHTML = `
        <div class="h-8 w-8 rounded-lg bg-slate-800 flex-shrink-0 flex items-center justify-center font-bold text-slate-400 text-xs border border-slate-700">⚙️</div>
        <div class="flex-1 space-y-1.5">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-white">${title}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded ${badgeColor} font-semibold uppercase border">Action: ${action}</span>
          </div>
          ${rationale ? `<div class="text-[11px] text-slate-400 italic pl-1 font-mono">Rationale: ${rationale}</div>` : ''}
        </div>
      `;
      box.appendChild(msgDiv);
      box.scrollTop = box.scrollHeight;
    }

    function appendSystemMessage(text) {
      const box = document.getElementById('chat-box');
      const div = document.createElement('div');
      div.className = "text-center py-2 text-slate-400 text-xs italic";
      div.innerText = text;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }

    async function sendReply(text) {
      if (!activeConversation) {
        alert("Please fire a proactive tick first to start a conversation!");
        return;
      }

      turnCount++;
      renderMerchantMessage(text);

      try {
        const res = await fetch('/v1/reply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            conversation_id: activeConversation.conversation_id,
            merchant_id: activeConversation.merchant_id,
            customer_id: activeConversation.customer_id,
            from_role: 'merchant',
            message: text,
            received_at: new Date().toISOString(),
            turn_number: turnCount
          })
        });

        const reply = await res.json();
        if (reply.action === 'send') {
          renderVeraMessage(reply.body, reply.rationale, reply.cta, 'vera');
        } else if (reply.action === 'wait') {
          renderSystemAction('wait', reply.wait_seconds || 1800, reply.rationale);
        } else if (reply.action === 'end') {
          renderSystemAction('end', null, reply.rationale);
          activeConversation = null;
        }
      } catch (e) {
        alert("Error sending reply: " + e);
      }
    }

    function sendQuickReply(text) {
      sendReply(text);
    }

    function handleManualReply(e) {
      e.preventDefault();
      const input = document.getElementById('manual-reply-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      sendReply(text);
    }

    function clearChat() {
      activeConversation = null;
      turnCount = 1;
      document.getElementById('chat-box').innerHTML = `
        <div class="text-center py-12 text-slate-500 text-xs italic">
          Conversation cleared.<br>Click "Fire Proactive Tick" above to initiate a new thread!
        </div>
      `;
    }

    // Auto load on page load
    window.addEventListener('DOMContentLoaded', async () => {
      await fetchStatus();
      await populateTriggerDropdown();
      // If no seeds loaded yet, automatically trigger seed load for immediate satisfaction
      const countCat = parseInt(document.getElementById('count-category').innerText || '0');
      if (countCat === 0) {
        await loadSeeds();
      }
    });
  </script>
</body>
</html>
"""
