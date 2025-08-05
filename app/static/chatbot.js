const form = document.getElementById("chat-form");
const input = document.getElementById("question-input");
const chatBox = document.getElementById("chat-box");

function appendMessage(role, text) {
    const msgWrapper = document.createElement("div");
    msgWrapper.className = `w-full flex ${role === "user" ? "justify-end" : "justify-start"}`;

    const msg = document.createElement("div");
    msg.className = `max-w-[75%] px-4 py-3 my-1 rounded-lg break-words shadow leading-relaxed whitespace-pre-wrap text-left ${role === "user" ? "bg-blue-600 text-white rounded-br-none" : "bg-gray-700 text-white rounded-bl-none"
        }`;

    const sourceMatch = text.match(/Source:\s*(.*)$/m);
    let content = text;
    let sourceLinks = [];

    if (sourceMatch) {
        content = text.replace(sourceMatch[0], "").trim();
        const sourceText = sourceMatch[1];
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        let match;
        while ((match = linkRegex.exec(sourceText)) !== null) {
            sourceLinks.push({ title: match[1], url: match[2] });
        }
    }

    msg.innerText = content;
    if (sourceLinks.length > 0) {
        const sourceDiv = document.createElement("div");
        sourceDiv.className = "text-sm text-gray-400 mt-2";
        sourceDiv.innerText = "Source: ";

        const links = sourceLinks.map((link, index) => {
            const a = document.createElement("a");
            a.href = link.url;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.className = "text-blue-400 underline hover:text-blue-300";
            a.innerText = link.title;
            return a.outerHTML + (index < sourceLinks.length - 1 ? ", " : "");
        }).join("");
        sourceDiv.innerHTML += links;
        msg.appendChild(sourceDiv);
    }
    msgWrapper.appendChild(msg);
    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;
    appendMessage("user", question);
    input.value = "";
    input.focus();

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await res.json();
        appendMessage("bot", data.answer || "Sorry, I couldn’t find a reliable answer.");
    } catch {
        appendMessage("bot", "⚠️ Error reaching chatbot. Please try again.");
    }
});