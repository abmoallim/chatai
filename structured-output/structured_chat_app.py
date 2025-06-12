from __future__ import annotations as _annotations

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, TypeVar, List, Optional
from enum import Enum

import fastapi
import logfire
import markdown
from fastapi import Depends, Request
from fastapi.responses import FileResponse, Response, StreamingResponse, HTMLResponse
from typing_extensions import LiteralString, ParamSpec, TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

# Configure logfire
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()

# Structured Output Models
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    title: str = Field(description="The task title")
    description: str = Field(description="Detailed description of the task")
    priority: TaskPriority = Field(description="Task priority level")
    estimated_time: str = Field(description="Estimated time to complete (e.g., '2 hours', '30 minutes')")
    category: str = Field(description="Task category (e.g., 'work', 'personal', 'study')")

class TaskList(BaseModel):
    """A structured task list response"""
    tasks: List[Task] = Field(description="List of tasks")
    total_tasks: int = Field(description="Total number of tasks")
    summary: str = Field(description="Brief summary of the task list")

class RecipeIngredient(BaseModel):
    name: str = Field(description="Ingredient name")
    amount: str = Field(description="Amount needed (e.g., '2 cups', '1 tbsp')")
    notes: Optional[str] = Field(description="Additional notes about the ingredient", default=None)

class Recipe(BaseModel):
    """A structured recipe response"""
    name: str = Field(description="Recipe name")
    description: str = Field(description="Brief description of the dish")
    prep_time: str = Field(description="Preparation time")
    cook_time: str = Field(description="Cooking time")
    servings: int = Field(description="Number of servings")
    difficulty: Literal["easy", "medium", "hard"] = Field(description="Difficulty level")
    ingredients: List[RecipeIngredient] = Field(description="List of ingredients")
    instructions: List[str] = Field(description="Step-by-step cooking instructions")

class WeatherCondition(str, Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    FOGGY = "foggy"

class WeatherForecast(BaseModel):
    """A structured weather forecast response"""
    location: str = Field(description="Location name")
    current_condition: WeatherCondition = Field(description="Current weather condition")
    temperature: str = Field(description="Current temperature with unit")
    humidity: str = Field(description="Humidity percentage")
    wind_speed: str = Field(description="Wind speed with unit")
    forecast_summary: str = Field(description="Brief forecast summary")
    recommendations: List[str] = Field(description="Clothing or activity recommendations")

class ProductReview(BaseModel):
    """A structured product review"""
    product_name: str = Field(description="Name of the product")
    rating: int = Field(description="Rating out of 5 stars", ge=1, le=5)
    pros: List[str] = Field(description="List of positive aspects")
    cons: List[str] = Field(description="List of negative aspects")
    summary: str = Field(description="Overall review summary")
    recommendation: bool = Field(description="Whether to recommend this product")

# Create different agents for different types of structured outputs
task_agent = Agent('openai:gpt-4o', result_type=TaskList)
recipe_agent = Agent('openai:gpt-4o', result_type=Recipe)
weather_agent = Agent('openai:gpt-4o', result_type=WeatherForecast)
review_agent = Agent('openai:gpt-4o', result_type=ProductReview)
# General structured agent for custom responses
general_agent = Agent('openai:gpt-4o')

THIS_DIR = Path(__file__).parent

@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    async with Database.connect() as db:
        yield {'db': db}

app = fastapi.FastAPI(lifespan=lifespan, title="Structured Output Chat App")
logfire.instrument_fastapi(app)

@app.get('/')
async def index() -> FileResponse:
    return FileResponse((THIS_DIR / 'structured_chat_app.html'), media_type='text/html')

@app.get('/structured_chat_app.ts')
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser."""
    return FileResponse((THIS_DIR / 'structured_chat_app.ts'), media_type='text/plain')

@app.get('/readme')
async def readme() -> HTMLResponse:
    """Serve the README as HTML like GitHub does"""
    readme_path = THIS_DIR / 'README.md'
    if not readme_path.exists():
        return HTMLResponse("README.md not found", status_code=404)
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content, 
        extensions=['codehilite', 'fenced_code', 'tables', 'toc']
    )
    
    # Wrap in a nice HTML template
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Structured Output Chat App - README</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
        <style>
            .readme-container {{
                max-width: 900px;
                margin: 20px auto;
                padding: 20px;
                background: white;
                border: 1px solid #d1d9e0;
                border-radius: 6px;
            }}
            pre {{
                background-color: #f6f8fa !important;
                border-radius: 6px;
                padding: 16px;
                overflow-x: auto;
            }}
            code {{
                background-color: rgba(175,184,193,0.2);
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 85%;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #d1d5da;
                padding-left: 16px;
                color: #6a737d;
            }}
            .nav-link {{
                color: #0969da;
                text-decoration: none;
            }}
        </style>
    </head>
    <body style="background-color: #f6f8fa;">
        <nav class="navbar navbar-light bg-light border-bottom">
            <div class="container">
                <a class="navbar-brand" href="/">← Back to Chat App</a>
                <span class="navbar-text">Structured Output README</span>
            </div>
        </nav>
        <div class="readme-container">
            {html_content}
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
    </body>
    </html>
    """
    
    return HTMLResponse(full_html)

async def get_db(request: Request) -> Database:
    return request.state.db

@app.get('/chat/')
async def get_chat(database: Database = Depends(get_db)) -> Response:
    msgs = await database.get_messages()
    return Response(
        b'\n'.join(json.dumps(to_chat_message(m)).encode('utf-8') for m in msgs),
        media_type='text/plain',
    )

class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""
    role: Literal['user', 'model']
    timestamp: str
    content: str
    message_type: Literal['text', 'structured']
    structured_data: Optional[dict]

def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            assert isinstance(first_part.content, str)
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
                'message_type': 'text',
                'structured_data': None,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
                'message_type': 'text',
                'structured_data': None,
            }
    raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')

def detect_intent(prompt: str) -> str:
    """Simple intent detection based on keywords"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['task', 'todo', 'plan', 'schedule', 'organize']):
        return 'tasks'
    elif any(word in prompt_lower for word in ['recipe', 'cook', 'ingredient', 'dish', 'meal']):
        return 'recipe'
    elif any(word in prompt_lower for word in ['weather', 'forecast', 'temperature', 'rain', 'sunny']):
        return 'weather'
    elif any(word in prompt_lower for word in ['review', 'product', 'rating', 'recommend', 'opinion']):
        return 'review'
    else:
        return 'general'

@app.post('/chat/')
async def post_chat(
    prompt: Annotated[str, fastapi.Form()], database: Database = Depends(get_db)
) -> StreamingResponse:
    async def stream_messages():
        """Streams structured responses based on detected intent."""
        # Stream the user prompt
        yield (
            json.dumps({
                'role': 'user',
                'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                'content': prompt,
                'message_type': 'text',
                'structured_data': None,
            }).encode('utf-8') + b'\n'
        )
        
        # Detect intent and choose appropriate agent
        intent = detect_intent(prompt)
        
        # Get chat history
        messages = await database.get_messages()
        
        try:
            if intent == 'tasks':
                result = await task_agent.run(
                    f"Create a task list based on this request: {prompt}",
                    message_history=messages
                )
                structured_data = result.data.model_dump()
                content = f"I've created a structured task list for you with {result.data.total_tasks} tasks."
                
            elif intent == 'recipe':
                result = await recipe_agent.run(
                    f"Provide a recipe based on this request: {prompt}",
                    message_history=messages
                )
                structured_data = result.data.model_dump()
                content = f"Here's a {result.data.difficulty} recipe for {result.data.name} (serves {result.data.servings})."
                
            elif intent == 'weather':
                result = await weather_agent.run(
                    f"Provide a weather forecast based on this request: {prompt}. Note: This is a demo - provide realistic but fictional weather data.",
                    message_history=messages
                )
                structured_data = result.data.model_dump()
                content = f"Here's the weather forecast for {result.data.location}."
                
            elif intent == 'review':
                result = await review_agent.run(
                    f"Provide a product review based on this request: {prompt}",
                    message_history=messages
                )
                structured_data = result.data.model_dump()
                content = f"Here's a structured review for {result.data.product_name} ({result.data.rating}/5 stars)."
                
            else:
                # General response
                result = await general_agent.run(prompt, message_history=messages)
                structured_data = None
                content = result.data
            
            # Stream the structured response
            response_message = {
                'role': 'model',
                'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                'content': content,
                'message_type': 'structured' if structured_data else 'text',
                'structured_data': structured_data,
            }
            
            yield json.dumps(response_message).encode('utf-8') + b'\n'
            
            # Save to database
            await database.add_messages(result.new_messages_json())
            
        except Exception as e:
            # Error handling
            error_message = {
                'role': 'model',
                'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                'content': f"Sorry, I encountered an error: {str(e)}",
                'message_type': 'text',
                'structured_data': None,
            }
            yield json.dumps(error_message).encode('utf-8') + b'\n'
    
    return StreamingResponse(stream_messages(), media_type='text/plain')

P = ParamSpec('P')
R = TypeVar('R')

@dataclass
class Database:
    """Database for storing structured chat messages in SQLite."""
    
    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(cls, file: Path = Path('structured-output/structured_chat.db')):
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        con = await loop.run_in_executor(executor, cls._connect, file)
        slf = cls(con, loop, executor)
        try:
            yield slf
        finally:
            await slf._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        # Ensure the directory exists
        file.parent.mkdir(exist_ok=True)
        con = sqlite3.connect(str(file))
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, message_list TEXT);'
        )
        con.commit()
        return con

    async def add_messages(self, messages: bytes):
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (message_list) VALUES (?);',
            messages,
            commit=True,
        )

    async def get_messages(self) -> list[ModelMessage]:
        c = await self._asyncify(
            self._execute, 'SELECT message_list FROM messages order by id'
        )
        rows = await self._asyncify(c.fetchall)
        messages: list[ModelMessage] = []
        for row in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return messages

    def _execute(
        self, sql: LiteralString, *args: Any, commit: bool = False
    ) -> sqlite3.Cursor:
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        return await self._loop.run_in_executor(
            self._executor,
            partial(func, **kwargs),
            *args,
        )

if __name__ == '__main__':
    import uvicorn
    
    # Run on a different port to avoid conflicts
    uvicorn.run(
        'structured_chat_app:app', 
        reload=True, 
        reload_dirs=[str(THIS_DIR)],
        port=8001,
        host="127.0.0.1"
    ) 