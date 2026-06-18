// =============================================
// TIPS — rotate every 4 seconds in the welcome banner
// =============================================
const tips = [
  "You can ask about the admission process",
  "Try asking: What programs does Kardan offer?",
  "Ask about library services and resources",
  "Find out about MBA or Data Science programs",
  "Ask: What are the admission requirements?",
  "Try: Tell me about Kardan University history",
  "Ask about campus addresses and locations",
  "Find out about civil engineering or law programs",
];

let tipIndex = 0;
const tipTextEl = document.getElementById("tipText");
const tipStripEl = tipTextEl ? tipTextEl.closest(".tip-strip") : null;

// Rotate tips every 4 seconds with a smooth fade-out → swap → fade-in effect
setInterval(() => {
  if (!tipStripEl || !tipTextEl) return;

  // Step 1: fade the strip out (CSS: opacity → 0)
  tipStripEl.classList.add("tip-fade");

  // Step 2: after the fade-out finishes (0.4s), swap the text and fade back in
  setTimeout(() => {
    tipIndex = (tipIndex + 1) % tips.length;
    tipTextEl.textContent = tips[tipIndex];
    tipStripEl.classList.remove("tip-fade");
  }, 420);
}, 4000);

// =============================================
// WELCOME BANNER — hide it the first time the user sends a message
// =============================================
let bannerVisible = true;

function hideBanner() {
  if (!bannerVisible) return;
  const banner = document.getElementById("welcomeBanner");
  if (banner) {
    // Fade out then remove from layout completely
    banner.style.transition = "opacity 0.3s ease";
    banner.style.opacity = "0";
    setTimeout(() => {
      banner.style.display = "none";
    }, 320);
  }
  bannerVisible = false;
}

// =============================================
// ENTER KEY — send message on Enter keypress
// =============================================
document.getElementById("userInput").addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});

// =============================================
// GET CURRENT TIME  →  "HH:MM"
// =============================================
function getCurrentTime() {
  const now = new Date();
  return (
    String(now.getHours()).padStart(2, "0") +
    ":" +
    String(now.getMinutes()).padStart(2, "0")
  );
}

// =============================================
// SEND MESSAGE
// =============================================
function sendMessage() {
  const inputEl = document.getElementById("userInput");
  const userText = inputEl.value.trim();
  if (!userText) return;

  inputEl.value = ""; // clear the input box
  hideBanner(); // hide the welcome banner on first message

  addMessage(userText, "user"); // add user bubble (right side)
  const typingId = showTyping(); // show three-dot animation
  fetchReply(userText, typingId); // call Flask API
}

// =============================================
// ADD A MESSAGE BUBBLE
// Parameters:
//   text   — the message string
//   sender — "user" or "ai"
// =============================================
function addMessage(text, sender) {
  const chatBox = document.getElementById("chatMessages");

  // --- Outer row ---
  const row = document.createElement("div");
  row.classList.add(
    "message",
    sender === "user" ? "user-message" : "ai-message",
  );

  if (sender === "ai") {
    // AI side: show the "Kardan AI" identity block (icon + label)
    // This replaces the plain robot avatar circle from before.
    const identity = document.createElement("div");
    identity.classList.add("ai-identity");
    identity.innerHTML = `
      <div class="ai-identity-icon">
        <i class="fa-solid fa-robot"></i>
      </div>
      <span class="ai-identity-label">Kardan AI</span>
    `;
    row.appendChild(identity);
  }
  // User side: NO avatar at all — just the bubble aligned to the right.

  // --- Bubble ---
  const bubble = document.createElement("div");
  bubble.classList.add(
    "message-bubble",
    sender === "user" ? "user-bubble" : "ai-bubble",
  );
  // innerHTML is used so AI responses with <b>, <ul>, <li> tags render correctly
  bubble.innerHTML = `<p>${text}</p><span class="message-time">${getCurrentTime()}</span>`;

  row.appendChild(bubble);
  chatBox.appendChild(row);

  // Scroll to the bottom so the new message is visible
  chatBox.scrollTop = chatBox.scrollHeight;
}

// =============================================
// SHOW TYPING INDICATOR (three bouncing dots)
// Returns the element's ID so we can remove it later.
// =============================================
function showTyping() {
  const chatBox = document.getElementById("chatMessages");
  const typingId = "typing-" + Date.now();

  const row = document.createElement("div");
  row.classList.add("message", "ai-message");
  row.id = typingId;

  // Same Kardan AI identity as a real message
  row.innerHTML = `
    <div class="ai-identity">
      <div class="ai-identity-icon">
        <i class="fa-solid fa-robot"></i>
      </div>
      <span class="ai-identity-label">Kardan AI</span>
    </div>
    <div class="message-bubble ai-bubble">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;

  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
  return typingId;
}

// =============================================
// REMOVE TYPING INDICATOR
// =============================================
function removeTyping(typingId) {
  const el = document.getElementById(typingId);
  if (el) el.remove();
}

// =============================================
// CALL FLASK API
// =============================================
async function fetchReply(userText, typingId) {
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
    });
    const data = await res.json();
    removeTyping(typingId);
    addMessage(data.response, "ai");
  } catch (err) {
    removeTyping(typingId);
    addMessage("connect the python first then try ", "ai");
    console.error("Flask error:", err);
  }
}

// =============================================
// CLEAR CHAT
// Removes all messages and brings the welcome banner back.
// =============================================
function clearChat() {
  const chatBox = document.getElementById("chatMessages");

  // Remove every child element from the messages box
  while (chatBox.firstChild) {
    chatBox.removeChild(chatBox.firstChild);
  }

  // Restore the welcome banner by cloning it fresh from the template
  // Since we removed it from the DOM, we rebuild it with innerHTML
  const banner = document.createElement("div");
  banner.className = "welcome-banner";
  banner.id = "welcomeBanner";
  banner.innerHTML = `
    <div class="welcome-identity">
      <div class="ai-badge">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="ai-badge-text">
        <span class="ai-badge-name">Kardan AI</span>
        </span>
      </div>
    </div>
    <h2 class="welcome-title">How can I help you today?</h2>
    <p class="welcome-sub">Ask me anything about Kardan University</p>
    <div class="tip-strip">
      <i class="fa-solid fa-lightbulb tip-icon"></i>
      <span id="tipText">${tips[tipIndex]}</span>
    </div>
  `;

  chatBox.appendChild(banner);
  bannerVisible = true; // reset flag so hideBanner() works again next send
}

// =============================================
// QUICK QUESTIONS DROPDOWN
// =============================================

// Toggle open / closed
function toggleDropdown() {
  const menu = document.getElementById("quickMenu");
  const arrow = document.getElementById("qdArrow");
  const isOpen = menu.classList.contains("visible");

  if (isOpen) {
    menu.classList.remove("visible");
    arrow.classList.remove("open");
  } else {
    menu.classList.add("visible");
    arrow.classList.add("open");
  }
}

// Close the dropdown if the user clicks anywhere outside it
document.addEventListener("click", function (e) {
  const dropdown = document.getElementById("quickDropdown");
  if (dropdown && !dropdown.contains(e.target)) {
    document.getElementById("quickMenu").classList.remove("visible");
    document.getElementById("qdArrow").classList.remove("open");
  }
});

// Called when any quick option is clicked:
// 1. Puts the text in the input box
// 2. Closes the dropdown
// 3. Sends the message immediately (same as pressing Enter)
function quickSend(text) {
  const inputEl = document.getElementById("userInput");
  inputEl.value = text;

  // Close dropdown
  document.getElementById("quickMenu").classList.remove("visible");
  document.getElementById("qdArrow").classList.remove("open");

  // Send it
  sendMessage();
}
