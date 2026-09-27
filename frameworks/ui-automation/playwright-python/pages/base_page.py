"""Base Page Object class encapsulating common interactions, synchronization, and logging."""
from typing import Any, Optional


class BasePage:
    def __init__(self, page: Optional[Any] = None):
        self.page = page

    def navigate_to(self, url: str) -> None:
        if self.page:
            self.page.goto(url)

    def click(self, selector: str) -> None:
        if self.page:
            self.page.click(selector)

    def fill(self, selector: str, text: str) -> None:
        if self.page:
            self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        if self.page:
            return self.page.inner_text(selector)
        return ""

    def is_visible(self, selector: str) -> bool:
        if self.page:
            return self.page.is_visible(selector)
        return True
