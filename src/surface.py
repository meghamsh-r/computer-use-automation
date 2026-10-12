from playwright.sync_api import sync_playwright


class BrowserSurface:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

    def navigate(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def type_by_label(self, label: str, value: str):
        self.page.get_by_label(label).fill(value)

    def click_by_role(self, role: str, name: str):
        self.page.get_by_role(role, name=name).click()
        self.page.wait_for_load_state("networkidle")

    def read_css(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)

    def close(self):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()