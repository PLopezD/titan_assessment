"""
Research Agent using LangGraph workflow
"""

import os
from typing import TypedDict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake import FakeListLLM
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from tools.wikipedia_tool import wikipedia_search
from tools.arxiv_tool import arxiv_search
from tools.fred_tool import fred_search
import random

class State(TypedDict):
    query: str
    result: str
    session_id: str
    tool_calls: List[str]

class ResearchAgent:
    def __init__(self):
        # Use Google AI Studio with free Gemini model, fallback to mock for development
        api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")

        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=api_key
            )
            # Create react agent with Wikipedia, arXiv, and FRED tools
            self.react_agent = create_react_agent(self.llm, [wikipedia_search, arxiv_search, fred_search])
        else:
            # For development without API key, create a simple mock agent
            self.llm = FakeListLLM(responses=["This is a mock response for development purposes."])
            self.react_agent = None

        # Create the workflow
        workflow = StateGraph(State)
        workflow.add_node("research", self.research_node)
        workflow.add_edge(START, "research")
        workflow.add_edge("research", END)

        self.agent = workflow.compile()

    def research_node(self, state: State) -> State:
        """Research node that uses react_agent with tool logging"""
        query = state["query"]
        session_id = state.get("session_id")
        tool_calls = state.get("tool_calls", [])

        try:
            result = ""
            if self.react_agent:
                # Use react agent with tools for research
                response = self.react_agent.invoke({"messages": [HumanMessage(content=f"Research and provide comprehensive information about: {query}")]})

                # Log tool usage from react agent messages
                for message in response["messages"]:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.get('name', 'unknown_tool')
                            tool_calls.append(f"Tool: {tool_name}")
                    elif hasattr(message, 'content') and "Action:" in str(message.content):
                        # Parse action from content for older LangChain versions
                        content = str(message.content)
                        if "wikipedia_search" in content:
                            tool_calls.append("Tool: wikipedia_search")
                        if "arxiv_search" in content:
                            tool_calls.append("Tool: arxiv_search")

                # Extract the final message content
                if response["messages"]:
                    result = response["messages"][-1].content
                else:
                    result = "No response from research agent"
            else:
                # Fallback for development without API key
                # Use all tools directly and log them
                tool_calls.append("Tool: wikipedia_search")
                wiki_result = wikipedia_search.invoke({"query": query})
                tool_calls.append("Tool: arxiv_search")
                arxiv_result = arxiv_search.invoke({"query": query})
                tool_calls.append("Tool: fred_search")
                fred_result = fred_search.invoke({"query": query})
                result = f"Mock research result for '{query}':\n\nWikipedia: {wiki_result}\n\narXiv: {arxiv_result}\n\nFRED: {fred_result}"

        except Exception as e:
            result = f"Error in research: {str(e)}"

        return {"query": query, "result": result, "session_id": session_id, "tool_calls": tool_calls}

    def research(self, query: str) -> dict:
        """Execute a research query using the workflow"""
        initial_state = {"query": query, "result": "", "session_id": str(random.randint(1, 1000000)), "tool_calls": []}
        final_state = self.agent.invoke(initial_state)

        return {
            "result": final_state["result"],
            "tool_calls": final_state.get("tool_calls", []),
            "session_id": final_state["session_id"]
        }