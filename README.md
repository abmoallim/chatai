# PydanticAI Chat App 🤖💬

A real-time chat application built with **PydanticAI** and **FastAPI** that lets you have conversations with OpenAI's GPT-4o model. This app demonstrates modern AI chat functionality with streaming responses, persistent chat history, and a beautiful web interface.

![Chat App Demo](https://i.imgur.com/placeholder.png)

## 🌟 What This App Does

- **Real-time AI Chat**: Talk to OpenAI's GPT-4o model through a web interface
- **Streaming Responses**: See the AI's response appear word-by-word in real-time
- **Persistent History**: Your conversations are saved and restored when you refresh the page
- **Modern UI**: Clean, responsive design using Bootstrap
- **Fast Backend**: Built with FastAPI for high-performance API handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed on your computer
- An OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))

### Installation

1. **Clone or download this project** to your computer

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   Create a file called `.env` in the project folder and add:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   Replace `your_actual_api_key_here` with your real OpenAI API key.

4. **Run the app**:
   ```bash
   python chat_app.py
   ```

5. **Open your browser** and go to: `http://localhost:8000`

🎉 **That's it!** You now have a working AI chat app!

## 📁 Project Structure

```
chatai/
├── chat_app.py      # Main Python backend server
├── chat_app.html    # Web interface (frontend)
├── chat_app.ts      # TypeScript for real-time chat features
├── requirements.txt # Python dependencies
├── .env            # Your API key (keep this secret!)
├── chat.db         # SQLite database (created automatically)
└── README.md       # This file
```

## 🔍 How It Works (For Beginners)

### The Big Picture

Think of this app like a restaurant:
- **Frontend (HTML/TypeScript)**: The dining room where customers (users) place orders
- **Backend (Python/FastAPI)**: The kitchen that processes orders and coordinates everything
- **AI Model (OpenAI GPT-4o)**: The chef that creates the responses
- **Database (SQLite)**: The receipt book that remembers all past orders

### Flow of a Chat Message

1. **User types a message** → Frontend captures it
2. **Frontend sends message** → Backend receives it
3. **Backend asks AI** → OpenAI processes the request
4. **AI streams response** → Backend forwards it in real-time
5. **Frontend displays response** → User sees it appear word-by-word
6. **Backend saves conversation** → Database stores it for later

## 🛠 Detailed Code Explanation

### 1. Backend (`chat_app.py`)

This is the heart of the application - a Python server that handles all the logic.

#### Setting Up the AI Agent
```python
from pydantic_ai import Agent
from dotenv import load_dotenv

# Load your API key from .env file
load_dotenv()

# Create an AI agent using OpenAI's GPT-4o model
agent = Agent('openai:gpt-4o')
```

**What this does**: Creates a connection to OpenAI's AI model. Think of it as hiring an AI assistant.

#### Handling Chat Messages
```python
@app.post('/chat/')
async def post_chat(prompt: str, database: Database = Depends(get_db)):
    async def stream_messages():
        # Send user message immediately
        yield user_message_json
        
        # Get chat history for context
        messages = await database.get_messages()
        
        # Ask AI and stream the response
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                yield ai_response_json
        
        # Save conversation to database
        await database.add_messages(result.new_messages_json())
```

**What this does**: 
- Receives your message
- Retrieves past conversation for context
- Asks the AI and streams its response back
- Saves everything to the database

#### Database Storage
```python
class Database:
    async def add_messages(self, messages: bytes):
        # Save messages to SQLite database
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (message_list) VALUES (?);',
            messages
        )
    
    async def get_messages(self) -> list[ModelMessage]:
        # Retrieve all past messages
        rows = await self._asyncify(c.fetchall)
        return messages
```

**What this does**: Manages the SQLite database that remembers all your conversations.

### 2. Frontend (`chat_app.html`)

The web interface that users see and interact with.

#### Basic Structure
```html
<main class="border rounded mx-auto my-5 p-4">
    <h1>Chat App</h1>
    <p>Ask me anything...</p>
    
    <!-- Chat messages appear here -->
    <div id="conversation" class="px-2"></div>
    
    <!-- Loading spinner -->
    <div id="spinner"></div>
    
    <!-- Message input form -->
    <form method="post">
        <input id="prompt-input" name="prompt" class="form-control"/>
        <button class="btn btn-primary mt-2">Send</button>
    </form>
</main>
```

**What this does**: Creates a clean chat interface with Bootstrap styling.

### 3. Real-time Features (`chat_app.ts`)

TypeScript code that handles the interactive chat features.

#### Streaming Messages
```typescript
async function onFetchResponse(response: Response): Promise<void> {
    const reader = response.body.getReader()
    let text = ''
    
    while (true) {
        const {done, value} = await reader.read()
        if (done) break
        
        text += new TextDecoder().decode(value)
        addMessages(text)  // Update UI in real-time
    }
}
```

**What this does**: Receives the AI's response piece by piece and displays it immediately, creating the "typing" effect.

#### Message Display
```typescript
function addMessages(responseText: string) {
    const messages = responseText.split('\n')
        .filter(line => line.length > 1)
        .map(j => JSON.parse(j))
    
    for (const message of messages) {
        const msgDiv = document.createElement('div')
        msgDiv.innerHTML = marked.parse(message.content)  // Convert markdown
        convElement.appendChild(msgDiv)
    }
}
```

**What this does**: Takes the raw message data and converts it into properly formatted HTML that appears in the chat.

## 🔧 Key Technologies Explained

### PydanticAI
- **What it is**: A Python library for building AI applications
- **Why we use it**: Makes it easy to connect to different AI models (OpenAI, Anthropic, etc.)
- **Key benefit**: Handles complex AI interactions with simple code

### FastAPI
- **What it is**: A modern Python web framework
- **Why we use it**: Fast, automatic API documentation, built-in async support
- **Key benefit**: Perfect for real-time applications like chat

### OpenAI GPT-4o
- **What it is**: One of the most advanced AI language models
- **Why we use it**: Excellent conversation abilities, good at following instructions
- **Key benefit**: Provides human-like responses

### SQLite
- **What it is**: A lightweight database that doesn't need a separate server
- **Why we use it**: Simple to set up, perfect for storing chat history
- **Key benefit**: No complex database setup required

## 🔐 Security & API Keys

### What is an API Key?
An API key is like a password that lets your app talk to OpenAI's servers. It's how OpenAI knows:
- Who is making the request
- How to bill you for usage
- Whether you have permission to use their AI

### Keeping Your API Key Safe
```bash
# ✅ Good - In .env file (never shared)
OPENAI_API_KEY=sk-proj-abc123...

# ❌ Bad - In your code (everyone can see it)
api_key = "sk-proj-abc123..."
```

**Important**: Never put your API key directly in your code or share it publicly!

## 💡 Understanding the Chat Flow

Let's trace through what happens when you send a message:

### Step 1: User Input
```html
<!-- User types "Hello, how are you?" and clicks Send -->
<input id="prompt-input" name="prompt" value="Hello, how are you?"/>
```

### Step 2: Frontend Processing
```typescript
// Form submission triggers this
async function onSubmit(e: SubmitEvent) {
    e.preventDefault()
    const body = new FormData(e.target as HTMLFormElement)
    const response = await fetch('/chat/', {method: 'POST', body})
    await onFetchResponse(response)
}
```

### Step 3: Backend Processing
```python
# FastAPI receives the POST request
@app.post('/chat/')
async def post_chat(prompt: str):
    # Get conversation history
    messages = await database.get_messages()
    
    # Ask AI with context
    async with agent.run_stream(prompt, message_history=messages) as result:
        # Stream response back
        async for text in result.stream():
            yield json.dumps(ai_message)
```

### Step 4: AI Processing
The AI (GPT-4o) receives:
- Your current message: "Hello, how are you?"
- Previous conversation history
- System instructions about how to behave

### Step 5: Response Streaming
```python
# AI responds with something like: "Hello! I'm doing well, thank you for asking..."
# This gets streamed back word by word
```

### Step 6: Database Storage
```python
# After the conversation, both messages are saved:
# User: "Hello, how are you?"
# AI: "Hello! I'm doing well, thank you for asking..."
await database.add_messages(result.new_messages_json())
```

## 🎨 Customization Ideas

### Change the AI Model
```python
# Current: OpenAI GPT-4o
agent = Agent('openai:gpt-4o')

# Try: OpenAI GPT-3.5 (cheaper)
agent = Agent('openai:gpt-3.5-turbo')

# Try: Anthropic Claude
agent = Agent('anthropic:claude-3-haiku')
```

### Add System Instructions
```python
agent = Agent(
    'openai:gpt-4o',
    system_prompt="You are a helpful cooking assistant. Always provide recipe suggestions."
)
```

### Customize the UI
```css
/* In chat_app.html, modify the styles */
#conversation .user::before {
    content: '👤 You: ';  /* Add emoji */
}
#conversation .model::before {
    content: '🤖 AI: ';   /* Add emoji */
}
```

## 🐛 Troubleshooting

### "OpenAI API key not found"
- Make sure your `.env` file exists
- Check that `OPENAI_API_KEY=your_key_here` is correctly formatted
- Restart the server after creating/modifying `.env`

### "Module not found" errors
- Run `pip install -r requirements.txt` again
- Make sure you're in the right directory
- Try `pip install --upgrade pip` first

### Server won't start
- Check if port 8000 is already in use
- Try `python -m uvicorn chat_app:app --port 8001` to use a different port

### Chat not responding
- Check browser console for errors (F12 → Console)
- Verify your OpenAI API key has credits
- Check network connectivity

## 💰 Cost Considerations

This app uses OpenAI's API, which charges based on usage:
- **GPT-4o**: ~$0.005 per 1K tokens (roughly 750 words)
- **GPT-3.5-turbo**: ~$0.001 per 1K tokens (much cheaper)

**Tip**: Start with GPT-3.5-turbo for testing, upgrade to GPT-4o for production.

## 🚀 Next Steps

Ready to enhance your chat app? Try these ideas:

1. **Add user authentication** - Let multiple people use the app
2. **File uploads** - Let users send images or documents
3. **Voice chat** - Add speech-to-text and text-to-speech
4. **Different AI personalities** - Create multiple chat bots
5. **Export conversations** - Download chat history as PDF
6. **Deploy online** - Host on Heroku, Railway, or similar platforms

## 📚 Learning Resources

- **PydanticAI Documentation**: [ai.pydantic.dev](https://ai.pydantic.dev)
- **FastAPI Tutorial**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **OpenAI API Guide**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **TypeScript Handbook**: [typescriptlang.org](https://www.typescriptlang.org)

## 🤝 Contributing

Found a bug or want to add a feature? Contributions are welcome! Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Chatting!** 🎉

*Built with ❤️ using PydanticAI, FastAPI, and OpenAI* 