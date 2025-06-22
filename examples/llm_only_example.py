"""
Example demonstrating standalone usage of the LLM client without browser automation.
This shows how to interact with the LLM directly for general purpose tasks.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agent_framework.llm import LLMClient

def print_action_result(response: dict):
    """Helper function to print the LLM response in a readable format."""
    print("\n" + "="*50)
    print("LLM RESPONSE:")
    print("-"*50)
    print(json.dumps(response, indent=2))
    print("="*50 + "\n")

def example_text_only():
    """Example using only text input."""
    print("\n=== Example 1: Text-only Input ===")
    llm = LLMClient()
    
    prompt = """
    I need to plan a birthday party. Please suggest a theme, location, 
    and three activities that would be fun for a group of 10-year-olds.
    """
    
    print(f"Sending prompt: {prompt.strip()}")
    response = llm.get_next_action(prompt=prompt)
    print_action_result(response)

def example_with_html_context():
    """Example using HTML context."""
    print("\n=== Example 2: HTML Context ===")
    llm = LLMClient()
    
    prompt = "Extract the product name, price, and description from this HTML."
    
    # Example HTML (in a real scenario, this would be scraped from a webpage)
    html_content = """
    <div class="product">
        <h1 class="product-title">Super Widget 3000</h1>
        <div class="price">$49.99</div>
        <p class="description">The best widget on the market with advanced features.</p>
        <button class="add-to-cart">Add to Cart</button>
    </div>
    """
    
    print(f"Sending prompt: {prompt}")
    response = llm.get_next_action(
        prompt=prompt,
        html=html_content
    )
    print_action_result(response)

def example_with_image():
    """Example using image input."""
    print("\n=== Example 3: Image Analysis ===")
    llm = LLMClient()
    
    # Note: In a real scenario, you would provide a path to an image file
    # For this example, we'll skip the actual API call to avoid errors
    try:
        image_path = "path/to/your/image.jpg"
        if not os.path.exists(image_path):
            print(f"Image not found at {image_path}. Please update the path to a real image.")
            return
            
        prompt = "Describe this image in detail."
        print(f"Sending image analysis request: {prompt}")
        
        # Uncomment this line to actually make the API call
        # response = llm.get_next_action(prompt=prompt, image=image_path)
        # print_action_result(response)
        
        print("Skipping actual API call to save resources. Uncomment the code to run with a real image.")
        
    except Exception as e:
        print(f"Error in image analysis example: {e}")

def example_decision_making():
    """Example showing decision making capabilities."""
    print("\n=== Example 4: Decision Making ===")
    llm = LLMClient()
    
    prompt = """
    I need to decide whether to invest in Company X. 
    Here are the details:
    - Current stock price: $150
    - 1-year target: $180
    - P/E ratio: 25
    - Industry average P/E: 20
    
    Should I invest? Please provide reasoning.
    """
    
    print("Requesting investment advice...")
    response = llm.get_next_action(prompt=prompt)
    print_action_result(response)

def main():
    """Run all example scenarios."""
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not found in .env file")
        print("Please add your OpenRouter API key to the .env file")
        return
    
    try:
        example_text_only()
        example_with_html_context()
        example_with_image()
        example_decision_making()
        
        print("\nAll examples completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have set up your .env file with a valid OpenRouter API key.")

if __name__ == "__main__":
    main()
