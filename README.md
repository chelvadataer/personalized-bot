
# Personalized Chatbot with Open LLaMA and Ngrok

Welcome to the **Personalized Chatbot** project! This repository contains code and resources to help you build a chatbot using the open-source Open LLaMA language model. We'll be setting up the chatbot in a Windows environment and deploying it with Ngrok for remote access.

## Prerequisites

To get started, ensure you have the following installed:

- **Python 3.7** or above
- [Git](https://git-scm.com/download/win)
- [Ngrok](https://ngrok.com/download) (for creating a public URL to access your chatbot remotely)
- [Ollama](https://ollama.com) (for handling the LLaMA model locally)

If any of these are missing, install them before proceeding.

## Setup Guide

### Step 1: Clone the Repository

Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/chelvadataer/personalized-bot.git
cd personalized-bot
```

### Step 2: Set Up a Python Virtual Environment

Create and activate a Python virtual environment, then install dependencies:
```bash
# Create a virtual environment
python -m venv chatbot-env

# Activate the environment
# On Windows
chatbot-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Chatbot Locally

The chatbot script uses [Streamlit](https://streamlit.io) for a simple web interface. To launch it, run:
```bash
streamlit run chatbot.py
```

### Step 4: Expose Your Chatbot to the Internet with Ngrok

To make your chatbot accessible from outside your local machine, use Ngrok to create a public URL.

1. Start Ngrok:
   ```bash
   ngrok http 8501
   ```
2. Ngrok will generate a forwarding URL (e.g., `http://abcd1234.ngrok.io`). Use this URL to access your chatbot from any device with an internet connection.

## Python Script Overview

The `chatbot.py` script does the following:
1. Takes user input.
2. Sends the input to the Open LLaMA model using `subprocess`.
3. Displays the model's response on a Streamlit web interface.

The script also includes user customization options, like setting a name, greeting, and managing chat history.

### Customizing the Chatbot UI

You can add images and branding by replacing `logo.svg` with your logo or preferred image, and modifying the UI colors and layout with Streamlit’s styling features.

## Next Steps

Here are some ideas to enhance your chatbot:
1. **Personalize** responses with different styles or tones.
2. **Add more features** like voice input or a knowledge base.
3. **Deploy on a cloud server** for greater accessibility and robustness.

## Conclusion

This project is an excellent start for building and deploying an interactive, personalized chatbot. The repository contains everything you need, from setup to deployment. We encourage you to explore and customize the bot to suit your needs!

For full code, images, and examples, visit the repository on GitHub: [Personalized Bot](https://github.com/chelvadataer/personalized-bot).

Happy coding! 🚀
