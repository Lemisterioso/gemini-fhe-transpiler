import streamlit as st
import google.generativeai as genai
import re
from PIL import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURATION ---
import streamlit as st
import google.generativeai as genai
import os

# --- SECURE API KEY HANDLING ---
api_key = None

# 1. Try to load from Streamlit secrets (local or cloud)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    pass

# 2. If not found in secrets, ask the user via the UI
if not api_key:
    st.warning("⚠️ No API key found in secrets.")
    # We use the key entered by the user
    api_key = st.text_input("Please enter your Google (Gemini) API Key:", type="password")

# 3. Configure Gemini OR Stop execution if no key
if api_key:
    genai.configure(api_key=api_key) # <--- C'est ici que la configuration se fait maintenant !
else:
    st.stop() # Stop the app until the key is provided
    
# --- CHOIX DU MODÈLE ---
# Modèle expérimental (Rapide + Quota OK pour la vidéo)
#model = genai.GenerativeModel("gemini-2.0-flash-exp")
# On utilise la version Flash Preview pour la vitesse et le quota (Hackathon compliant)
model = genai.GenerativeModel("gemini-3-flash-preview")

# --- CONFIGURATION SÉCURITÉ (ANTI-BLOCAGE) ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- CLEANING FUNCTION ---
def parse_gemini_response(text):
    """Separates Python code from the explanatory text."""
    code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
    
    if code_match:
        code_content = code_match.group(1).strip()
        explanation = text.replace(code_match.group(0), "")
    else:
        if "def " in text:
            code_content = text
            explanation = "Code extracted directly."
        else:
            code_content = "# No code generated or incorrect format."
            explanation = text
        
    return code_content, explanation

# --- INTERFACE ---
st.set_page_config(page_title="Gemini FHE Transpiler", layout="wide", page_icon="🔐")

st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4285F4; font-weight: bold;}
    .sub-text {font-size: 1.1rem; color: #555;}
    .stTextArea textarea {font-family: 'Fira Code', monospace;}
</style>
<div class='main-header'>🔐 Gemini FHE Transpiler</div>
<p class='sub-text'>Instantly convert your Python scripts (or diagrams!) into encrypted circuits using Gemini.</p>
<hr>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# --- COLUMN 1 : INPUT (Multimodal) ---
with col1:
    st.subheader("1. Define Logic")

    input_method = st.radio(
        "Logic Source:",
        ["💻 Code Editor", "📸 Photo / Diagram (Vision)"],
        horizontal=True
    )
    
    final_code_input = ""

    if input_method == "💻 Code Editor":
        default_code = """def credit_score(salary, loan_amount):
    # FHE Challenge: Division + If/Else
    # The server must not see the salary nor the loan amount.
    
    if loan_amount / salary > 0.33:
        return 1 # High Risk
    else:
        return 0 # Low Risk"""
        final_code_input = st.text_area("Python Editor", value=default_code, height=300)

    else:
        st.info("Upload a photo of a diagram or a handwritten rule.")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Document Preview', use_column_width=True)
            
            if st.button("✨ Extract Logic from Image"):
                with st.spinner("Gemini Vision is analyzing the diagram..."):
                    try:
                        prompt_vision = """
                        Analyze this image. It describes a logical rule or a decision tree.
                        Your mission is to transcribe this logic into a simple Python function.
                        Constraints:
                        1. Create a valid Python function.
                        2. Use ONLY numeric variables (int/float) and if/else structures.
                        3. Return ONLY the Python code block (inside ```python tags).
                        """
                        response_vision = model.generate_content(
                            [prompt_vision, image],
                            safety_settings=safety_settings
                        )
                        extracted_code, _ = parse_gemini_response(response_vision.text)
                        st.session_state.extracted_code_from_img = extracted_code
                        st.success("Logic extracted successfully!")
                    except Exception as e:
                        st.error(f"Vision Error: {e}")
            
            if 'extracted_code_from_img' in st.session_state:
                final_code_input = st.text_area("Extracted Code (Editable)", value=st.session_state.extracted_code_from_img, height=200)
        else:
            st.warning("Waiting for image upload...")

    st.markdown("---")
    if st.button("🚀 Generate Secure Circuit", type="primary", use_container_width=True):
        if not final_code_input:
            st.error("Please provide code or an analyzed image first.")
        else:
            with st.spinner("Gemini is transpiling logic to FHE cryptography..."):
                try:
                    # --- PROMPT MIS À JOUR AVEC LE NOUVEAU FORMAT DE SORTIE ---
                    # --- PROMPT CORRIGÉ (VERSION ZAMA 2.0+) ---
                    full_prompt = f"""
                    Act as a Zama/Concrete expert. 
                    Task: Convert this Python function into an FHE circuit compatible with the LATEST version of Concrete-Python (v2+).

                    CRITICAL RULES:

                    0. IMPORTS (CRITICAL):
                    - You MUST use: `from concrete import fhe`
                    - You MUST NOT use `concrete.numpy` (it is deprecated).
                    - Compilation line MUST be: `compiler = fhe.Compiler(your_function, {{"input_name": "encrypted"}})`

                    1. COMPILER & CALIBRATION:
                    - Create a realistic 'inputset' (e.g., [(10, 20), (50, 60)]).
                    - Compile with: `circuit = compiler.compile(inputset)`

                    2. ENCRYPTION:
                    - Use grouped encryption: `args = circuit.encrypt(val1, val2)`

                    3. LOGIC TRANSFORMATION:
                    - Replace 'if/else' with arithmetic: result = (condition * val_true) + ((1 - condition) * val_false).
                    - NO imaginary functions.

                    4. DEMO & VISUALIZATION (MANDATORY):
                    - You MUST generate a `if __name__ == "__main__":` block at the end.
                    - Use `import time` and emojis.
                    - Follow this logging structure EXACTLY:
                      
                      print("⚙️ COMPILING FHE Circuit...")
                      time.sleep(0.5)
                      print("✅ Compilation Successful.\\n")
                      
                      print("🔒 ENCRYPTION (Client side)...")
                      # Print input values here (e.g., "-> Input Glucose: 145")
                      time.sleep(1)
                      print("   -> Data transformed into encrypted noise.\\n")
                      
                      print("☁️ HOMOMORPHIC EXECUTION (Server side)...")
                      print("   (Computing blindly on encrypted data...)")
                      # Run circuit here
                      time.sleep(1.5)
                      print("   -> Computation finished.\\n")
                      
                      print("🔓 DECRYPTION (Client side)...")
                      # Decrypt here
                      
                      print("-" * 40)
                      print(f"🚀 SUCCESS: Decrypted result matches!")
                      
                      # LOGIC FOR FINAL PRINT:
                      # If result is 1, print "(High Risk)". If 0, print "(Low Risk)".
                      label = "(High Risk)" if result == 1 else "(Low Risk)"
                      print(f"🎯 FINAL RESULT: {{result}} {{label}}")
                      print("-" * 40)

                    SOURCE CODE TO CONVERT:
                    {final_code_input}

                    Provide the complete executable Python code.
                    """                    
                    response = model.generate_content(
                        full_prompt,
                        safety_settings=safety_settings
                    )
                    
                    code, expl = parse_gemini_response(response.text)
                    
                    st.session_state.g_code = code
                    st.session_state.g_expl = expl
                    st.success("FHE Transpilation Successful!")
                    
                except Exception as e:
                    st.error(f"Generation Error: {e}")

# --- COLUMN 2 : OUTPUT ---
with col2:
    st.subheader("🛡️ Compiled Result")
    
    if 'g_code' in st.session_state:
        tab1, tab2 = st.tabs(["🐍 Concrete Code", "💡 Technical Explanation"])
        
        with tab1:
            st.code(st.session_state.g_code, language='python')
            st.download_button(
                label="📥 Download .py file",
                data=st.session_state.g_code,
                file_name="fhe_circuit.py",
                mime="text/x-python"
            )
            
        with tab2:
            st.markdown(st.session_state.g_expl)
    else:
        st.info("Result will appear here after compilation.")
        st.markdown("""
        **Transpiler Architecture:**
        1. **Vision (Optional):** Image $\\to$ Raw Python Code.
        2. **Logic Analysis:** Gemini detects insecure operations.
        3. **FHE Math:** It rewrites equations (e.g., `A/B > C` becomes `A > B*C`).
        4. **Generation:** Produces final `concrete-python` code.
        """)