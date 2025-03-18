import os
import pytz
from datetime import datetime

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.agent import ReActChatFormatter
from llama_index.core.llms import MessageRole
from llama_index.llms.openai_like import OpenAILike

from dotenv import load_dotenv

load_dotenv()

def get_current_username(input: str) -> str:
    "Get the username of the current user."
    return "Dennis"

get_current_username_tool = FunctionTool.from_defaults(fn=get_current_username)

def get_current_location(username: str) -> str:
    "Get the current timezone location of the user for a given username."
    print(username)
    if "Dennis" in username:
        return "Europe/Berlin"
    else:
        return "America/New_York"

get_current_location_tool = FunctionTool.from_defaults(fn=get_current_location)

def get_current_time(location: str) -> str:
    "Get the current time in the given location. The pytz is used to get the timezone for that location. Location names should be in a format like America/Seattle, Asia/Bangkok, Europe/London. Anything in Germany should be Europe/Berlin"
    try:
        print("get current time for location: ", location)
        location = str.replace(location, " ", "")
        location = str.replace(location, "\"", "")
        location = str.replace(location, "\n", "")
        # Get the timezone for the city
        timezone = pytz.timezone(location)

        # Get the current time in the timezone
        now = datetime.now(timezone)
        current_time = now.strftime("%I:%M:%S %p")

        return current_time
    except Exception as e:
        print("Error: ", e)
        return "Sorry, I couldn't find the timezone for that location."

get_current_time_tool = FunctionTool.from_defaults(fn=get_current_time)

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

llm = OpenAILike(model=model_name, api_base=endpoint, api_key=token)

from llama_index.core import PromptTemplate

react_system_header_str = """\

You are designed to help with a variety of tasks, from answering questions \
    to providing summaries to other types of analyses.

## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.
```

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""
react_system_prompt = PromptTemplate(react_system_header_str)

agent = ReActAgent.from_tools(
    [get_current_username_tool, get_current_location_tool, get_current_time_tool],
    llm=llm,
    react_chat_formatter=ReActChatFormatter.from_defaults(
        observation_role=MessageRole.TOOL
    ),
    verbose=False,
)

# agent = ReActAgent.from_tools([multiply_tool, add_tool], llm=llm, verbose=True)

# agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
# agent.reset()

response_gen = agent.stream_chat("What time is it here? Figure it out by using the tools available to you.")

# msg = ""
# for delta in response_gen.response_gen:
#     msg += delta
# print(msg)

response_gen.print_response_stream()

