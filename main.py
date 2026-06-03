#!/usr/bin/env python3
"""
Minimal Research Agent Framework
A simple CLI wrapper for LangGraph research agents
"""

import click
from agents.ResearchAgent import ResearchAgent


@click.command()
@click.argument('query', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(query: str, verbose: bool):
    """Research Agent CLI - Execute research queries using LangGraph"""

    if verbose:
        click.echo(f"Executing research query: {query}")

    agent = ResearchAgent()
    result = agent.research(query)

    click.echo("\n--- Research Result ---")
    click.echo(result)

if __name__ == "__main__":
    main()