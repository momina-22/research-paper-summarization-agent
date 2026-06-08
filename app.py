import streamlit as st
import tempfile, os
from summarizer.extractor import extract_text_from_pdf
from summarizer.preprocessor import preprocess_text
from summarizer.chunker import chunk_text
from summarizer.llm_engine import summarize_chunk, generate_final_summary

st.set_page_config(page_title="Research Paper Summarizer", layout="wide")
st.title("📄 Research Paper Summarization Agent")

uploaded_file = st.file_uploader("Upload a research paper (PDF)", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Extracting text..."):
        raw_text = extract_text_from_pdf(tmp_path)
        clean_text = preprocess_text(raw_text)
        chunks = chunk_text(clean_text)

    st.success(f"Extracted {len(chunks)} chunks from the paper.")

    if st.button("Generate Summary"):
        partial = []
        with st.spinner("Summarizing..."):
            for i, chunk in enumerate(chunks):
                st.write(f"Processing chunk {i+1}/{len(chunks)}...")
                partial.append(summarize_chunk(chunk))
            
            final = generate_final_summary(partial)

        st.markdown("## Summary")
        st.markdown(final)
        
        st.download_button("Download Summary", final, file_name="summary.txt")
    
    os.unlink(tmp_path)