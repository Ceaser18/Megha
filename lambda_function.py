from fastapi import FastAPI, HTTPException
from mangum import Mangum
from typing import Dict
import os
import json
import requests
from dotenv import load_dotenv
from avachain import OpenaiLLM, CallbackHandler
from avachain.avachain_executor import AvaAgent
from fastapi.responses import HTMLResponse # For HTML response

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Global variables
class GlobalVariables:
    current_user_token: str = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzdlYzJhZmExN2JkNjMzYjU3ZTBkNTMiLCJvcyI6Im9zIiwiZGV2aWNlTmFtZSI6ImRldmljZU5hbWUiLCJ1c2VyVHlwZSI6ImF2YSIsImlhdCI6MTczNzAxMjkwNiwiZXhwIjoxNzM4MjIyNTA2fQ.Bt7KNYunJVw93I8I4aiidbaYk1nJEOQi3bsZKIgXX2aH72vv27Q8Bc6Blb2Ru-TdS5hcDbMsrUaTjew7DHKZBA'



# Endpoint to get user token

# Initialize OpenAI LLM
openai_llm = OpenaiLLM(
    model=os.getenv("MODEL", "gpt-4o"),
    api_key=GlobalVariables.current_user_token,
    base_url="https://avaai.pathor.in/api/v1/users/",
    max_tokens=450,
    temperature=0.7,
)

# Callback Handler
class MainAgentCallbackHandler(CallbackHandler):
    def on_tool_call(self, tool_name: str, tool_params: Dict):
        print(f"AGENT TAKING ACTION: {tool_name}")
        return super().on_tool_call(tool_name=tool_name, tool_params=tool_params)

# System prompt for Kasturi Didi
kasturi_sys_prompt = """
Megha Didi is here to assist you with health advice and embedding search queries.
She is caring, supportive, and knowledgeable, always ready to help with your concerns.
Ask her about health or search-related tasks!

Rules:
1. Provide concise, clear, and actionable advice.
2. If no relevant information is found, politely decline to answer.
"""

# Initialize Kasturi Didi Agent
kasturi_agent = AvaAgent(
    sys_prompt=kasturi_sys_prompt,
    ava_llm=openai_llm,
    agent_name_identifier="KASTURI_DIDI_AGENT",
    tools_list=[],  # Add required tools if needed
    callback_handler=MainAgentCallbackHandler(),
    max_agent_iterations=3,
    logging=True,  # Enable detailed logging
    deeper_logs=True  # Enable deeper logs
)


# Endpoint to handle queries
@app.post("/query")
async def query(event: Dict):
    try:
        user_message = event.get("query", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Query is required")

        # Run the agent with the user query
        result = kasturi_agent.run(msg=user_message)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/query")
async def query(event: Dict):
    try:
        user_message = event.get("query", "")
        logger.info(f"Received query: {user_message}")
        if not user_message:
            raise HTTPException(status_code=400, detail="Query is required")

        # Run the agent with the user query
        result = kasturi_agent.run(msg=user_message)
        logger.info(f"Agent response: {result}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': result
            })
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }




@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title>Welcome to Megha Didi's Assistant</title>
        </head>
        <body>
            <h1>Welcome to Megha Didi's Assistant!</h1>
            <p>Click the link below to access the Streamlit app:</p>
            <a href="http://192.168.0.105:8501" target="_blank">
                Go to Streamlit App
            </a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)



# AWS Lambda handler
handler = Mangum(app)
