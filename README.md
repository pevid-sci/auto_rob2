## 💊 RoB-2 Automated Expert Ratings

An AI-powered tool designed for clinical trial methodologists to automate the Risk of Bias 2 (RoB-2) assessment of randomized controlled trials. This application allows you to run the entire analysis locally using Ollama, eliminating the need to upload files to external servers or cloud-based APIs.


## 🌐 Online
**Note:** You still need to have **Ollama** running locally on your computer for the cloud interface to communicate with the models.

https://riskofbias2.streamlit.app/


## 🚀 Key Features

* **Local Processing:** Run your analysis offline. No need for OpenAI/Anthropic API keys or sending data to external servers.
* **Batch Processing:** Upload multiple study PDFs and process them sequentially in one go.
* **Model Flexibility:** Compatible with any model available on **Ollama** (Llama 3.1, Command R, Qwen 2.5, DeepSeek, etc.).
* **Methodological Rigor:** Uses an optimized expert prompt based on the **Lai et al. (JAMA Network Open)** framework.
* **Auto-Correction Loop:** Built-in retry logic (up to 3 attempts) to handle model inconsistencies and ensure structured JSON outputs.
* **Exports:** Download results in `.csv` or `.xlsx` formatted for direct use in the `robvis` R package.
* **Audit Trail:** Full transparency with access to the AI's reasoning and supporting quotes for manual verification.

## 🛠️ Prerequisites

Before running the app, ensure you have the following:

**Ollama**: Download and install from ollama.com.

**Local Models**: models like llama3.1:8b or higher.

**Python 3.8+**

## 📦 Setup for advanced users 

*Optional: Only if you prefer to run the app offline*

Clone this repository:

    git clone https://github.com/your-username/rob2-automated-ratings.git
    cd rob2-automated-ratings

Install dependencies:

    pip install streamlit ollama pandas PyPDF2 xlsxwriter

## 🖥️ Usage

1. Open the Ollama application.

2. Access the website or launch the Streamlit interface.

       streamlit run rob2.py

> Note for web users: If the website cannot find your local Ollama, you might need to set an environment variable to allow the connection. Run this in your terminal once:

    $env:OLLAMA_ORIGINS="https://riskofbias2.streamlit.app"; ollama serve

3. Use the sidebar to select your local model.

4. Upload your RCT PDFs and click "Start Batch Processing".

5. Download the results.
     


## 📜 Credits

The prompting logic and criteria are adapted from: [Lai et al., 2024 - JAMA Network Open](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2818882)


## 📲 Contact

Feel free to send an email: pedro.vidor@ufrgs.br 

*AI technologies were used in the development of this project.*
