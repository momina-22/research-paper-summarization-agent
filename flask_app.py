from flask import Flask, request, render_template_string, session
from summarizer.extractor import extract_text_from_pdf
from summarizer.preprocessor import preprocess_text
from summarizer.llm_engine import run_agent, set_active_paper_text
import tempfile
import os

app = Flask(__name__)
app.secret_key = "super_secret_agent_key_for_session_management"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResearchEase · AI Research Agent</title>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #faf8f4; color: #2c2a26; min-height: 100vh; }
        .hero { background: #fff9f0; border-bottom: 1px solid #e8e0d0; padding: 32px 24px; text-align: center; }
        .hero h1 { font-family: 'Lora', serif; font-size: 28px; font-weight: 600; color: #1a1814; }
        .hero p { font-size: 14px; color: #7a7060; margin-top: 4px; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .card { background: #ffffff; border: 1px solid #e8e0d0; border-radius: 16px; padding: 30px; margin-bottom: 24px; }
        .drop-zone { border: 2px dashed #d4c9b8; border-radius: 12px; padding: 30px; text-align: center; background: #faf8f4; cursor: pointer; }
        input[type="file"] { display: none; }
        .choose-btn { display: inline-block; padding: 8px 20px; background: #c17a3a; color: #fff; border-radius: 20px; font-size: 13px; cursor: pointer; margin-bottom: 8px; }
        .submit-btn { width: 100%; margin-top: 16px; padding: 12px; background: #2c2a26; color: #faf8f4; border: none; border-radius: 25px; font-size: 14px; cursor: pointer; font-weight: 500; }
        .submit-btn:hover { background: #1a1814; }
        
        /* Chat Box Styling */
        .chat-container { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; max-height: 450px; overflow-y: auto; padding-right: 10px; }
        .msg { padding: 14px 18px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 14.5px; }
        .msg.user { background: #f0e6d2; color: #3a3225; align-self: flex-end; border-bottom-right-radius: 4px; }
        .msg.agent { background: #ffffff; border: 1px solid #e8e0d0; align-self: flex-start; border-bottom-left-radius: 4px; font-family: 'Lora', serif; white-space: pre-wrap; }
        
        .chat-input-form { display: flex; gap: 10px; margin-top: 20px; }
        .chat-input { flex: 1; padding: 12px 18px; border: 1px solid #d4c9b8; border-radius: 25px; font-size: 14px; outline: none; }
        .chat-input:focus { border-color: #c17a3a; }
        .send-btn { padding: 12px 24px; background: #c17a3a; color: white; border: none; border-radius: 25px; font-size: 14px; cursor: pointer; font-weight: 500; }
        .send-btn:hover { background: #a8642c; }
        .status-tag { display: inline-block; background: #edf7ee; color: #3a7a42; font-size: 11px; padding: 3px 10px; border-radius: 12px; margin-bottom: 10px; font-weight: 500; }
    </style>
</head>
<body>

<div class="hero">
    <h1>🔬 ResearchEase Agent</h1>
    <p>An autonomous agent that reasons over documents, answers fine-grained questions, and compiles insights.</p>
</div>

<div class="container">
    <div class="card">
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <div class="drop-zone" onclick="document.getElementById('pdf-input').click()">
                <p style="margin-bottom: 10px; color: #7a7060;">📄 Upload a new research paper to initialize the agent context</p>
                <label class="choose-btn">Select PDF</label>
                <input type="file" id="pdf-input" name="pdf" accept=".pdf" onchange="this.form.submit()">
                {% if filename %}
                    <div style="margin-top: 8px; font-size: 13px; color: #c17a3a; font-weight: 500;">Active Context: {{ filename }}</div>
                {% endif %}
            </div>
        </form>
    </div>

    {% if filename %}
    <div class="card">
        <span class="status-tag">Agent Online</span>
        <h3>Conversation Thread</h3>
        
        <div class="chat-container" id="chat-box">
            {% for turn in chat_history %}
                <div class="msg user">{{ turn.user }}</div>
                <div class="msg agent">{{ turn.agent }}</div>
            {% endfor %}
        </div>

        <form method="POST" action="/chat" class="chat-input-form">
            <input type="text" name="message" class="chat-input" placeholder="Ask the agent anything ('Summarize it', 'What's the dataset size?', etc.)" required autocomplete="off">
            <button type="submit" class="send-btn">Ask Agent</button>
        </form>
    </div>
    {% endif %}
</div>

<script>
    // Keep chat box scrolled to the bottom automatically
    const chatBox = document.getElementById('chat-box');
    if (chatBox) { chatBox.scrollTop = chatBox.scrollHeight; }
</script>

</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template_string(HTML, chat_history=session["chat_history"], filename=session.get("filename"))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("pdf")
    if file and file.filename != '':
        # Reset session chat history on new upload
        session["chat_history"] = []
        session["filename"] = file.filename
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        try:
            # 1. Pipeline preparation
            raw = extract_text_from_pdf(tmp_path)
            clean = preprocess_text(raw)
            
            # 2. Inject context directly into our dynamic agent engine memory
            set_active_paper_text(clean)
            
            # 3. FAST GREETING (Bypasses the slow heavy initial summary call)
            agent_response = "I have successfully processed and indexed your research paper! 🚀\n\nWhat would you like to know? You can ask me to 'give me a full summary', or ask specific questions about the methodology, results, or limitations."
            
            # Append initial greeting to logs
            session["chat_history"].append({"user": f"Uploaded: {file.filename}", "agent": agent_response})
            session.modified = True
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    return render_template_string(HTML, chat_history=session.get("chat_history", []), filename=session.get("filename"))
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")
    chat_history = session.get("chat_history", [])
    
    # Format current history logs into structured format LangChain expects
    formatted_history = []
    for turn in chat_history:
        formatted_history.append(("user", turn["user"]))
        formatted_history.append(("assistant", turn["agent"]))
    
    # Compute next agent step using decision-making tool loop
    agent_output = run_agent(user_message, history=formatted_history)
    
    chat_history.append({"user": user_message, "agent": agent_output})
    session["chat_history"] = chat_history
    session.modified = True
    
    return render_template_string(HTML, chat_history=chat_history, filename=session.get("filename"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)