# File: api/index.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for frontend development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    response: str

# Initialize OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

# Create OpenAI client using a different approach to avoid the proxies issue
# We'll import OpenAI only when needed, not at the module level
def get_openai_response(prompt, history):
    """
    Fetches a response from OpenAI's API with a given prompt and conversation history.
    """
    try:
        # Import here to handle initialization differently
        import openai
        
        # Create a client without any extra parameters that might cause conflicts
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY
        )
        
        messages = history + [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}"

# HTML template - replace this comment with your full HTML from the original code
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthAssist Chatbot</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary-color: #0088ff;
            --primary-dark: #0066cc;
            --secondary-color: #4caf50;
            --secondary-dark: #388e3c;
            --dark-bg: #ffffff;
            --panel-bg: #f8f9fa;
            --message-bg: #f0f2f5;
            --user-message-bg: #0088ff;
            --border-color: #e0e0e0;
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --text-muted: #9aa0a6;
            --input-bg: #f8f9fa;
            --highlight: rgba(0, 0, 0, 0.05);
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: #f5f5f5;
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            margin: 0;
        }
        
        .chat-container {
            max-width: 1200px;
            margin: 20px auto;
            height: calc(100vh - 40px);
            display: flex;
            flex-direction: column;
            background-color: var(--dark-bg);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
            border-radius: 15px;
        }
        
        .background-decoration {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
        }
        
        .bg-circle {
            position: absolute;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.05), rgba(0, 136, 255, 0.05));
            filter: blur(30px);
        }
        
        .bg-circle-1 {
            width: 400px;
            height: 400px;
            top: -100px;
            left: -100px;
        }
        
        .bg-circle-2 {
            width: 500px;
            height: 500px;
            bottom: -200px;
            right: -100px;
            background: linear-gradient(135deg, rgba(0, 136, 255, 0.05), rgba(76, 175, 80, 0.05));
        }
        
        .header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
            background-color: #ffffff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1;
            position: relative;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .logo-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #4caf50, #0088ff);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 10px rgba(0, 136, 255, 0.5);
        }
        
        .logo-text {
            font-size: 24px;
            font-weight: 600;
            background: linear-gradient(90deg, #4caf50, #0088ff);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: none;
            letter-spacing: 0.5px;
        }
        
        .header-controls {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .header-button {
            background-color: var(--panel-bg);
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .header-button:hover {
            background-color: var(--message-bg);
            color: var(--text-primary);
            transform: translateY(-2px);
        }
        
        .chat-body {
            flex-grow: 1;
            overflow-y: auto;
            padding: 10px;
            background-color: transparent;
            z-index: 1;
            display: flex;
            flex-direction: column;
            scroll-behavior: smooth;
        }
        
        .chat-body::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-body::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .chat-body::-webkit-scrollbar-thumb {
            background-color: var(--border-color);
            border-radius: 6px;
        }
        
        .message-container {
            margin-bottom: 16px;
            max-width: 85%;
        }
        
        .user-container {
            align-self: flex-end;
            text-align: right;
        }
        
        .bot-container {
            align-self: flex-start;
            text-align: left;
        }
        
        .message {
            display: inline-block;
            padding: 12px 18px;
            border-radius: 18px;
            position: relative;
            margin-bottom: 4px;
            word-break: break-word;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            border-bottom-right-radius: 4px;
            text-align: left;
        }
        
        .bot-message {
            background-color: var(--panel-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            border-bottom-left-radius: 4px;
        }
        
        .bot-message-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .bot-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4caf50, #0088ff);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 12px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .message-time {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 4px;
            opacity: 0.8;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 8px 12px;
            margin-top: 4px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: var(--text-muted);
            border-radius: 50%;
            animation: typingAnimation 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typingAnimation {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }
        
        .footer {
            padding: 16px 20px;
            background-color: #ffffff;
            border-top: 1px solid var(--border-color);
            z-index: 1;
            position: relative;
            box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .input-container {
            position: relative;
            border-radius: 16px;
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .input-container:focus-within {
            box-shadow: 0 0 0 2px rgba(0, 136, 255, 0.3), 0 4px 12px rgba(0, 0, 0, 0.2);
            border-color: var(--primary-color);
        }
        
        .message-input {
            border: none;
            background: transparent;
            padding: 16px 20px;
            padding-right: 120px;
            width: 100%;
            resize: none;
            min-height: 24px;
            max-height: 200px;
            color: var(--text-primary);
            font-size: 15px;
            line-height: 1.5;
            font-family: 'Poppins', sans-serif;
        }
        
        .message-input:focus {
            outline: none;
        }
        
        .message-input::placeholder {
            color: var(--text-muted);
        }
        
        .button-container {
            position: absolute;
            right: 10px;
            bottom: 8px;
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .action-button {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .action-button:hover {
            background-color: var(--highlight);
            color: var(--text-primary);
        }
        
        .action-button i {
            font-size: 20px;
        }
        
        .send-button {
            background: linear-gradient(135deg, #4caf50, #0088ff);
            color: white;
            width: 48px;
            height: 48px;
            box-shadow: 0 2px 8px rgba(0, 136, 255, 0.4);
            transition: all 0.3s;
        }
        
        .send-button:hover {
            background: linear-gradient(135deg, #43a047, #0072cc);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 136, 255, 0.6);
        }
        
        .voice-button {
            background-color: rgba(0, 136, 255, 0.1);
            color: var(--primary-color);
        }
        
        .voice-button:hover {
            background-color: rgba(0, 136, 255, 0.2);
        }
        
        .voice-button.listening {
            background: linear-gradient(135deg, #0088ff, #0066cc);
            color: white;
            box-shadow: 0 0 0 rgba(0, 136, 255, 0.4);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(0, 136, 255, 0.4);
            }
            70% {
                box-shadow: 0 0 0 8px rgba(0, 136, 255, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(0, 136, 255, 0);
            }
        }
        
        .pulse-dot {
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            background: linear-gradient(135deg, #4caf50, #0088ff);
            border-radius: 50%; 
            margin-right: 8px; 
            animation: dot-pulse 1.5s infinite;
        }
        
        @keyframes dot-pulse {
            0% { opacity: 0.4; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1); }
            100% { opacity: 0.4; transform: scale(0.8); }
        }
        
        .listening-indicator {
            display: flex;
            align-items: center;
            color: var(--primary-color);
            font-size: 14px;
            font-weight: 500;
            background-color: rgba(0, 136, 255, 0.1);
            padding: 6px 12px;
            border-radius: 20px;
            visibility: hidden;
        }
        
        .welcome-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            padding: 0px;
            margin-top: 0px;
            position: relative;
            z-index: 1;
        }
        
        .welcome-logo {
            width: 90px;
            height: 90px;
            border-radius: 24px;
            background: linear-gradient(135deg, #4caf50, #0088ff);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px rgba(0, 136, 255, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        .welcome-logo::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                to bottom right,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0) 40%,
                rgba(255, 255, 255, 0.4) 50%,
                rgba(255, 255, 255, 0) 60%,
                rgba(255, 255, 255, 0) 100%
            );
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: rotate(45deg) translateX(-100%); }
            30%, 100% { transform: rotate(45deg) translateX(100%); }
        }
        
        .welcome-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 16px;
            background: linear-gradient(90deg, #4caf50, #0088ff);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            position: relative;
            text-align: center;
        }
        
        .welcome-subtitle {
            font-size: 18px;
            margin-bottom: 32px;
            color: var(--text-secondary);
            max-width: 600px;
            line-height: 1.6;
            text-align: center;
        }
        
        .capability-chips {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
            margin-top: 16px;
            max-width: 700px;
        }
        
        .chip {
            padding: 12px 20px;
            background-color: var(--panel-bg);
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .chip svg {
            color: var(--primary-color);
            font-size: 16px;
        }
        
        .chip:hover {
            background-color: var(--message-bg);
            border-color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        @media (max-width: 768px) {
            .chat-container {
                height: 100vh;
                width: 100%;
                margin: 0;
                border-radius: 0;
            }
            
            .welcome-title {
                font-size: 28px;
            }
            
            .welcome-subtitle {
                font-size: 16px;
                padding: 0 20px;
            }
            
            .message-container {
                max-width: 90%;
            }
            
            .capability-chips {
                gap: 10px;
                padding: 0 10px;
            }
            
            .chip {
                padding: 10px 16px;
                font-size: 13px;
            }
            
            .message-input {
                padding-right: 100px;
            }
            
            .header, .footer {
                padding: 12px 16px;
            }
            
            .action-button {
                width: 38px;
                height: 38px;
            }
            
            .send-button {
                width: 42px;
                height: 42px;
            }
            
            .logo-text {
                font-size: 20px;
            }
            
            .logo-icon {
                width: 36px;
                height: 36px;
            }
        }
        
        @media (max-width: 480px) {
            .welcome-logo {
                width: 70px;
                height: 70px;
            }
            
            .welcome-title {
                font-size: 24px;
            }
            
            .welcome-subtitle {
                font-size: 14px;
            }
            
            .chip {
                padding: 8px 14px;
                font-size: 12px;
            }
            
            .message {
                padding: 10px 14px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="background-decoration">
            <div class="bg-circle bg-circle-1"></div>
            <div class="bg-circle bg-circle-2"></div>
        </div>
        
        <div class="header">
            <div class="logo">
                <div class="logo-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
                    </svg>
                </div>
                <div class="logo-text">HealthAssist</div>
            </div>
            <div class="header-controls">
                <div id="speech-status" class="listening-indicator">
                    <span class="pulse-dot"></span>
                    Listening...
                </div>
                <button class="header-button" title="Settings">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                        <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/>
                    </svg>
                </button>
                <button class="header-button" title="Help">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                        <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
                    </svg>
                </button>
            </div>
        </div>
        <div class="chat-body" id="chatBody">
            <div class="welcome-container" id="welcomeContainer">
                <div class="welcome-logo">
                    <svg xmlns="http://www.w3.org/2000/svg" width="42" height="42" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
                    </svg>
                </div>
                <h1 class="welcome-title">Hello, I'm HealthAssist</h1>
                <p class="welcome-subtitle">Your trusted AI health companion. I can help answer your health questions, provide information about symptoms, medications, and wellness topics.</p>
                
                <div class="capability-chips">
                    
                    <div class="chip">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#0088ff" viewBox="0 0 16 16">
                            <path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>
                        </svg>
                        Ask about symptoms
                    </div>
                    
                    <div class="chip">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#0088ff" viewBox="0 0 16 16">
                            <path d="M11 2a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V5a3 3 0 0 1 3-3h6zM5 1a4 4 0 0 0-4 4v6a4 4 0 0 0 4 4h6a4 4 0 0 0 4-4V5a4 4 0 0 0-4-4H5z"/>
                            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                        </svg>
                        Nutrition advice
                    </div>
                    <div class="chip">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#0088ff" viewBox="0 0 16 16">
                            <path d="M8 9.783v2.734l-.088-.047c-.437.289-.477.373-.77.25-.324-.14-.227-.432-.073-.615.49-.401-.204-1.003-1.132-1.256-.928-.253-1.382-.829-.818-1.256.564-.426 2.036-.194 2.254.272.218.466.35.53.638.7.288.17.457-.018.485-.168s.037-.286-.037-.376c-.073-.09-.164-.234-.54-.234-.376 0-.613.238-.927.882L7 10.134l-.021-.339A1.298 1.298 0 0 0 6.5 8.5c0-.497.183-.966.513-1.324a1.773 1.773 0 0 1 1.287-.662c.773 0 1.356.32 1.764.863.568.759.514 1.595.408 2.126-.396 2.014-1.357 2.235-1.972 2.543-.206.103-.738.485-.79.709-.051.224.019.495.14.557.126.062.482-.07.696-.154.337-.131.774-.272 1.656-.797l.797.483c.532-.32 1.02-.683 1.324-1.109 1.324-1.853.884-5.27-1.15-4.628-.713.228-1.25.78-1.653 1.28h.001Z"/>
                            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0ZM1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8Z"/>
                        </svg>
                        Exercise recommendations
                    </div>
                </div>
            </div>
            
            <!-- Chat messages will appear here -->
        </div>
        
        <div class="footer">
            <div class="input-container">
                <textarea class="message-input" placeholder="Ask HealthAssist about your health concerns..." rows="1" id="messageInput"></textarea>
                <div class="button-container">
                    <button class="action-button" title="Attach files">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M4.5 3a2.5 2.5 0 0 1 5 0v9a1.5 1.5 0 0 1-3 0V5a.5.5 0 0 1 1 0v7a.5.5 0 0 0 1 0V3a1.5 1.5 0 1 0-3 0v9a2.5 2.5 0 0 0 5 0V5a.5.5 0 0 1 1 0v7a3.5 3.5 0 1 1-7 0V3z"/>
                        </svg>
                    </button>
                    <button class="action-button voice-button" id="voiceButton" title="Voice input">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
                            <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5z"/>
                        </svg>
                    </button>
                    <button class="action-button send-button" id="sendButton" title="Send message">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083l6-15Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // Store chat history
        let chatHistory = [];
        
        // Auto-resize textarea
        const textarea = document.getElementById('messageInput');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight < 200) ? this.scrollHeight + 'px' : '200px';
        });
        
        // Get current time for messages
        function getCurrentTime() {
            const now = new Date();
            return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        // Send message to backend API
        async function sendMessageToAPI(message) {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        history: chatHistory
                    }),
                });
                
                const data = await response.json();
                return data.response;
            } catch (error) {
                console.error('Error sending message to API:', error);
                return "I'm sorry, I encountered an error. Please try again later.";
            }
        }
        
        // Send message function
        const sendButton = document.getElementById('sendButton');
        const chatBody = document.getElementById('chatBody');
        const welcomeContainer = document.getElementById('welcomeContainer');
        
        async function sendMessage() {
            const message = textarea.value.trim();
            if (message) {
                // Hide welcome container when chat starts
                if (welcomeContainer && welcomeContainer.style.display !== 'none') {
                    welcomeContainer.style.display = 'none';
                }
                
                // Add user message
                const userContainer = document.createElement('div');
                userContainer.className = 'message-container user-container';
                
                const userMessageDiv = document.createElement('div');
                userMessageDiv.className = 'message user-message';
                userMessageDiv.textContent = message;
                
                const userTimeDiv = document.createElement('div');
                userTimeDiv.className = 'message-time';
                userTimeDiv.textContent = getCurrentTime();
                
                userContainer.appendChild(userMessageDiv);
                userContainer.appendChild(userTimeDiv);
                chatBody.appendChild(userContainer);
                
                // Update chat history
                chatHistory.push({ role: "user", content: message });
                
                // Clear input
                textarea.value = '';
                textarea.style.height = 'auto';
                
                // Scroll to bottom
                chatBody.scrollTop = chatBody.scrollHeight;
                
                // Create and show typing indicator
                const botContainer = document.createElement('div');
                botContainer.className = 'message-container bot-container';
                
                const typingIndicator = document.createElement('div');
                typingIndicator.className = 'typing-indicator';
                typingIndicator.innerHTML = `
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                `;
                
                botContainer.appendChild(typingIndicator);
                chatBody.appendChild(botContainer);
                chatBody.scrollTop = chatBody.scrollHeight;
                
                // Get response from API
                const botResponse = await sendMessageToAPI(message);
                
                // Update chat history
                chatHistory.push({ role: "assistant", content: botResponse });
                
                // Remove typing indicator
                chatBody.removeChild(botContainer);
                
                // Add bot message
                const newBotContainer = document.createElement('div');
                newBotContainer.className = 'message-container bot-container';
                
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot-message';
                
                const botMessageHeader = document.createElement('div');
                botMessageHeader.className = 'bot-message-header';
                
                const botIcon = document.createElement('div');
                botIcon.className = 'bot-icon';
                botIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/></svg>';
                
                botMessageHeader.appendChild(botIcon);
                botMessageDiv.appendChild(botMessageHeader);
                
                const botResponseDiv = document.createElement('div');
                botResponseDiv.textContent = botResponse;
                botMessageDiv.appendChild(botResponseDiv);
                
                const botTimeDiv = document.createElement('div');
                botTimeDiv.className = 'message-time';
                botTimeDiv.textContent = getCurrentTime();
                
                newBotContainer.appendChild(botMessageDiv);
                newBotContainer.appendChild(botTimeDiv);
                chatBody.appendChild(newBotContainer);
                chatBody.scrollTop = chatBody.scrollHeight;
            }
        }
        
        sendButton.addEventListener('click', sendMessage);
        
        // Voice input functionality
        const voiceButton = document.getElementById('voiceButton');
        const speechStatus = document.getElementById('speech-status');
        let recognition;
        
        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            // Create speech recognition object
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = true;
            
            // Configure speech recognition
            recognition.lang = 'en-US';
            
            // Handle results
            recognition.onresult = function(event) {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                
                textarea.value = transcript;
                textarea.dispatchEvent(new Event('input'));
            };
            
            // Handle end of speech
            recognition.onend = function() {
                voiceButton.classList.remove('listening');
                speechStatus.style.visibility = 'hidden';
                
                // If we got text, automatically send the message
                if (textarea.value.trim()) {
                    setTimeout(() => sendMessage(), 500);
                }
            };
            
            // Handle errors
            recognition.onerror = function(event) {
                console.error('Speech recognition error', event.error);
                voiceButton.classList.remove('listening');
                speechStatus.style.visibility = 'hidden';
            };
            
            // Set up voice button
            voiceButton.addEventListener('click', function() {
                if (voiceButton.classList.contains('listening')) {
                    // Stop listening
                    recognition.stop();
                    voiceButton.classList.remove('listening');
                    speechStatus.style.visibility = 'hidden';
                } else {
                    // Start listening
                    recognition.start();
                    voiceButton.classList.add('listening');
                    speechStatus.style.visibility = 'visible';
                    
                    // Cancel if no speech detected after 5 seconds
                    setTimeout(() => {
                        if (voiceButton.classList.contains('listening') && !textarea.value.trim()) {
                            recognition.stop();
                        }
                    }, 5000);
                }
            });
        } else {
            // Browser doesn't support speech recognition
            voiceButton.addEventListener('click', function() {
                alert('Your browser does not support speech recognition. Please try using Chrome or Edge.');
            });
        }
        
        // Send message on Enter (but Shift+Enter for new line)
        textarea.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendButton.click();
            }
        });
        
        // Handle example chips
        const chips = document.querySelectorAll('.chip');
        chips.forEach(chip => {
            chip.addEventListener('click', function() {
                textarea.value = this.textContent.trim();
                textarea.dispatchEvent(new Event('input'));
                textarea.focus();
                
                // After a short delay, send the message
                setTimeout(() => sendButton.click(), 300);
            });
        });
    </script>
</body>
</html>"""

# Define API routes
@app.get("/")
async def get_homepage(request: Request):
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is running"""
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    # Get user message
    user_message = chat_request.message
    
    # Convert Pydantic model to dict for history
    history = [{"role": msg.role, "content": msg.content} for msg in chat_request.history]
    
    # Get response from OpenAI
    response = get_openai_response(user_message, history)
    
    # Return response
    return {"response": response}
