document.addEventListener("DOMContentLoaded", () => {
    const initialScreen = document.getElementById("initial-screen");
    const chatContainer = document.getElementById("chat-container");
    const chatBox = document.getElementById("chat-box");
    const inputForm = document.getElementById("input-form");
    const userInput = document.getElementById("user-input");
    const initialInputForm = document.getElementById("initial-input-form");
    const initialUserInput = document.getElementById("initial-user-input");
    const backButton = document.getElementById("back-button");
    let sessionId = null;

    function appendMessage(role, text, sources = []) {
        const msgWrapper = document.createElement("div");
        msgWrapper.className = `w-full flex ${role === "user" ? "justify-end" : "justify-start"} fade-in`;
        const msg = document.createElement("div");
        msg.className = `max-w-[80%] px-4 py-3 my-1 rounded-lg break-words shadow-md leading-relaxed whitespace-pre-wrap text-left ${role === "user" ? "bg-blue-600 text-white rounded-br-none" : "bg-gray-700 text-white rounded-bl-none"}`;
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

    async function sendMessage(question, isInitial = false) {
        appendMessage("user", question);
        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question, session_id: sessionId })
            });
            const data = await response.json();
            sessionId = data.session_id;
            appendMessage("bot", data.answer, data.sources || []);
        } catch (error) {
            appendMessage("bot", "Error: Could not get response.");
        }
    }

    initialInputForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = initialUserInput.value.trim();
        if (!question) return;
        initialScreen.classList.add("hidden");
        chatContainer.classList.remove("hidden");
        await sendMessage(question, true);
        initialUserInput.value = "";
    });

    inputForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = userInput.value.trim();
        if (!question) return;
        await sendMessage(question);
        userInput.value = "";
    });

    backButton.addEventListener("click", () => {
        chatContainer.classList.add("hidden");
        initialScreen.classList.remove("hidden");
        sessionId = null;
    });
});
