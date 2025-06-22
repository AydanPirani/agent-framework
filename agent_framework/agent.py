"""
Agent module that coordinates between the LLM and browser to execute tasks.
"""
import json
import time
import base64
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .browser_agent import BrowserAgent
from .llm import LLMClient
from .actions import (
    Action, NavigateAction, ClickAction, TypeAction,
    ScrollAction, WaitAction, ExtractAction, DoneAction, ImpossibleAction
)
from .config import MODEL_NAME, MODEL_TEMPERATURE, SCREENSHOT_DIR

class Agent:
    """
    An autonomous agent that can execute tasks in a web browser using LLM guidance.
    """
    
    def __init__(
        self,
        headless: bool = False,
        model: str = MODEL_NAME,
        temperature: float = MODEL_TEMPERATURE,
        max_steps: int = 20,
        verbose: bool = True
    ):
        """
        Initialize the agent.
        
        Args:
            headless: Whether to run the browser in headless mode
            model: The LLM model to use
            temperature: Sampling temperature for the LLM
            max_steps: Maximum number of steps to execute before stopping
            verbose: Whether to print detailed execution information
        """
        self.browser = BrowserAgent(headless=headless)
        self.llm = LLMClient(model=model, temperature=temperature)
        self.max_steps = max_steps
        self.verbose = verbose
        self.history: List[Dict[str, Any]] = []
    
    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level.upper()}] {message}")
    
    def get_page_context(self) -> Dict[str, Any]:
        """
        Get the current page context including URL, title, and a screenshot.
        
        Returns:
            Dict containing page context with screenshot as base64-encoded string
        """
        context = {
            "url": "unknown",
            "title": "Unknown",
            "screenshot": None,
            "screenshot_format": None,
            "html": None,
            "timestamp": time.localtime()
        }
        
        try:
            # Get basic page info
            context["url"] = self.browser.get_current_url()
            context["title"] = self.browser.get_page_title()
            context["html"] = self.browser.get_page_source()
            
            # Take a screenshot and encode it as base64
            try:
                screenshot = self.browser.take_screenshot()

                # save screenshot to local directory
                if screenshot:
                    ts_str = time.strftime("%Y%m%d_%H%M%S", context['timestamp'])
                    if isinstance(screenshot, bytes):
                        with open(f"{SCREENSHOT_DIR}/screenshot_{ts_str}.png", "wb") as f:
                            f.write(screenshot)
                    elif isinstance(screenshot, str):
                        with open(f"{SCREENSHOT_DIR}/screenshot_{ts_str}.png", "w") as f:
                            f.write(screenshot)

                if screenshot:
                    if isinstance(screenshot, bytes):
                        context["screenshot"] = base64.b64encode(screenshot).decode('utf-8')
                        context["screenshot_format"] = "base64_png"
                    elif isinstance(screenshot, str):
                        # If it's already a string, assume it's base64
                        context["screenshot"] = screenshot
                        context["screenshot_format"] = "base64_png"
            except Exception as e:
                self.log(f"Warning: Could not take screenshot: {str(e)}", "warning")
                
        except Exception as e:
            self.log(f"Error getting page context: {str(e)}", "error")
            context["error"] = str(e)
            
        return context
    
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """
        Execute a single action using the browser agent.
        
        Args:
            action: The action to execute
            
        Returns:
            Dict containing the result of the action
        """
        action_type = action.action_type
        params = action.parameters
        
        self.log(f"Executing action: {action_type} with params: {params}")
        
        # Execute the action using the browser agent
        result = self.browser.execute_action(action_type, **params)
        
        # Add to history
        self.history.append({
            "step": len(self.history) + 1,
            "action": action.to_dict(),
            "result": result,
            "timestamp": time.time(),
            "context": self.get_page_context()
        })
        
        self.log(f"Action result: {result['success']} - {result['message']}")
        return result
    
    def run(self, task: str, initial_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent to complete a given task.
        
        Args:
            task: The task to complete
            initial_url: Optional URL to start from
            
        Returns:
            Dict containing the final result and execution history
        """
        self.log(f"Starting task: {task}")
        
        if initial_url:
            self.execute_action(NavigateAction(initial_url))
        
        for step in range(1, self.max_steps + 1):
            self.log(f"\n--- Step {step}/{self.max_steps} ---")
            
            # Get the current page context
            context = self.get_page_context()
            
            # Get the next action from the LLM
            prompt = f"""
            Task: {task}
            
            Current page: {context.get('title', 'Unknown')}
            URL: {context.get('url', 'Unknown')}

            Previous Action: {self.history[-1].get('action', {})}
            Previous Result: {self.history[-1].get('result', {})}
            
            What should I do next to complete the task?
            """
            
            try:
                # Get the current page context including screenshot
                context = self.get_page_context()
                
                # Get the next action from the LLM with full context
                print("Before LLM step")
                response = self.llm.get_next_action(
                    prompt=prompt,
                    html=context.get("html"),
                    image=context.get("screenshot")  # Pass the base64-encoded screenshot
                )
                print("After LLM step")
                
                action_data = response.get("action", {})
                action_type = action_data.get("action_type")
                action_params = action_data.get("parameters", {})
                
                self.log(f"LLM chose action: {action_type}")
                self.log(f"Reasoning: {response.get('reasoning', 'No reasoning provided')}")
                
                # Map action type to the appropriate action class
                action_classes = {
                    "navigate": NavigateAction,
                    "click": ClickAction,
                    "type": TypeAction,
                    "scroll": ScrollAction,
                    "wait": WaitAction,
                    "extract": ExtractAction,
                    "done": DoneAction,
                    "impossible": ImpossibleAction
                }
                
                if action_type not in action_classes:
                    self.log(f"Unknown action type: {action_type}", "error")
                    continue
                
                # Create and execute the action
                action_class = action_classes[action_type]
                action = action_class(**action_params)
                result = self.execute_action(action)
                
                # Check if we're done
                if action_type in ["done", "impossible"]:
                    self.log(f"Task completed: {action_params.get('result', 'No result')}")
                    return {
                        "success": action_type == "done",
                        "message": action_params.get("result", ""),
                        "steps": step,
                        "history": self.history
                    }
                
            except Exception as e:
                self.log(f"Error in step {step}: {str(e)}", "error")
                # If we encounter multiple errors in a row, give up
                if len(self.history) > 0 and not self.history[-1].get("result", {}).get("success", False):
                    self.log("Multiple errors in a row, giving up", "error")
                    return {
                        "success": False,
                        "message": f"Agent failed after {step} steps: {str(e)}",
                        "steps": step,
                        "history": self.history
                    }
        
        # If we've reached max steps without completing
        return {
            "success": False,
            "message": f"Reached maximum number of steps ({self.max_steps}) without completing the task",
            "steps": self.max_steps,
            "history": self.history
        }
    
    def __enter__(self):
        """Enable use as a context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are cleaned up when used as a context manager."""
        self.browser.close()
        self.log("Browser closed")
