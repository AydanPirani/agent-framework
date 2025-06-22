"""
Demo of the Agent framework in action.
This script shows how to use the Agent to complete web tasks.
"""
import time
from pathlib import Path
from agent_framework.agent import Agent

def demo_search_google():
    """Demo searching Google for a query."""
    query = "latest AI news"
    task = f"Search Google for '{query}' and click on the first result"
    
    with Agent(headless=False, verbose=True) as agent:
        print(f"\n{'='*50}")
        print(f"TASK: {task}")
        print(f"{'='*50}\n")
        
        result = agent.run(
            task=task,
            initial_url="https://www.google.com"
        )
        
        print("\nTask completed!")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Steps taken: {result['steps']}")

def demo_impossible_task():
    """Demo handling an impossible task."""
    task = "Order a pizza using this website"  # This will likely be marked as impossible
    
    with Agent(headless=True, verbose=True) as agent:
        print(f"\n{'='*50}")
        print(f"TASK: {task}")
        print(f"{'='*50}\n")
        
        result = agent.run(
            task=task,
            initial_url="https://www.example.com"
        )
        
        print("\nTask completed!")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Steps taken: {result['steps']}")

if __name__ == "__main__":
    print("Agent Framework Demo")
    print("1. Search Google")
    print("2. Impossible Task")
    
    choice = input("\nSelect a demo (1-2): ")
    
    if choice == "1":
        demo_search_google()
    elif choice == "2":
        demo_impossible_task()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")
