"""
Basic usage example for the BrowserAgent.
"""
import time
from agent_framework.browser_agent import BrowserAgent

def main():
    # Create a new browser agent
    with BrowserAgent(headless=False) as agent:
        # Navigate to a website
        print("Navigating to example.com...")
        agent.get("https://example.com")
        
        # Keep the browser open for a few seconds to see the result
        print("Browser will close in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    main()
