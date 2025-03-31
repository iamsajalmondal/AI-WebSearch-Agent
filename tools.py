from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import  datetime


def save_to_text(data:str, filename: str = 'research_output.txt'):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formated_text = f"Research Output: {timestamp}\n\n{data}"
    with open(filename, 'a', encoding="utf-8") as f:
        f.write(formated_text)
    return f"Data Saved to {filename}"

save_tool = Tool(
    name="Save_to_text",
    description="Save the research output to a text file.",
    func=save_to_text
)    


search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="DuckDuckGo_Search",
    description="Searches DuckDuckGo for the query and returns the top search results.",
    func =search.run
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

