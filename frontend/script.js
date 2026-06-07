const API_URL = "http://127.0.0.1:5000";

const pdfFile = document.getElementById("pdfFile");
const chatContainer = document.getElementById("chatContainer");
const sendBtn = document.getElementById("sendBtn");
const questionInput = document.getElementById("questionInput");


// ==========================
// Load Documents
// ==========================

async function loadDocuments() {

    try {

        const response = await fetch(
            `${API_URL}/documents`
        );

        const data = await response.json();

        const documentsList =
            document.getElementById(
                "documentsList"
            );

        documentsList.innerHTML = "";

        data.documents.forEach(doc => {

            const div =
                document.createElement("div");

            div.className =
                "document-card";

            div.innerHTML =
                `📄 ${doc}`;

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

pdfFile.addEventListener(
    "change",
    uploadPDF
);

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
                    body:formData
                }
            );

        const data =
            await response.json();

        alert(
            `${data.document} uploaded successfully`
        );

        loadDocuments();

    }

    catch(error){

        console.error(error);

        alert(
            "Upload failed"
        );

    }

}


// ==========================
// Add User Message
// ==========================

function addUserMessage(text){

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
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
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
                <div class="source-item">
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


// ==========================
// Ask Question
// ==========================

async function askQuestion(){

    const question =
        questionInput.value.trim();

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
                    headers:{
                        "Content-Type":
                        "application/json"
                    },
                    body:JSON.stringify({
                        question
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
