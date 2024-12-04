document.getElementById("queryForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = document.getElementById("query").value.trim();
    const method = document.getElementById("ragMethod").value;
    const chatContainer = document.getElementById("chat-container");

    if (!query) {
        alert("Please enter a question.");
        return;
    }

    // Add user query to the chat
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.innerHTML = `<p><b>Use Query:<b> ${query}</p>`;
    chatContainer.appendChild(userMessage);

    // Scroll to the bottom of the chat
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Send the query to FastAPI backend
    try {
        const startTime = performance.now(); // Start timer
        const response = await fetch(`http://127.0.0.1:8000/${method}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question: query, top_k: 3 }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Error fetching results");
        }

        const data = await response.json();

        // Add assistant responses to the chat
        let responseHTML = `<div class="message assistant">
            <strong>Time Taken:</strong> ${data.time_taken.toFixed(2)} seconds<br>
            <strong>CPU Usage:</strong> ${data.cpu_usage.toFixed(2)}%</div>`;

        data.answers.forEach((answer, index) => {
            responseHTML += `<div class="message assistant"><strong>Answer ${index + 1}:</strong> ${answer}</div>`;
        });

        chatContainer.innerHTML += responseHTML;

        // Scroll to the bottom of the chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        const errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "assistant");
        errorMessage.innerHTML = `<p>Error: ${error.message}</p>`;
        chatContainer.appendChild(errorMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } finally {
        document.getElementById("query").value = ""; // Clear the input
    }
});
