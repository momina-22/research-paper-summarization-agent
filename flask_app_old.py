from flask import Flask, request, render_template_string
from summarizer.extractor import extract_text_from_pdf
from summarizer.preprocessor import preprocess_text
from summarizer.chunker import chunk_text
from summarizer.llm_engine import summarize_chunk, generate_final_summary
import tempfile, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Summarizer</title>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: #faf8f4;
            color: #2c2a26;
            min-height: 100vh;
        }

        .hero {
            background: #fff9f0;
            border-bottom: 1px solid #e8e0d0;
            padding: 48px 24px 40px;
            text-align: center;
        }

        .hero-icon {
            font-size: 48px;
            margin-bottom: 16px;
            display: block;
        }

        .hero h1 {
            font-family: 'Lora', serif;
            font-size: 32px;
            font-weight: 600;
            color: #1a1814;
            margin-bottom: 10px;
        }

        .hero p {
            font-size: 16px;
            color: #7a7060;
            max-width: 480px;
            margin: 0 auto;
            line-height: 1.6;
        }

        .container {
            max-width: 720px;
            margin: 48px auto;
            padding: 0 24px;
        }

        .upload-card {
            background: #ffffff;
            border: 1px solid #e8e0d0;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 32px;
        }

        .upload-card h2 {
            font-family: 'Lora', serif;
            font-size: 20px;
            color: #1a1814;
            margin-bottom: 6px;
        }

        .upload-card .subtitle {
            font-size: 14px;
            color: #9a8e7e;
            margin-bottom: 28px;
        }

        .drop-zone {
            border: 2px dashed #d4c9b8;
            border-radius: 16px;
            padding: 48px 24px;
            text-align: center;
            background: #faf8f4;
            cursor: pointer;
            transition: all 0.2s;
        }

        .drop-zone:hover {
            border-color: #c17a3a;
            background: #fff9f0;
        }

        .drop-zone .big-icon {
            font-size: 36px;
            margin-bottom: 12px;
        }

        .drop-zone p {
            font-size: 15px;
            color: #7a7060;
            margin-bottom: 16px;
        }

        .drop-zone em {
            font-family: 'Lora', serif;
            font-style: italic;
            color: #9a8e7e;
            font-size: 13px;
        }

        input[type="file"] { display: none; }

        .choose-btn {
            display: inline-block;
            padding: 10px 22px;
            background: #c17a3a;
            color: #fff;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            margin-bottom: 8px;
        }

        .choose-btn:hover { background: #a8642c; }

        #file-name {
            margin-top: 10px;
            font-size: 13px;
            color: #c17a3a;
            font-style: italic;
        }

        .submit-btn {
            width: 100%;
            margin-top: 24px;
            padding: 14px;
            background: #2c2a26;
            color: #faf8f4;
            border: none;
            border-radius: 30px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: background 0.2s;
            letter-spacing: 0.02em;
        }

        .submit-btn:hover { background: #1a1814; }

        .result-card {
            background: #ffffff;
            border: 1px solid #e8e0d0;
            border-radius: 20px;
            padding: 40px;
        }

        .result-card .done-tag {
            display: inline-block;
            background: #edf7ee;
            color: #3a7a42;
            font-size: 12px;
            padding: 4px 14px;
            border-radius: 20px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .result-card h2 {
            font-family: 'Lora', serif;
            font-size: 22px;
            color: #1a1814;
            margin-bottom: 20px;
        }

        .summary-body {
            font-size: 15px;
            line-height: 1.85;
            color: #3a3630;
            white-space: pre-wrap;
            font-family: 'Lora', serif;
        }

        .divider {
            border: none;
            border-top: 1px solid #e8e0d0;
            margin: 28px 0;
        }

        footer {
            text-align: center;
            padding: 32px;
            font-size: 13px;
            color: #b0a898;
            font-style: italic;
            font-family: 'Lora', serif;
        }
    </style>
</head>
<body>

<div class="hero">
    <span class="hero-icon">📖</span>
    <h1 style="font-family: 'Roboto', sans-serif;"><b>ResearchEase</b></h1>
    <h2>Read less, understand more.</h2>
    <p>Drop in a research paper and get a clear, structured summary — contributions, methods, results and all.</p>
</div>

<div class="container">
    <div class="upload-card">
        <h2>Upload your paper</h2>
        <p class="subtitle">Supports PDF files up to any length</p>
        <form method="POST" enctype="multipart/form-data">
            <div class="drop-zone" onclick="document.getElementById('pdf-input').click()">
                <div class="big-icon">📄</div>
                <p>Click to browse or drop your PDF here</p>
                <label class="choose-btn">Choose file</label>
                <input type="file" id="pdf-input" name="pdf" accept=".pdf" onchange="showName(this)">
                <div id="file-name"></div>
                <em>Your paper stays private — nothing is stored.</em>
            </div>
            <button type="submit" class="submit-btn"> Generate summary</button>
        </form>
    </div>

    {% if summary %}
    <div class="result-card">
        <span class="done-tag">✓ Ready</span>
        <h2>Here's what this paper is about</h2>
        <hr class="divider">
        <div class="summary-body">{{ summary }}</div>
    </div>
    {% endif %}
</div>

<footer>Made with curiosity &amp; Python &nbsp;·&nbsp; Research Paper Summarization Agent</footer>

<script>
    function showName(input) {
        const name = input.files[0]?.name || '';
        document.getElementById('file-name').textContent = name ? '📎 ' + name : '';
    }
</script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    if request.method == "POST":
        file = request.files["pdf"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        try:
            raw = extract_text_from_pdf(tmp_path)
            clean = preprocess_text(raw)
            chunks = chunk_text(clean)
            partials = [summarize_chunk(c) for c in chunks]
            summary = generate_final_summary(partials)
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    return render_template_string(HTML, summary=summary)

if __name__ == "__main__":
    app.run(debug=True, port=5000)