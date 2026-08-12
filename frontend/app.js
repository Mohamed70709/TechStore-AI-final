const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const newChatButton = document.getElementById("new-chat-button");
const typingIndicator = document.getElementById("typing-indicator");
const voiceButton = document.getElementById("voice-button");
const imageButton =
    document.getElementById("image-button");

const imageInput =
    document.getElementById("image-input");

const authButton = document.getElementById("auth-button");
const authPanel = document.getElementById("auth-panel");
const authTitle = document.getElementById("auth-title");
const authName = document.getElementById("auth-name");
const authEmail = document.getElementById("auth-email");
const authPassword = document.getElementById("auth-password");
const authSubmit = document.getElementById("auth-submit");
const authSwitch = document.getElementById("auth-switch");
const authMessage = document.getElementById("auth-message");
const userInfo = document.getElementById("user-info");

// Session used for this browser demonstration
let sessionId =
    localStorage.getItem("memory_session_id") ||
    "memory_" + Date.now();

localStorage.setItem(
    "memory_session_id",
    sessionId
);

// Authentication mode
let isRegisterMode = false;


// ==============================
// Authentication
// ==============================

function openAuthPanel() {

    authPanel.classList.remove("hidden");

    authTitle.textContent =
        isRegisterMode ? "Create Account" : "Sign In";

    authSubmit.textContent =
        isRegisterMode ? "Register" : "Sign In";

    authSwitch.textContent =
        isRegisterMode
            ? "Already have an account? Sign In"
            : "Create an account";

    authName.classList.toggle(
        "hidden",
        !isRegisterMode
    );

    authMessage.textContent = "";

    authEmail.focus();
}


authButton.addEventListener(
    "click",
    function() {

        // If already logged in, log out
        if (localStorage.getItem("access_token")) {

            localStorage.removeItem("access_token");
            localStorage.removeItem("user_name");
            localStorage.removeItem("user_email");
            localStorage.removeItem("user_role");

            updateAuthUI();

            return;
        }

        openAuthPanel();
    }
);


authSwitch.addEventListener(
    "click",
    function() {

        isRegisterMode = !isRegisterMode;

        openAuthPanel();
    }
);


authSubmit.addEventListener(
    "click",
    async function() {

        const email = authEmail.value.trim();
        const password = authPassword.value.trim();
        const name = authName.value.trim();

        if (!email || !password) {

            authMessage.textContent =
                "Please enter your email and password.";

            return;
        }

        if (isRegisterMode && !name) {

            authMessage.textContent =
                "Please enter your name.";

            return;
        }

        authSubmit.disabled = true;

        authMessage.textContent =
            "Please wait...";

        try {

            const endpoint =
                isRegisterMode
                    ? "/auth/register"
                    : "/auth/login";

            const body =
                isRegisterMode
                    ? {
                        name: name,
                        email: email,
                        password: password
                    }
                    : {
                        email: email,
                        password: password
                    };

            const response = await fetch(
                endpoint,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(body)
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail || "Authentication failed."
                );
            }

            // Save authentication information
            localStorage.setItem(
                "access_token",
                data.access_token
            );

            localStorage.setItem(
                "user_name",
                data.name
            );

            localStorage.setItem(
                "user_email",
                data.email
            );

            // Decode role from JWT
            const tokenParts =
                data.access_token.split(".");

            const payload =
                JSON.parse(
                    atob(
                        tokenParts[1]
                        .replace(/-/g, "+")
                        .replace(/_/g, "/")
                    )
                );

            localStorage.setItem(
                "user_role",
                payload.role || "customer"
            );

            updateAuthUI();

            authPanel.classList.add("hidden");

            authEmail.value = "";
            authPassword.value = "";
            authName.value = "";

        } catch (error) {

            console.error(
                "Authentication error:",
                error
            );

            authMessage.textContent =
                error.message;

        } finally {

            authSubmit.disabled = false;
        }
    }
);


// Update header after login/logout

function updateAuthUI() {

    const token =
        localStorage.getItem("access_token");

    const name =
        localStorage.getItem("user_name");

    const role =
        localStorage.getItem("user_role");

    if (token) {

        userInfo.textContent =
            `${name} (${role})`;

        authButton.textContent =
            "Sign Out";

    } else {

        userInfo.textContent =
            "Not signed in";

        authButton.textContent =
            "Sign In";
    }
}


// Check login state when page loads

updateAuthUI();


// ==============================
// Chat
// ==============================

async function sendMessage() {

    const message =
        messageInput.value.trim();

    if (!message) {
        return;
    }

    // Show user's message
    const userMessage =
        document.createElement("div");

    userMessage.className =
        "message user";

    userMessage.textContent =
        message;

    chatBox.appendChild(
        userMessage
    );

    // Clear input
    messageInput.value = "";

    // Disable sending while request is running
    sendButton.disabled = true;

    // Show typing indicator
    typingIndicator.classList.remove(
        "hidden"
    );

    // Create empty assistant message
    const assistantMessage =
        document.createElement("div");

    assistantMessage.className =
        "message assistant";

    assistantMessage.textContent = "";

    chatBox.appendChild(
        assistantMessage
    );

    try {

        const response =
            await fetch(
                "/chat/stream",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        session_id:
                            sessionId,

                        message:
                            message
                    })
                }
            );

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder();

        let buffer = "";

        while (true) {

            const {
                value,
                done
            } = await reader.read();

            if (done) {
                break;
            }

            buffer +=
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );

            const lines =
                buffer.split("\n");

            buffer =
                lines.pop();

            for (const line of lines) {

                if (!line.startsWith("data:")) {
                    continue;
                }

                const data =
                    line.substring(5).trim();

                if (!data) {
                    continue;
                }

                const event =
                    JSON.parse(data);

                if (event.delta) {

                    typingIndicator.classList.add(
                        "hidden"
                    );

                    assistantMessage.textContent +=
                        event.delta;

                    chatBox.scrollTop =
                        chatBox.scrollHeight;
                }

                if (event.done) {

                    console.log("Streaming complete");

                    speakResponse(
                        assistantMessage.textContent
                    );
                }
            }
        }

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        assistantMessage.textContent =
            "Sorry, I could not connect to the TechStore AI server.";

    } finally {

        typingIndicator.classList.add(
            "hidden"
        );

        sendButton.disabled = false;

        messageInput.focus();
    }
}


// Send button

sendButton.addEventListener(
    "click",
    sendMessage
);


// Enter key

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            sendMessage();
        }

    }
);


// New conversation

newChatButton.addEventListener(
    "click",
    function() {



        chatBox.innerHTML = `
            <div class="message assistant">
                Hello! I'm the TechStore AI assistant.
                How can I help you today?
            </div>
        `;

        messageInput.value = "";

        messageInput.focus();
    }
);

// ==============================
// Voice Assistant
// ==============================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let recognition = null;

if (SpeechRecognition) {

    recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.maxAlternatives = 3;

    recognition.onstart = function() {

        voiceButton.textContent = "🔴";
        voiceButton.title = "Listening...";

    };

    recognition.onresult = function(event) {

        const transcript =
            event.results[0][0].transcript;

        messageInput.value = transcript;

        // Automatically send the recognized message
        sendMessage();

    };

    recognition.onerror = function(event) {

        console.error(
            "Speech recognition error:",
            event.error
        );

        voiceButton.textContent = "🎤";
        voiceButton.title = "Voice input";

    };

    recognition.onend = function() {

        voiceButton.textContent = "🎤";
        voiceButton.title = "Voice input";

    };

    voiceButton.addEventListener(
        "click",
        function() {

            recognition.start();

        }
    );

} else {

    voiceButton.disabled = true;
    voiceButton.title =
        "Speech recognition is not supported in this browser.";

}


// ==============================
// Text To Speech
// ==============================

function speakResponse(text) {

    if (!("speechSynthesis" in window)) {
        return;
    }

    // Stop any previous speech
    window.speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;

    window.speechSynthesis.speak(speech);
}

// ==============================
// Image Product Recognition
// ==============================

imageButton.addEventListener(
    "click",
    function() {

        imageInput.click();

    }
);


imageInput.addEventListener(
    "change",
    async function() {

        const file = imageInput.files[0];

        if (!file) {
            return;
        }

        // Show image message in chat
        const userMessage =
            document.createElement("div");

        userMessage.className =
            "message user";

        userMessage.textContent =
            "📷 Uploaded a product image.";

        chatBox.appendChild(userMessage);

        // Show loading message
        const assistantMessage =
            document.createElement("div");

        assistantMessage.className =
            "message assistant";

        assistantMessage.textContent =
            "🔎 Analyzing the product image...";

        chatBox.appendChild(
            assistantMessage
        );

        chatBox.scrollTop =
            chatBox.scrollHeight;

        try {

            const formData =
                new FormData();

            formData.append(
                "image",
                file
            );

            const response =
                await fetch(
                    "/image/analyze",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Image analysis failed."
                );
            }

            if (!data.catalog) {

                assistantMessage.textContent =
                    data.message;

                return;
            }

            assistantMessage.textContent =
                "I identified this product as: " +
                data.identified_product +
                "\n\n" +
                formatCatalogResult(
                    data.catalog
                );

        } catch (error) {

            console.error(
                "Image error:",
                error
            );

            assistantMessage.textContent =
                "Sorry, I could not analyze " +
                "that product image.";

        } finally {

            imageInput.value = "";

            chatBox.scrollTop =
                chatBox.scrollHeight;
        }
    }
);


function formatCatalogResult(result) {

    if (result.message) {
        return result.message;
    }

    if (!Array.isArray(result)) {
        return JSON.stringify(result);
    }

    if (result.length === 0) {
        return "I couldn't find that product in our catalog.";
    }

    return result.map(function(product) {

        return (
            "Product: " + product.name +
            "\nPrice: $" + product.price +
            "\nCategory: " + product.category +
            "\nStock: " + product.stock
        );

    }).join("\n\n");
}