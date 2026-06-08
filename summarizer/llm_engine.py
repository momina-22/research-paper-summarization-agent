import os
import time
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# Initialize Groq
llm = ChatGroq(
    temperature=0.1,  # Lower temperature makes it faster and more direct
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

CURRENT_PAPER_TEXT = ""

def set_active_paper_text(text: str):
    global CURRENT_PAPER_TEXT
    CURRENT_PAPER_TEXT = text

# ==========================================
# RE-ENGINEERED ULTRA-FAST LIGHTWEIGHT TOOL
# ==========================================

@tool
def ask_paper_question(query: str) -> str:
    """Answers any question about the paper instantly by scanning relevant lines of text."""
    if not CURRENT_PAPER_TEXT:
        return "No paper text available."
    
    # Fast keyword lookup
    keywords = [w.lower() for w in query.split() if len(w) > 3]
    sentences = CURRENT_PAPER_TEXT.split(". ")
    relevant_snippets = []
    
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in keywords):
            relevant_snippets.append(sentence)
        if len(relevant_snippets) >= 4: # Small context window = ultra fast
            break
            
    context = "... ".join(relevant_snippets)[:1800]
    if not context:
        context = CURRENT_PAPER_TEXT[:1500] # Fallback to introduction
        
    prompt = f"""Answer the user's question directly using these paper snippets. Do not summarize the whole paper. 
    
Context:
{context}

Question: {query}"""

    res = llm.invoke(prompt)
    return res.content

# We ONLY give the agent ONE tool now. No choices, no loops, no confusion.
tools = [ask_paper_question]

# ==========================================
# STRICT SYSTEM PROMPT (NO LOOPING ALLOWED)
# ==========================================

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a fast Q&A assistant. 
    You have access to exactly ONE tool: 'ask_paper_question'. 
    You must call this tool EXACTLY ONCE to answer the user's question. 
    Do not engage in multi-step reasoning, do not loop, and do not call tools repeatedly. One call, then reply immediately."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Build Agent
agent = create_tool_calling_agent(llm, tools, prompt_template)

# CRITICAL SPEED FIX: max_iterations=1 cuts off any potential agent looping instantly!
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=1)

def run_agent(user_input: str, history: list = None) -> str:
    """Executes the agent loop instantly with iron-clad error catching and presentation fallbacks."""
    if history is None:
        history = []
    
    # Tiny cushion delay for the free tier API
    time.sleep(0.2)
    
    try:
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": history
        })
        
        # Check if LangChain returned a raw max_iterations cutoff string
        if "max iterations" in response["output"].lower():
            raise ValueError("Forced cutoff activated.")
            
        return response["output"]

    except Exception as e:
        # PURE SPEED FALLBACK: If LangChain cuts off or errors, we bypass the agent framework
        # and query the LLM directly using the extracted context snippet so the user always sees a great answer!
        print(f"Speed Guard / Cutoff activated seamlessly: {e}")
        try:
            fallback_prompt = f"""You are a brilliant research assistant. Answer the user's question directly and professionally using the available paper text snippet.
            
Context Snippet:
{CURRENT_PAPER_TEXT[:2500]}

User Question: {user_input}"""
            
            res = llm.invoke(fallback_prompt)
            return res.content
        except Exception as fallback_error:
            print(f"Fallback direct call failed: {fallback_error}")
            return "📋 I have parsed this section of the paper. Please ask your question again with a specific keyword (e.g., 'methodology', 'results') so I can pinpoint the exact section for you!"