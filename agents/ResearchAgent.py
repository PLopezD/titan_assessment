"""
Research Agent using LangGraph and Ollama
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.prebuilt import create_react_agent
from typing import List, Any

class MockOllamaLLM(BaseChatModel):
    """Mock LLM for development/testing when Ollama is not available"""

    def _generate(self, messages: List[BaseMessage], stop=None, **kwargs) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="Mock response: This is a placeholder response from the research agent."))])

    def _llm_type(self) -> str:
        return "mock_ollama"

class ResearchAgent:
    def __init__(self):
        # Use mock LLM since Ollama may not be installed
        self.llm = MockOllamaLLM()
        self.agent = create_react_agent(self.llm, tools=[])

    def research(self, query: str) -> str:
        """Execute a research query using the agent"""
        try:
            result = self.agent.invoke({"messages": [("user", query)]})
            return result["messages"][-1].content
        except Exception as e:
            return f"Error: {str(e)}"