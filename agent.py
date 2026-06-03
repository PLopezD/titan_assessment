#!/usr/bin/env python3
"""
Minimal Research Agent Framework
A simple CLI wrapper for LangGraph research agents
"""

import click
from agents.ResearchAgent import ResearchAgent
from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.argument('query', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(query: str, verbose: bool):
    """Research Agent CLI - Execute research queries using LangGraph"""

    if verbose:
        click.echo(f"Executing research query: {query}")

    agent = ResearchAgent()
    response = agent.research(query)

    click.echo("\n--- Research Result ---")
    click.echo(response["result"])
    if response["tool_calls"]:
        click.echo("\n--- Tools Used ---")
        for tool_call in response["tool_calls"]:
            click.echo(f"  - {tool_call}")


    if verbose:
        if response["tool_calls"]:
            click.echo("\n--- Tools Used ---")
            for tool_call in response["tool_calls"]:
                click.echo(f"  - {tool_call}")

        if response.get("raw_results"):
            click.echo("\n--- Raw Research Data ---")
            click.echo(response["raw_results"])

        click.echo(f"\nSession ID: {response['session_id']}")

if __name__ == "__main__":
    main()