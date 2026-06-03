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
    raw_results: str
    synthesized_result: str
    scope_check: str

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
        workflow.add_node("scope_check", self.scope_check_node)
        workflow.add_node("research", self.research_node)
        workflow.add_node("synthesize", self.synthesis_node)
        workflow.add_edge(START, "scope_check")
        workflow.add_conditional_edges(
            "scope_check",
            self.route_after_scope,
            {"research": "research", "out_of_scope": END}
        )
        workflow.add_edge("research", "synthesize")
        workflow.add_edge("synthesize", END)

        self.agent = workflow.compile()

    def scope_check_node(self, state: State) -> State:
        """Pre-research node that validates query scope"""
        query = state["query"]
        session_id = state.get("session_id")

        # Define out-of-scope query patterns
        out_of_scope_keywords = [
            "best restaurant", "recommend", "opinion", "taste", "favorite",
            "what should i", "personal preference", "subjective", "rating",
            "review", "which is better", "personal experience"
        ]

        # Define in-scope query patterns
        in_scope_keywords = [
            "what is", "how does", "definition", "explain", "research", "study",
            "data", "statistics", "history", "facts", "GDP", "inflation",
            "unemployment", "economy", "science", "academic", "paper"
        ]

        query_lower = query.lower()

        # Check for obvious out-of-scope patterns
        if any(keyword in query_lower for keyword in out_of_scope_keywords):
            scope_check = "out_of_scope"
            result = "Out of Scope: This research agent is designed for factual, academic, and economic research. Questions asking for personal recommendations, opinions, or subjective evaluations are outside the scope of available tools (Wikipedia, arXiv, FRED)."
        # Check for in-scope patterns
        elif any(keyword in query_lower for keyword in in_scope_keywords):
            scope_check = "in_scope"
            result = ""
        # Use LLM for borderline cases
        else:
            try:
                scope_prompt = f"""
Determine if this query is within scope for a research agent with access to Wikipedia (general knowledge), arXiv (academic papers), and FRED (economic data).

Query: "{query}"

Respond with only "IN_SCOPE" or "OUT_OF_SCOPE".

IN_SCOPE examples:
- What is machine learning?
- GDP growth rate trends
- History of quantum computing
- Economic impact of inflation

OUT_OF_SCOPE examples:
- Best restaurant in New York
- Personal recommendations
- Subjective opinions
- Product reviews

Response:"""

                if hasattr(self.llm, 'invoke') and hasattr(self.llm, 'bind_tools'):
                    scope_response = self.llm.invoke([HumanMessage(content=scope_prompt)])
                    if "OUT_OF_SCOPE" in scope_response.content.upper():
                        scope_check = "out_of_scope"
                        result = "Out of Scope: This research agent is designed for factual, academic, and economic research. Your query appears to be outside the scope of available tools (Wikipedia, arXiv, FRED)."
                    else:
                        scope_check = "in_scope"
                        result = ""
                else:
                    # Conservative fallback - allow most queries through
                    scope_check = "in_scope"
                    result = ""

            except Exception as e:
                # On error, allow query through
                scope_check = "in_scope"
                result = ""

        return {
            "query": query,
            "result": result,
            "session_id": session_id,
            "tool_calls": [],
            "raw_results": "",
            "synthesized_result": "",
            "scope_check": scope_check
        }

    def route_after_scope(self, state: State) -> str:
        """Route based on scope check result"""
        return "research" if state["scope_check"] == "in_scope" else "out_of_scope"

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

        return {
            "query": query,
            "result": result,
            "session_id": session_id,
            "tool_calls": tool_calls,
            "raw_results": result,
            "synthesized_result": ""
        }

    def extract_source_details(self, raw_results, tool_calls: list) -> str:
        """Extract specific source details from raw results"""
        sources = []

        # Convert raw_results to string if it's a list
        if isinstance(raw_results, list):
            if raw_results and isinstance(raw_results[0], dict) and 'text' in raw_results[0]:
                text_content = raw_results[0]['text']
            else:
                text_content = str(raw_results)
        else:
            text_content = str(raw_results)

        for tool in tool_calls:
            if "wikipedia_search" in tool:
                # Extract Wikipedia article titles
                import re
                wiki_matches = re.findall(r'\*\*([^*]+)\*\*:', text_content)
                for match in wiki_matches:
                    if match and "Wikipedia" not in match and len(match) > 3:
                        sources.append(f"Wikipedia: '{match}' article (https://en.wikipedia.org/wiki/{match.replace(' ', '_')})")

            elif "arxiv_search" in tool:
                # Extract arXiv paper details
                import re
                arxiv_matches = re.findall(r'URL: (http://arxiv\.org/abs/[\w\.]+)', text_content)
                paper_titles = re.findall(r'arXiv search results.*?\*\*([^*]+)\*\*', text_content, re.DOTALL)
                for i, url in enumerate(arxiv_matches[:3]):
                    title = paper_titles[i] if i < len(paper_titles) else "Paper"
                    paper_id = url.split('/')[-1] if url else "Unknown"
                    sources.append(f"arXiv: '{title}' (ID: {paper_id}, {url})")

            elif "fred_search" in tool:
                # Extract FRED series details
                import re
                fred_matches = re.findall(r'\*\*([^*]+)\*\* \(ID: ([^)]+)\)', text_content)
                for title, series_id in fred_matches:
                    sources.append(f"FRED: '{title}' (Series ID: {series_id}, https://fred.stlouisfed.org/series/{series_id})")

        return sources

    def synthesis_node(self, state: State) -> State:
        """Synthesis node that creates a clear, compact response with proper citations"""
        query = state["query"]
        raw_results = state["raw_results"]
        session_id = state["session_id"]
        tool_calls = state["tool_calls"]

        try:
            # Extract specific source details
            source_details = self.extract_source_details(raw_results, tool_calls)

            # Create synthesis prompt with enhanced citation requirements
            synthesis_prompt = f"""
Based on the following research results, synthesize a clear and compact response to the user's question: "{query}"

Raw research data:
{raw_results}

Please provide a response that:
1. Synthesizes the information into a clear, coherent answer
2. Cites sources with SPECIFIC details including article titles, paper IDs, and URLs
3. Clearly distinguishes between factual information from sources and any reasoning/inference you add
4. Is compact but comprehensive

IMPORTANT: In the Sources section, you MUST include specific identifiers:
- For Wikipedia: Article titles and Wikipedia URLs
- For arXiv: Paper titles, arXiv IDs, and paper URLs
- For FRED: Series titles, series IDs, and FRED URLs

Format your response with:
- Main answer first
- Sources section with specific citations (titles, IDs, URLs)
- Note any reasoning or inference you've added beyond the source material

Tools used: {', '.join(tool_calls)}
Source details found: {source_details}
"""

            if hasattr(self.llm, 'invoke') and hasattr(self.llm, 'bind_tools'):
                # Use Google AI model for synthesis
                synthesis_response = self.llm.invoke([HumanMessage(content=synthesis_prompt)])
                synthesized_result = synthesis_response.content
            else:
                # Enhanced fallback synthesis with detailed citations
                sources_formatted = "\n".join([f"- {source}" for source in source_details]) if source_details else f"- Tools used: {', '.join(tool_calls)}"

                synthesized_result = f"""
**Answer to: {query}**

Based on the research conducted using {len(tool_calls)} tools, here is a synthesized response:

{raw_results}

**Sources with Details:**
{sources_formatted}

**Reasoning/Inference Added:**
This synthesis combines information from multiple sources to provide a comprehensive answer. No additional reasoning beyond source compilation was required.

**Session:** {session_id}
"""

        except Exception as e:
            synthesized_result = f"Error in synthesis: {str(e)}\n\nRaw results:\n{raw_results}"

        return {
            "query": query,
            "result": synthesized_result,
            "session_id": session_id,
            "tool_calls": tool_calls,
            "raw_results": raw_results,
            "synthesized_result": synthesized_result
        }

    def research(self, query: str) -> dict:
        """Execute a research query using the workflow"""
        initial_state = {
            "query": query,
            "result": "",
            "session_id": str(random.randint(1, 1000000)),
            "tool_calls": [],
            "raw_results": "",
            "synthesized_result": "",
            "scope_check": ""
        }
        final_state = self.agent.invoke(initial_state)

        return {
            "result": final_state["result"],
            "tool_calls": final_state.get("tool_calls", []),
            "session_id": final_state["session_id"],
            "raw_results": final_state.get("raw_results", ""),
            "synthesized_result": final_state.get("synthesized_result", ""),
            "scope_check": final_state.get("scope_check", "")
        }