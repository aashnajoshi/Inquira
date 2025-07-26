const form = document.getElementById("chat-form");
const input = document.getElementById("question-input");
const chatBox = document.getElementById("chat-box");

function appendMessage(role, text) {
    const msg = document.createElement("div");

    msg.className = `max-w-[75%] px-4 py-2 my-1 rounded-lg break-words shadow 
        ${role === "user"
            ? "bg-gray-600 text-white self-end text-right rounded-br-none"
            : "bg-gray-900 text-white self-start text-left rounded-bl-none"
        }`;

    msg.textContent = text;
    chatBox.appendChild(msg);
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
        appendMessage("bot", data.answer || "Sorry, no response.");
    } catch {
        appendMessage("bot", "Error reaching chatbot.");
    }
});