const API_URL = "http://127.0.0.1:5000";

const pdfFile = document.getElementById("pdfFile");
const chatContainer = document.getElementById("chatContainer");
const sendBtn = document.getElementById("sendBtn");
const questionInput = document.getElementById("questionInput");
let conversations = [];
let currentConversation = null;

// ==========================
// Load Documents
// ==========================

const token =
    localStorage.getItem(
        "token"
    );

if(!token){

    window.location.href =
        "login.html";

}

const selectedDocument =
    document.getElementById(
        "selectedDocument"
    );

if(selectedDocument){

    selectedDocument.innerHTML = `
        <option value="">
            All Documents
        </option>
    `;

}

document.getElementById(
    "newChatBtn"
)

function logout(){

    localStorage.removeItem("token");
    localStorage.removeItem("username");

    conversations = [];
    currentConversation = null;

    window.location.href =
        "login.html";

}

function getAuthHeaders() {

    const token =
        localStorage.getItem("token");

    return {
        "Content-Type":"application/json",
        "Authorization":`Bearer ${token}`
    };

}

async function loadDocuments() {

    try {

        const response = await fetch(
            `${API_URL}/documents`,
            {
                headers:{
                    "Authorization":
                    `Bearer ${localStorage.getItem("token")}`
                }
            }
        );

        const data = await response.json();

        const documentsList =
            document.getElementById(
                "documentsList"
            );

        documentsList.innerHTML = "";

        if(data.documents.length === 0){

        documentsList.innerHTML = `
        <div class="empty-state">
            No PDFs uploaded yet
        </div>
        `;

        return;
    }

        selectedDocument.innerHTML =
        `
        <option value="">
            All Documents
        </option>
        `;

        data.documents.forEach(doc => {

        
        const option =
            document.createElement(
                "option"
            );

        option.value = doc;

        option.textContent = doc;

        selectedDocument.appendChild(
            option
        );

            const div =
                document.createElement("div");

            div.className =
                "document-card";

            const displayName =
                doc.length > 25
                ? doc.substring(0, 25) + "..."
                : doc;

            div.innerHTML =
            `
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">

                <span>
                    📄 ${displayName}
                </span>

                <span
                    style="
                        cursor:pointer;
                        color:#ff4d4d;
                        font-size:18px;
                    "
                    onclick="deleteDocument('${doc}')"
                >
                    🗑
                </span>

            </div>
            `;

            documentsList.appendChild(div);

        });

    }

    catch(error){

        console.error(error);

    }

}


// ==========================
// Upload PDF
// ==========================

if(pdfFile){

    pdfFile.addEventListener(
        "change",
        uploadPDF
    );

}

async function uploadPDF() {

    const file =
        pdfFile.files[0];

    if(!file){
        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    try{

        const response =
            await fetch(
                `${API_URL}/upload`,
                {
                    method:"POST",
                    headers:{
                        "Authorization":
                        `Bearer ${localStorage.getItem("token")}`
                    },
                    body:formData
                }
            )

        const data =
            await response.json();

        console.log(
            `${data.document} uploaded successfully`
        );

        loadDocuments();

    }

    catch(error){

        console.error(
            "Upload Error:",
            error
        );

    }

}


// ==========================
// Delete Document
// ==========================

async function deleteDocument(document){

    const confirmDelete =
        confirm(
            `Delete ${document}?`
        );

    if(!confirmDelete){
        return;
    }

    try{

        const response =
            await fetch(
                `${API_URL}/delete-document`,
                {
                    method:"POST",

                    headers:getAuthHeaders(),

                    body: JSON.stringify({
                        document
                    })
                }
            );

        const data =
            await response.json();

        console.log(
            data.message
        );

        loadDocuments();

    }

    catch(error){

        console.error(
            "Delete Error:",
            error
        );

    }

}


// ==========================
// Add User Message
// ==========================

function addUserMessage(text){

    const hero =
        document.querySelector(".hero");

    if(hero){
        hero.remove();
    }

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "user-message";

    wrapper.innerHTML =
    `
        <div class="user-bubble">
            ${text}
        </div>
    `;

    chatContainer.appendChild(
        wrapper
    );

    scrollToBottom();

}


// ==========================
// Typing Indicator
// ==========================

function showTyping(){

    const typing =
        document.createElement("div");

    typing.className =
        "ai-message";

    typing.id =
        "typingIndicator";

    typing.innerHTML =
    `
        <div class="ai-bubble">

            <div>
                

                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

            </div>

        </div>
    `;

    chatContainer.appendChild(
        typing
    );

    scrollToBottom();

}

function removeTyping(){

    const typing =
        document.getElementById(
            "typingIndicator"
        );

    if(typing){
        typing.remove();
    }

}


// ==========================
// Add AI Message
// ==========================

function addAIMessage(
    answer,
    sources
){

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "ai-message";

    let sourcesHTML = "";

    if(
        sources &&
        sources.length > 0
    ){

        sourcesHTML +=
        `
        <div class="sources">

            <div class="sources-title">
                Sources
            </div>
        `;

        sources.forEach(source => {

            sourcesHTML +=
            `
            <div
                class="source-item"
                onclick="
                    previewPDF(
                        '${source.document}',
                        ${source.page}
                    )
                "
            >

            📄 ${source.document}
            • Page ${source.page}

            </div>
            `;

        });

        sourcesHTML +=
        `
        </div>
        `;

    }

    wrapper.innerHTML =
    `
        <div class="ai-bubble">

            ${answer}

            ${sourcesHTML}

        </div>
    `;

    chatContainer.appendChild(
        wrapper
    );

    scrollToBottom();

}


function renderHistory(){

    const historyList =
        document.getElementById(
            "historyList"
        );

    historyList.innerHTML = "";

    if(conversations.length === 0){

    historyList.innerHTML = `
    <div class="empty-state">
        No chats yet
    </div>
    `;

    return;
}

    conversations.forEach(
        conversation => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "history-item";

            div.innerHTML =
`
<div style="
display:flex;
justify-content:space-between;
align-items:center;
">

    <span>
        ${conversation.title}
    </span>

    <span
        style="
        color:#ff4d4d;
        cursor:pointer;
        font-size:16px;
        "
        onclick="
        event.stopPropagation();
        deleteConversation(${conversation.id})
        "
    >
        🗑
    </span>

</div>
`;

            div.onclick =
            () => openConversation(
                conversation.id
            );

            historyList.appendChild(
                div
            );

        }
    );

}


// ==========================
// Ask Question
// ==========================

async function askQuestion(){

    const question =
    questionInput.value.trim();

    if(!question){
        return;
    }

    if(
        currentConversation.messages.length === 0
    ){

        currentConversation.title =
            question.substring(0,40);

    }

    if(!question){
        return;
    }

    addUserMessage(
        question
    );

    questionInput.value = "";

    showTyping();

    try{

        const response =
            await fetch(
                `${API_URL}/ask`,
                {
                    method:"POST",
                    headers:getAuthHeaders(),
                    body:JSON.stringify({
                        question,
                        document: selectedDocument.value
                    })
                }
            );

        const data =
            await response.json();

        removeTyping();

        addAIMessage(
            data.answer,
            data.sources
        );

        currentConversation.messages.push({

            role:"user",

            content:question

        });

        currentConversation.messages.push({

    role:"assistant",

    content:data.answer,

    sources:data.sources

});

        saveConversations();
        renderHistory();

    }

    catch(error){

        removeTyping();

        addAIMessage(
            "Something went wrong.",
            []
        );

        console.error(error);

    }

}


// ==========================
// Send Button
// ==========================

const clearChatBtn =
document.getElementById(
    "clearChatBtn"
);

if(clearChatBtn){

    clearChatBtn.addEventListener(
        "click",
        clearCurrentChat
    );

}

sendBtn.addEventListener(
    "click",
    askQuestion
);

questionInput.addEventListener(
    "keydown",
    function(event){

        if(
            event.key === "Enter" &&
            !event.shiftKey
        ){

            event.preventDefault();

            askQuestion();

        }

    }
);


// ==========================
// Auto Scroll
// ==========================

function scrollToBottom(){

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}


// ==========================
// Startup
// ==========================

loadDocuments();

loadConversations();

if(
    conversations.length === 0
){

    createNewChat();

}

renderHistory();



function previewPDF(
    fileName,
    page
){

    const panel =
        document.getElementById(
            "pdfPanel"
        );

    const viewer =
        document.getElementById(
            "pdfViewer"
        );

    panel.classList.add(
        "active"
    );

    viewer.src = "";

    setTimeout(() => {

        viewer.src =
            `${API_URL}/pdf/${encodeURIComponent(fileName)}?t=${Date.now()}#page=${page}`;

    }, 100);

}

function closePreview(){

    const panel =
        document.getElementById(
            "pdfPanel"
        );

    const viewer =
        document.getElementById(
            "pdfViewer"
        );

    panel.classList.remove(
        "active"
    );

    viewer.src = "";

}



function createNewChat(){

    currentConversation = {

        id: Date.now(),

        title: "New Chat",

        messages: []

    };

    conversations.unshift(
        currentConversation
    );

    saveConversations();

}

document
.getElementById("newChatBtn")
.addEventListener(
    "click",
    () => {

        createNewChat();

        renderHistory();

        chatContainer.innerHTML =
        `
        <div class="hero">
            <h1>IntelliDocs</h1>
            <p>Chat with your PDFs using AI.</p>
        </div>
        `;

    }
);

function saveConversations(){

    const username =
    localStorage.getItem("username");

localStorage.setItem(
    `intellidocs_conversations_${username}`,
    JSON.stringify(conversations)
);

}

function loadConversations(){

    const username =
    localStorage.getItem("username");

    const saved =
    localStorage.getItem(
        `intellidocs_conversations_${username}`
    );

    if(saved){

        conversations =
            JSON.parse(saved);

        if(conversations.length > 0){

            currentConversation =
                conversations[0];

        }

    }

}

function openConversation(id){

    currentConversation =
        conversations.find(
            c => c.id === id
        );

    chatContainer.innerHTML = "";

    if(currentConversation.messages.length === 0){

    chatContainer.innerHTML = `
    <div class="hero">

        <h1>IntelliDocs</h1>

        <p>
            Start a new conversation
        </p>

    </div>
    `;

    return;
}

    currentConversation.messages.forEach(
        message => {

            if(
                message.role === "user"
            ){

                addUserMessage(
                    message.content
                );

            }

            else{

                addAIMessage(
                    message.content,
                    message.sources || []
                );

            }

        }
    );

}


function deleteConversation(id){

    const confirmDelete =
        confirm(
            "Delete this chat?"
        );

    if(!confirmDelete){
        return;
    }

    conversations =
        conversations.filter(
            c => c.id !== id
        );

    saveConversations();

    if(
        currentConversation &&
        currentConversation.id === id
    ){

        if(
            conversations.length > 0
        ){

            currentConversation =
                conversations[0];

            openConversation(
                currentConversation.id
            );

        }

        else{

            createNewChat();

            chatContainer.innerHTML =
            `
            <div class="hero">
                <h1>IntelliDocs</h1>
                <p>
                Chat with your PDFs using AI.
                </p>
            </div>
            `;

        }

    }

    renderHistory();

}

const logoutBtn =
document.getElementById("logoutBtn");

if(logoutBtn){

    logoutBtn.addEventListener(
        "click",
        () => {

            localStorage.removeItem("token");

            localStorage.removeItem("username");

            window.location.href =
                "login.html";

        }
    );

}

function clearCurrentChat(){

    if(
        !currentConversation
    ){
        return;
    }

    const confirmClear =
        confirm(
            "Clear current conversation?"
        );

    if(!confirmClear){
        return;
    }

    currentConversation.messages = [];

    currentConversation.title =
        "New Chat";

    saveConversations();

    renderHistory();

    chatContainer.innerHTML =
    `
    <div class="hero">

        <h1>IntelliDocs</h1>

        <p>
            Chat with your PDFs using AI.
        </p>

    </div>
    `;
}
