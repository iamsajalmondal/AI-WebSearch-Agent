import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticBaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, save_tool, wiki_tool

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="Research Assistant API")

# Pydantic model for response
class ResearchResponse(PydanticBaseModel):
    topic: str
    summary: str
    tools_used: list[str]
    sources: list[str]

# Pydantic model for request
class ResearchRequest(PydanticBaseModel):
    query: str

# Initialize LLM and tools
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=google_api_key, temperature=0.5)
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
         You are a research assistant. Current date is March 28, 2025. Use tools like DuckDuckGo to fetch the most recent data available when answering queries about current events or updates.
         You are a research assistant that helps generate research papers.
         Answer the user's query and use necessary tools to generate the research paper.
         Wrap the output in this format and provide no other text: \n {format_instructions}
         """),
        ('human', "{query}"),
        ('placeholder', "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, save_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

@app.post("/research", response_model=ResearchResponse)
async def perform_research(request: ResearchRequest):
    try:
        # Invoke the agent
        raw_response = agent_executor.invoke({"query": request.query})
        
        # Debug: Print the raw response to understand its structure
        print("Raw Response:", raw_response)
        
        # Extract the output (assuming it’s a string containing JSON)
        # The agent’s output is likely in raw_response["output"] as a string
        output = raw_response.get("output")
        if isinstance(output, str):
            structured_response = parser.parse(output)
        else:
            raise ValueError("Unexpected output format from agent_executor")
        
        return structured_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)