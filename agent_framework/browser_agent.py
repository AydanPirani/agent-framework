"""
Browser Agent - A Selenium-based web automation agent.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class BrowserAgent:
    """A Selenium-based web automation agent."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the BrowserAgent.
        
        Args:
            headless: If True, run the browser in headless mode
        """
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--disable-gpu")
        
        # Set up Chrome with automatic driver management
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
    
    def get(self, url: str):
        """Navigate to the specified URL."""
        self.driver.get(url)
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
        if self.service:
            self.service.stop()
    
    def __enter__(self):
        """Enable use as a context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are cleaned up when used as a context manager."""
        self.close()
