/* ============================================
   MedQuery — Chat Frontend Logic
   ============================================ */

let selectedCategory = "All";
let totalAsked  = 0;
let confScores  = [];

const messagesEl  = document.getElementById("messages");
const userInputEl = document.getElementById("userInput");
const sendBtnEl   = document.getElementById("sendBtn");

// ---- Auto-resize textarea ----
userInputEl.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 130) + "px";
});

// ---- Enter to send ----
userInputEl.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ---- Category sidebar ----
document.querySelectorAll(".cat-btn").forEach(btn => {
    btn.addEventListener("click", function () {

        document.querySelectorAll(".cat-btn")
            .forEach(b => b.classList.remove("active"));

        this.classList.add("active");

        selectedCategory = this.dataset.cat;

        const pill = document.getElementById("activeCatPill");

        if (pill) {
            pill.textContent =
                selectedCategory === "All"
                    ? "All Categories"
                    : selectedCategory;
        }
    });
});
// ---- Sidebar search: prefill input ----
document.getElementById("sidebarSearch").addEventListener("input", function () {
  const val = this.value.trim();
  if (val) userInputEl.value = val;
});

// ---- Suggestion chips ----
function askFromChip(btn) {
  userInputEl.value = btn.textContent.trim();
  sendMessage();
}

// ---- Main send function ----
function sendMessage() {
  const query = userInputEl.value.trim();
  if (!query) return;

  userInputEl.value = "";
  userInputEl.style.height = "";
  sendBtnEl.disabled = true;

  appendUserMsg(query);
  showTyping();

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, category: selectedCategory })
  })
    .then(res => res.json())
    .then(data => {
      removeTyping();
      totalAsked++;
      if (data.matched) {
        confScores.push(data.score);
        appendBotAnswer(data);
      } else {
        appendBotError(data.message);
      }
      updateStats();
      sendBtnEl.disabled = false;
    })
    .catch(() => {
      removeTyping();
      appendBotError("Server error. Please make sure Flask is running.");
      sendBtnEl.disabled = false;
    });
}

// ---- Append user message ----
function appendUserMsg(text) {
  const div = document.createElement("div");
  div.className = "msg user";
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
    <div class="msg-content">
      <div class="bubble user-bubble">${escHtml(text)}</div>
    </div>`;
  messagesEl.appendChild(div);
  localStorage.setItem(
    "chatHistory",
    messagesEl.innerHTML
);
  scrollBottom();
}

// ---- Append bot answer ----
function appendBotAnswer(data) {
  const { answer, confidence, score, alternatives, related } = data;
  const confClass = { High: "badge-high", Medium: "badge-mid", Low: "badge-low", None: "badge-none" }[confidence] || "badge-none";
  const barPct    = Math.min(100, Math.round(score * 300));

  let altHTML = "";
  if (alternatives && alternatives.length) {
    altHTML = `
      <div class="alternatives">
        <div class="alt-label">Also possibly relevant</div>
        ${alternatives.map(a => `
          <div class="alt-item">
            <i class="fa-solid fa-angle-right" style="margin-top:3px;color:var(--muted)"></i>
            <span>${escHtml(a.question)}</span>
          </div>`).join("")}
      </div>`;
  }

  let relHTML = "";
  if (related && related.length) {
    relHTML = `
      <div class="related-chips">
        ${related.map(r => `
          <button class="rel-chip" onclick="askFromChipText('${escAttr(r.question)}')">
            <i class="fa-solid fa-arrow-right"></i> ${escHtml(r.question.length > 40 ? r.question.slice(0, 40) + "…" : r.question)}
          </button>`).join("")}
      </div>`;
  }

  const div = document.createElement("div");
  div.className = "msg bot";
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="msg-content">
      <div class="bubble bot-bubble">
        <div class="answer-cat">
          <i class="fa-solid fa-folder-open"></i> ${escHtml(answer.category)}
        </div>
        <div class="answer-q">${escHtml(answer.question)}</div>
        <div class="answer-text">${escHtml(answer.answer)}</div>
        <div class="conf-bar-wrap conf-${confidence.toLowerCase()}">
          <div class="conf-bar-label">
            <span>Match confidence</span>
            <span>${confidence} · ${barPct}%</span>
          </div>
          <div class="conf-bar">
            <div class="conf-bar-fill" style="width:${barPct}%"></div>
          </div>
        </div>
        ${altHTML}
      </div>
      <div class="msg-meta">
        <span class="conf-badge ${confClass}">${confidence} confidence</span>
        <span style="font-family:var(--mono);font-size:10px">FAQ #${answer.id}</span>
      </div>
      ${relHTML}
    </div>`;
  messagesEl.appendChild(div);
  localStorage.setItem(
    "chatHistory",
    messagesEl.innerHTML
);
  scrollBottom();
}

// ---- Append error/no-match ----
function appendBotError(message) {
  const div = document.createElement("div");
  div.className = "msg bot";
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="msg-content">
      <div class="bubble bot-bubble" style="color:var(--muted)">
        <i class="fa-solid fa-circle-exclamation" style="color:var(--amber);margin-right:6px"></i>
        ${escHtml(message)}
      </div>
    </div>`;
  messagesEl.appendChild(div);
  localStorage.setItem(
    "chatHistory",
    messagesEl.innerHTML
);
  scrollBottom();
}

// ---- Typing indicator ----
function showTyping() {
  const div = document.createElement("div");
  div.className = "msg bot";
  div.id = "typingIndicator";
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="msg-content">
      <div class="bubble bot-bubble">
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>`;
  messagesEl.appendChild(div);
  localStorage.setItem(
    "chatHistory",
    messagesEl.innerHTML
);
  scrollBottom();
}

function removeTyping() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

// ---- Stats update ----
function updateStats() {
  document.getElementById("statAsked").textContent = totalAsked;
  if (confScores.length) {
    const avg = Math.round(confScores.reduce((a, b) => a + b, 0) / confScores.length * 100);
    document.getElementById("statConf").textContent = avg + "%";
  }
}

// ---- Helpers ----
function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escAttr(str) {
    return String(str)
        .replace(/'/g, "\\'")
        .replace(/"/g, "&quot;");
}

function askFromChipText(text) {
  userInputEl.value = text;
  sendMessage();
  
}
// Click related question
function askRelatedQuestion(question) {
  userInputEl.value = question;
  sendMessage();
}
window.onload = function ()  {
    const savedChat = localStorage.getItem("chatHistory");

    if (savedChat) {
        messagesEl.innerHTML = savedChat;
        localStorage.setItem(
    "chatHistory",
    messagesEl.innerHTML
);
    }
};
function clearChat() {
    localStorage.removeItem("chatHistory");
    location.reload();
}