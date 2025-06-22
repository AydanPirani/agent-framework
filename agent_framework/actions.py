"""Define possible actions that the agent can take."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Literal

@dataclass
class Action:
    """Base class for all agent actions."""
    action_type: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary."""
        return {
            "action_type": self.action_type,
            "parameters": self.parameters
        }

# Specific action types
@dataclass
class NavigateAction(Action):
    """Navigate to a URL."""
    def __init__(self, url: str):
        super().__init__(
            action_type="navigate",
            parameters={"url": url}
        )

@dataclass
class ClickAction(Action):
    """Click on an element."""
    def __init__(self, selector: str):
        super().__init__(
            action_type="click",
            parameters={"selector": selector}
        )

@dataclass
class TypeAction(Action):
    """Type text into an element."""
    def __init__(self, selector: str, text: str):
        super().__init__(
            action_type="type",
            parameters={"selector": selector, "text": text}
        )

@dataclass
class ScrollAction(Action):
    """Scroll the page."""
    def __init__(self, direction: Literal["up", "down", "left", "right"], amount: int = 300):
        super().__init__(
            action_type="scroll",
            parameters={"direction": direction, "amount": amount}
        )

@dataclass
class WaitAction(Action):
    """Wait for a specified time."""
    def __init__(self, seconds: float):
        super().__init__(
            action_type="wait",
            parameters={"seconds": seconds}
        )

@dataclass
class ExtractAction(Action):
    """Extract information from the page."""
    def __init__(self, selector: str, attribute: Optional[str] = None):
        super().__init__(
            action_type="extract",
            parameters={"selector": selector, "attribute": attribute}
        )

@dataclass
class DoneAction(Action):
    """Indicate that the task is complete."""
    def __init__(self, result: str = "Task completed successfully"):
        super().__init__(
            action_type="done",
            parameters={"result": result}
        )

# List of all possible action types
ALL_ACTION_TYPES = [
    "navigate",
    "click",
    "type",
    "scroll",
    "wait",
    "extract",
    "done"
]
