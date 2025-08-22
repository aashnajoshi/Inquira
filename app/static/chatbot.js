document.addEventListener("DOMContentLoaded", () => {
    const initialScreen = document.getElementById("search-container");
    const chatContainer = document.getElementById("chat-container");
    const chatBox = document.getElementById("chat-box");
    const inputForm = document.getElementById("chat-form");
    const userInput = document.getElementById("question-input");
    const initialInputForm = document.getElementById("initial-form");
    const initialUserInput = document.getElementById("initial-input");
    const backButton = document.getElementById("back-button");
    const sessionIndicator = document.getElementById("session-indicator");
    let sessionId = localStorage.getItem("sessionId") || null;
    let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];

    function appendMessage(role, text, sources = []) {
        const msgWrapper = document.createElement("div");
        msgWrapper.className = `w-full flex ${role === "user" ? "justify-end" : "justify-start"} fade-in`;
        const msg = document.createElement("div");
        msg.className = `max-w-[80%] px-4 py-3 my-1 rounded-lg break-words shadow-md leading-relaxed whitespace-pre-wrap text-left ${role === "user" ? "bg-blue-600 text-white rounded-br-none" : "bg-gray-700 text-white rounded-bl-none"}`;
        let content = text
            .replace(/https?:\/\/[^\s"]+/g, "")
            .replace(/<[^>]+>/g, "")
            .replace(/"\s*(target|rel|class)="[^"]*"/g, "")
            .replace(/iXie Gaming/g, "iXie Gaming")
            .trim();
        msg.textContent = content;
        if (sources.length > 0) {
            const sourceDiv = document.createElement("div");
            sourceDiv.className = "text-sm text-gray-400 mt-2";
            sourceDiv.innerHTML = "For more details: " + sources.map(src => 
                `<a href="${src.url}" target="_blank" rel="noopener noreferrer" class="text-blue-400 underline hover:text-blue-300">${src.title}</a>`
            ).join(", ");
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

    function saveHistory() {
        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
        localStorage.setItem("sessionId", sessionId);
    }

    function loadHistory() {
        if (chatHistory.length > 0 && sessionId) {
            initialScreen.classList.add("hidden");
            chatContainer.classList.remove("hidden");
            sessionIndicator.classList.remove("hidden");
            chatHistory.forEach(msg => {
                appendMessage(msg.role, msg.text, msg.sources || []);
            });
        }
    }

    async function sendMessage(question, isInitial = false) {
        appendMessage("user", question);
        chatHistory.push({role: "user", text: question});
        saveHistory();
        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question, session_id: sessionId })
            });
            const data = await response.json();
            sessionId = data.session_id;
            appendMessage("bot", data.answer, data.sources || []);
            chatHistory.push({role: "bot", text: data.answer, sources: data.sources});
            saveHistory();
        } catch (error) {
            appendMessage("bot", "Error: Could not get response.");
            chatHistory.push({role: "bot", text: "Error: Could not get response."});
            saveHistory();
        }
    }

    initialInputForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = initialUserInput.value.trim();
        if (!question) return;
        initialUserInput.value = "";
        initialScreen.classList.add("hidden");
        chatContainer.classList.remove("hidden");
        sessionIndicator.classList.remove("hidden");
        await sendMessage(question, true);
    });

    inputForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = userInput.value.trim();
        if (!question) return;
        userInput.value = "";
        await sendMessage(question);
    });

    initialUserInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            initialInputForm.dispatchEvent(new Event("submit"));
        }
    });

    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            inputForm.dispatchEvent(new Event("submit"));
        }
    });

    backButton.addEventListener("click", () => {
        chatContainer.classList.add("hidden");
        initialScreen.classList.remove("hidden");
        sessionIndicator.classList.add("hidden");
        sessionId = null;
        chatHistory = [];
        localStorage.removeItem("sessionId");
        localStorage.removeItem("chatHistory");
        chatBox.innerHTML = "";
    });

    loadHistory();
});