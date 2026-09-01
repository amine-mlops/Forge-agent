from playwright.sync_api import sync_playwright
from langchain.tools import tool

playwright = sync_playwright().start()

browser = playwright.chromium.launch(
    headless=False
)
page = browser.new_page()

@tool
def browser_open(url: str) -> str:
    """Open a URL in a browser and return its title."""

    try:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=False
            )

            page = browser.new_page()

            page.goto(url)

            title = page.title()

            browser.close()

            return f"Opened: {url}\nTitle: {title}"

    except Exception as e:
        return f"Browser error: {e}"

@tool
def browser_read() -> str:
    """Read the visible text of the current webpage."""

    try:
        text = page.locator("body").inner_text()

        if len(text) > 12000:
            text = text[:12000] + "\n...[truncated]"

        return text

    except Exception as e:
        return f"Browser error:{e}"

@tool
def browser_click(text: str) -> str:
    """Click an element containing the specified text."""

    try:
        page.get_by_text(
            text,
            exact=False
        ).first.click()

        return f"Click: {text}"

    except Exception as e:
        return f"Click error: {e}"

@tool
def browser_type(selector: str, text: str) -> str:
    """Fill an input using a CSS selector."""

    try:
        page.localor(selector).fill(text)

        return f"Filled: {selector}"

    except Exception as e:
        return f"Type error: {e}"

@tool
def browser_screenshot(filename: str) -> str:
    """Save a screenshot inside agent_workspace."""

    try:
        file_path = safe_path(filename)

        page.screenshot(
            path=str(file_path),
            full_page=True
        )

        return (
            f"Screenshot saved: "
            f"{file_path.relative_to(WORKSPACE)}"
        )
    except Exception as e:
        return f"Screenshot error: {e}"





    
