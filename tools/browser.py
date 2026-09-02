from pathlib import Path

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    Page,
)

from langchain.tools import tool

# WORKSPACE

WORKSPACE = Path("agent_workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# BROWSER MANAGER

class BrowserManager:
    """
    Manages one persistent Playwright browser and page.
    """

    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    async def start(self):
        """Start Playwright and the browser."""

        if self.page is not None:
            return self.page

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            executable_path="/usr/bin/brave",
            headless=False
        )

        self.page = await self.browser.new_page()

        return self.page

    async def get_page(self):
        """Return the persistent page."""

        if self.page is None:
            return await self.start()

        return self.page

    async def close(self):
        """Close browser and Playwright."""

        if self.browser is not None:
            await self.browser.close()

        if self.playwright is not None:
            await self.playwright.stop()

        self.page = None
        self.browser = None
        self.playwright = None

# GLOBAL BROWSER MANAGER

browser_manager = BrowserManager()

# OPEN PAGE


@tool
async def browser_open(url: str) -> str:
    """
    Open a URL in the persistent browser.
    """

    try:
        page = await browser_manager.get_page()

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000,
        )

        title = await page.title()

        return (
            f"Opened: {url}\n"
            f"Title: {title}"
        )

    except Exception as e:
        return f"Browser open error: {e}"


# READ PAGE


@tool
async def browser_read() -> str:
    """
    Read visible text from the current webpage.
    """

    try:
        page = await browser_manager.get_page()

        text = await page.locator("body").inner_text()

        if len(text) > 12000:
            text = text[:12000] + "\n...[truncated]"

        return text

    except Exception as e:
        return f"Browser read error: {e}"


# CLICK


@tool
async def browser_click(text: str) -> str:
    """
    Click the first element containing the specified text.
    """

    try:
        page = await browser_manager.get_page()

        element = page.get_by_text(
            text,
            exact=False
        ).first

        await element.click()

        return f"Clicked: {text}"

    except Exception as e:
        return f"Browser click error: {e}"

# TYPE

@tool
async def browser_type(selector: str, text: str) -> str:
    """
    Fill an input using a CSS selector.
    """

    try:
        page = await browser_manager.get_page()

        await page.locator(selector).fill(text)

        return f"Filled: {selector}"

    except Exception as e:
        return f"Browser type error: {e}"

# SCREENSHOT

@tool
async def browser_screenshot(filename: str) -> str:
    """
    Save a full-page screenshot inside agent_workspace.
    """

    try:
        page = await browser_manager.get_page()

        # Prevent path traversal
        filename = Path(filename).name

        file_path = WORKSPACE / filename

        await page.screenshot(
            path=str(file_path),
            full_page=True,
        )

        return f"Screenshot saved: {file_path}"

    except Exception as e:
        return f"Browser screenshot error: {e}"





    
