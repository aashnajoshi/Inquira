const searchContainer = document.getElementById("search-container");
const chatContainer = document.getElementById("chat-container");
const initialForm = document.getElementById("initial-form");
const initialInput = document.getElementById("initial-input");
const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question-input");
const chatBox = document.getElementById("chat-box");
const backButton = document.getElementById("back-button");
const sessionIndicator = document.getElementById("session-indicator");
let sessionId = null;

function updateSessionIndicator() {
    if (sessionId) {
        sessionIndicator.classList.remove("hidden");
    } else {
        sessionIndicator.classList.add("hidden");
    }
}

function switchToChatInterface(initialQuestion) {
    searchContainer.classList.add("slide-up");
    setTimeout(() => {
        searchContainer.classList.add("hidden");
        chatContainer.classList.remove("hidden");
        chatContainer.classList.add("flex", "fade-in");
        if (initialQuestion) {
            processQuestion(initialQuestion);
        }
    }, 400);
    return new Promise(resolve => setTimeout(resolve, 400));
}

function switchToSearchInterface() {
    chatContainer.classList.remove("flex", "fade-in");
    chatContainer.classList.add("hidden");
    searchContainer.classList.remove("hidden", "slide-up");
    searchContainer.style.opacity = "0";
    setTimeout(() => {
        searchContainer.style.opacity = "1";
    }, 10);
    chatBox.innerHTML = "";
    initialInput.value = "";
    questionInput.value = "";
    sessionId = null;
    localStorage.removeItem("chatSessionId");
    updateSessionIndicator();
}

function appendMessage(role, text) {
    const msgWrapper = document.createElement("div");
    msgWrapper.className = `w-full flex ${role === "user" ? "justify-end" : "justify-start"} fade-in`;
    const msg = document.createElement("div");
    msg.className = `max-w-[80%] px-4 py-3 my-1 rounded-lg break-words shadow-md leading-relaxed whitespace-pre-wrap text-left ${role === "user"
        ? "bg-blue-600 text-white rounded-br-none"
        : "bg-gray-700 text-white rounded-bl-none"
        }`;
    const sourceMatch = text.match(/Source:\s*(.*)$/m);
    let content = text;
    const sourceLinks = [];
    if (sourceMatch) {
        content = text.replace(sourceMatch[0], "").trim();
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        let match;
        while ((match = linkRegex.exec(sourceMatch[1])) !== null) {
            sourceLinks.push({ title: match[1], url: match[2] });
        }
    }
    msg.innerText = content;
    if (sourceLinks.length > 0) {
        const sourceDiv = document.createElement("div");
        sourceDiv.className = "text-sm text-gray-400 mt-2";
        sourceDiv.innerHTML = "Source: " + sourceLinks.map((link, i) => {
            return `<a href="${link.url}" target="_blank" rel="noopener noreferrer" class="text-blue-400 underline hover:text-blue-300">${link.title}</a>${i < sourceLinks.length - 1 ? ", " : ""}`;
        }).join("");
        msg.appendChild(sourceDiv);
    }
    if (role === "bot") {
        msg.classList.add("typing-effect");
        setTimeout(() => {
            msg.classList.remove("typing-effect");
        }, Math.min(content.length * 10, 1000));
    }
    msgWrapper.appendChild(msg);
    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function processQuestion(question) {
    if (!question) return;
    appendMessage("user", question);
    questionInput.value = "";
    questionInput.focus();
    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question,
                session_id: sessionId
            }),
        });
        const data = await res.json();
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("chatSessionId", sessionId);
            updateSessionIndicator();
        }
        appendMessage("bot", data.answer || "Sorry, I couldn't find a reliable answer.");
    } catch {
        appendMessage("bot", "⚠️ Error reaching chatbot. Please try again.");
    }
}
initialForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = initialInput.value.trim();
    if (question) switchToChatInterface(question);
});
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    if (question) processQuestion(question);
});
backButton.addEventListener("click", switchToSearchInterface);
initialInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        initialForm.dispatchEvent(new Event("submit"));
    }
});
questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});

document.addEventListener("DOMContentLoaded", async () => {
    const savedSessionId = localStorage.getItem("chatSessionId");
    if (savedSessionId) {
        sessionId = savedSessionId;
        updateSessionIndicator();
        await loadConversationHistory();
    }
    setupTextareaAutoResize(initialInput);
    setupTextareaAutoResize(questionInput);
});

function setupTextareaAutoResize(textarea) {
    if (!textarea) return;
    textarea.style.height = '48px';
    textarea.addEventListener('input', function () {
        this.style.height = '48px';
        const newHeight = Math.min(this.scrollHeight, 96);
        this.style.height = newHeight + 'px';
        if (this.scrollHeight > 96) {
            this.classList.add('scrollable');
        } else {
            this.classList.remove('scrollable');
        }
    });
}

async function loadConversationHistory() {
    if (!sessionId) return;
    try {
        const res = await fetch("/get_session_history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId }),
        });
        const data = await res.json();
        const history = data.history || [];
        chatBox.innerHTML = "";
        if (history.length > 0) {
            if (chatContainer.classList.contains("hidden")) {
                await switchToChatInterface();
            }
            history.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error("Error loading conversation history:", error);
    }
}