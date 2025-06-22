"""
Browser Agent - A Selenium-based web automation agent.
"""
import time
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

class BrowserAgent:
    """A Selenium-based web automation agent with support for various actions."""
    
    def __init__(self, headless: bool = False, implicit_wait: int = 10):
        """
        Initialize the BrowserAgent.
        
        Args:
            headless: If True, run the browser in headless mode
            implicit_wait: Default wait time in seconds for element operations
        """
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--disable-gpu")
        
        # Add common options for better stability
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Set up Chrome with automatic driver management
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.implicitly_wait(implicit_wait)
        self.wait = WebDriverWait(self.driver, implicit_wait)
    
    # Core browser actions
    def navigate(self, url: str) -> None:
        """Navigate to the specified URL."""
        self.driver.get(url)
    
    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """Get the current page title."""
        return self.driver.title
    
    # Element interaction methods
    def find_element(self, selector: str, timeout: Optional[float] = None) -> WebElement:
        """
        Find a single web element using a CSS selector.
        
        Args:
            selector: CSS selector for the element
            timeout: Optional timeout in seconds (overrides default wait)
            
        Returns:
            WebElement: The found web element
            
        Raises:
            NoSuchElementException: If the element is not found
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    
    def click(self, selector: str, timeout: Optional[float] = None) -> None:
        """
        Click on an element.
        
        Args:
            selector: CSS selector for the element to click
            timeout: Optional timeout in seconds
            
        Raises:
            NoSuchElementException: If the element is not found or not clickable
        """
        element = self.find_element(selector, timeout)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click()
    
    def type_text(self, selector: str, text: str, timeout: Optional[float] = None, press_enter: bool = False) -> None:
        """
        Type text into an input field.
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            timeout: Optional timeout in seconds
        """
        print("Finding element: ", selector)
        element = self.find_element(selector, timeout)
        print("Clearing element: ", selector)
        element.clear()
        print("Typing text into", selector)
        element.send_keys(text)
        print("Typed text into ", selector)
        # if press_enter:
        #     self.press_enter()

    
    def get_text(self, selector: str, timeout: Optional[float] = None) -> str:
        """
        Get text from an element.
        
        Args:
            selector: CSS selector for the element
            timeout: Optional timeout in seconds
            
        Returns:
            str: The text content of the element
        """
        element = self.find_element(selector, timeout)
        return element.text
    
    def get_attribute(self, selector: str, attribute: str, timeout: Optional[float] = None) -> Optional[str]:
        """
        Get an attribute value from an element.
        
        Args:
            selector: CSS selector for the element
            attribute: Name of the attribute to get
            timeout: Optional timeout in seconds
            
        Returns:
            The attribute value, or None if not found
        """
        try:
            element = self.find_element(selector, timeout)
            return element.get_attribute(attribute)
        except (NoSuchElementException, TimeoutException):
            return None
    
    # Page actions
    def scroll(self, direction: str = "down", amount: int = 300) -> None:
        """
        Scroll the page in the specified direction.
        
        Args:
            direction: Direction to scroll ('up', 'down', 'left', 'right')
            amount: Number of pixels to scroll (default: 300)
        """
        direction = direction.lower()
        if direction == "down":
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
        elif direction == "up":
            self.driver.execute_script(f"window.scrollBy(0, -{amount});")
        elif direction == "right":
            self.driver.execute_script(f"window.scrollBy({amount}, 0);")
        elif direction == "left":
            self.driver.execute_script(f"window.scrollBy(-{amount}, 0);")
    
    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_to_top(self) -> None:
        """Scroll to the top of the page."""
        self.driver.execute_script("window.scrollTo(0, 0);")
    
    def wait_for_element(self, selector: str, timeout: float = 10) -> bool:
        """
        Wait for an element to be present on the page.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if element is found, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def wait_until_visible(self, selector: str, timeout: float = 10) -> bool:
        """
        Wait for an element to be visible on the page.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if element becomes visible, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            return False
    
    # Page information
    def get_page_source(self) -> str:
        """Get the current page source."""
        return self.driver.page_source
    
    def take_screenshot(self, path: Optional[str] = None) -> bytes:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Optional path to save the screenshot
            
        Returns:
            bytes: The screenshot as PNG data
        """
        screenshot = self.driver.get_screenshot_as_png()
        if path:
            with open(path, 'wb') as f:
                f.write(screenshot)
        return screenshot
    
    # Browser control
    def back(self) -> None:
        """Go back to the previous page."""
        self.driver.back()
    
    def forward(self) -> None:
        """Go forward to the next page in browser history."""
        self.driver.forward()
    
    def refresh(self) -> None:
        """Refresh the current page."""
        self.driver.refresh()
    
    def close_tab(self) -> None:
        """Close the current tab/window."""
        self.driver.close()
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        try:
            if self.service:
                self.service.stop()
        except Exception:
            pass
    
    def __enter__(self):
        """Enable use as a context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are cleaned up when used as a context manager."""
        self.close()
    
    # Action execution
    def execute_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a browser action based on the action type.
        
        Args:
            action_type: Type of action to execute
            **kwargs: Parameters for the action
            
        Returns:
            Dict containing the result and any relevant data
        """
        result = {"success": False, "message": "", "data": None}
        
        try:
            if action_type == "navigate":
                self.navigate(kwargs["url"])
                result.update({
                    "success": True,
                    "message": f"Navigated to {kwargs['url']}",
                    "data": {"url": self.get_current_url(), "title": self.get_page_title()}
                })
                
            elif action_type == "click":
                selector = kwargs["selector"]
                self.click(selector)
                result.update({
                    "success": True,
                    "message": f"Clicked element: {selector}",
                    "data": {"selector": selector}
                })
                
            elif action_type == "type":
                self.type_text(kwargs["selector"], kwargs["text"], press_enter=kwargs.get("press_enter", False))
                result.update({
                    "success": True,
                    "message": f"Typed text into {kwargs['selector']}",
                    "data": {"selector": kwargs["selector"], "text_length": len(kwargs["text"])}
                })
                
            elif action_type == "scroll":
                direction = kwargs.get("direction", "down")
                amount = kwargs.get("amount", 300)
                self.scroll(direction, amount)
                result.update({
                    "success": True,
                    "message": f"Scrolled {direction} by {amount}px",
                    "data": {"direction": direction, "amount": amount}
                })
                
            elif action_type == "wait":
                seconds = kwargs.get("seconds", 1)
                time.sleep(seconds)
                result.update({
                    "success": True,
                    "message": f"Waited for {seconds} seconds",
                    "data": {"seconds": seconds}
                })
                
            elif action_type == "extract":
                selector = kwargs["selector"]
                attribute = kwargs.get("attribute")
                
                if attribute:
                    value = self.get_attribute(selector, attribute)
                else:
                    value = self.get_text(selector)
                
                result.update({
                    "success": value is not None,
                    "message": f"Extracted {'attribute ' + attribute if attribute else 'text'} from {selector}",
                    "data": {"value": value, "selector": selector, "attribute": attribute}
                })
                
            else:
                result["message"] = f"Unknown action type: {action_type}"
                
        except Exception as e:
            print(e)
            result["message"] = f"Error executing {action_type}: {str(e)}"
            
        return result
