from typing import Dict, Type
from avachain.avachain_executor import AvaAgent
from avachain import OpenaiLLM, BaseTool, CallbackHandler
from pydantic import BaseModel, Field
import requests
import warnings

warnings.filterwarnings("ignore")

# Server Authorization Token
server_auth_token = (
    "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzdkNDk0N2NiZjNkZTU4YTA3MjcyN2IiLCJvcyI6Im9zIiwiZGV2aWNlTmFtZSI6ImRldmljZU5hbWUiLCJ1c2VyVHlwZSI6ImVudGVycHJpc2UiLCJpYXQiOjE3MzY1ODQ4OTIsImV4cCI6MTczNzc5NDQ5Mn0.tdEomg9vnNUwgCPEpnd7sfbYyL65mg4QS4vtfGAKE5ZeeJn8Fyk8ZingRmhoOq8cVLXR_qQSHmHg84eJuSU7vg"
)

# API Base URL
embedding_base_url = "https://node-ms-f7nozesjca-em.a.run.app"  # Replace with your base URL


class EmbeddingSearchToolInput(BaseModel):
    text: str = Field(description="Query text for embedding search.")
    filename: str = Field(default=None, description="Filename filter (optional).")
    folder_name: str = Field(default=None, description="Folder name filter (optional).")


class EmbeddingSearchTool(BaseTool):
    name: str = "embeddingSearchTool"
    description: str = "Tool to perform embedding search queries."
    args_schema: Type[BaseModel] = EmbeddingSearchToolInput

    def _run(self, text: str, filename: str = None, folder_name: str = None):
        """Perform embedding search query."""
        endpoint = f"{embedding_base_url}/api/v1/query_vec"
        payload = {"text": text}
        if filename:
            payload["filename"] = filename
        if folder_name:
            payload["folder_name"] = folder_name

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {server_auth_token}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "true":
                results = data.get("results", [])
                return (
                    f"Search results:\n"
                    + "\n".join(
                        [
                            f"Text: {result['text']}\nID: {result['id']}\nFilename: {result['filename']}\nFolder: {result['folder_name']}\nScore: {result['score']}"
                            for result in results
                        ]
                    )
                )
            else:
                return f"Failed to perform search: {data.get('error', 'Unknown error')}"
        except requests.RequestException as e:
            return f"Error during API call: {str(e)}"


# Callback Handler
class MainAgentCallbackHandler(CallbackHandler):
    def on_agent_run(self, input_msg: str):
        print(f"Processing input: {input_msg}")
        return super().on_agent_run(input_msg)

    def on_general_response(self, response: str):
        print(f"Response: {response}")
        return super().on_general_response(response)

    def on_tool_call(self, tool_name: str, tool_params: Dict):
        print(f"Tool called: {tool_name}")
        return super().on_tool_call(tool_name=tool_name, tool_params=tool_params)


# Initialize LLM
openai_llm = OpenaiLLM(
    model="gpt-4o-mini",
    base_url="https://avaai.pathor.in/api/v1/users/",
    api_key=server_auth_token,
    max_tokens=450,
    temperature=0.3,
    frequency_penalty=1.0,
    presence_penalty=0.5,
)

# System Prompt for the Nurse Agent
nurse_sys_prompt = """
Kasturi Didi is here to assist you with health advice and embedding search queries. She is caring, supportive, and knowledgeable, always ready to help with your concerns. Ask her about health or search-related tasks!
"""

# Initialize the Agent
nurse_agent = AvaAgent(
    sys_prompt=nurse_sys_prompt,
    ava_llm=openai_llm,
    agent_name_identifier="KASTURI_DIDI_AGENT",
    tools_list=[
        EmbeddingSearchTool(),  # Add the embedding search tool
    ],
    pickup_mes_count=5,
    logging=True,
    deeper_logs=False,
    callback_handler=MainAgentCallbackHandler(),
    max_agent_iterations=3,
)

run_locally = True

if run_locally:
    def run_agent():
        print("Kasturi Didi is here to assist you! Type 'exit' to quit.")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Kasturi Didi: Take care and stay healthy! Goodbye!")
                break
            try:
                response = nurse_agent.run(msg=user_input)
                print(response)
            except Exception as e:
                print(f"Error: {str(e)}")

    if __name__ == "__main__":
        run_agent()
else:
    from avachain import persona_creator
    token = server_auth_token
    persona_creator.push_to_store(
        name="Kasturi Didi",
        title="Health and Search Assistant",
        public_description="""Hi, I am Kasturi Didi. I can assist you with health advice and embedding search queries.""",
        is_AssistantProfile=False,
        logo_path=r"AvaTools\Urav\Persona\kasturi_didi.jpg",
        gender="female",
        agent_obj=nurse_agent,
        can_be_used_as_tool=True,
        age=40,
        supported_os=["nt"],
        tags=["Health", "Care", "Search"],
        behaviour=["Compassionate", "Supportive", "Knowledgeable"],
        langauges=["english", "hindi"],
        isPublic=True,
        action="update",
        token=token,
        custom_personaId="kasturi_didi",
    )
