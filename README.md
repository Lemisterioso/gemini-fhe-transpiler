# 🔒 Gemini FHE Transpiler

**Turning standard Python into Fully Homomorphic Encryption (FHE) circuits using Gemini 3.**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1qxlh0uzw0htfz5gJUeYmdOa3tUST1muT?usp=sharing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📝 Overview
**Gemini FHE Transpiler** is a Proof-of-Concept (PoC) demonstrating how Large Language Models (LLMs) can bridge the gap between medical logic and privacy-preserving cryptography.

Using **Gemini 3 Pro**, this tool automatically transpiles standard, readable Python code (e.g., a Diabetes Risk protocol) into complex, FHE-compatible arithmetic circuits powered by **Zama's Concrete ML**. This allows sensitive medical data to be processed **while encrypted**, ensuring zero privacy leaks.

## 🌟 Features
* **Gemini 3 Powered:** leverages the latest Google LLM to understand and rewrite logical branches (`if/else`) into arithmetic operations (`*`, `+`).
* **Automated Transpilation:** Converts standard Python functions into Zama `concrete` circuits.
* **Privacy by Design:** Input data (age, glucose, etc.) is encrypted on the client side and never revealed to the server.
* **Interactive Demo:** Includes a Streamlit dashboard and a Colab notebook for instant testing.

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)
The easiest way to test the project is to run the interactive notebook. No installation required.
👉 [**Click here to run in Google Colab**](https://colab.research.google.com/drive/1qxlh0uzw0htfz5gJUeYmdOa3tUST1muT?usp=sharing)

### Option 2: Local Installation
To run the Streamlit interface locally:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Lemisterioso/gemini-fhe-transpiler.git](https://github.com/Lemisterioso/gemini-fhe-transpiler.git)
    cd gemini-fhe-transpiler
    ```

2.  **Install dependencies:**
    *(Note: Concrete ML requires Linux, macOS, or WSL on Windows)*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

## 🛠️ Architecture
1.  **Input:** User provides a Python function (Medical Protocol).
2.  **Transpilation:** Gemini 3 analyzes the Abstract Syntax Tree (AST) logic and rewrites it into FHE-friendly arithmetic.
3.  **Compilation:** The generated code is compiled by Zama's Concrete.
4.  **Execution:** Encrypted data is passed through the circuit to produce an encrypted result.

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Submitted for the Google AI Hackathon 2026.*
