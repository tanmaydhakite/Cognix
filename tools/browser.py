from playwright.sync_api import sync_playwright


class BrowserTool:

    def open_url(self, url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                result = {
                    "success": True,
                    "url": page.url,
                    "title": page.title()
                }

                browser.close()

                return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def click(self, url, selector):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                page.click(selector)

                result = {
                    "success": True,
                    "url": page.url,
                    "title": page.title()
                }

                browser.close()

                return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def extract_text(self, url, selector="body"):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                text = page.locator(selector).inner_text()

                browser.close()

                # Clean webpage formatting
                lines = []

                for line in text.splitlines():
                    line = line.strip()

                    if not line:
                        continue

                    # Remove markdown headings
                    while line.startswith("#"):
                        line = line[1:].strip()

                    # Remove simple table separators
                    line = line.replace("|", " ")

                    if line:
                        lines.append(line)

                clean_text = "\n".join(lines)

                return {
                    "success": True,
                    "text": clean_text
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
    def type_text(self, url, selector, text):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
    
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )
    
                page.fill(selector, text)
    
                result = {
                    "success": True,
                    "url": page.url,
                    "title": page.title(),
                    "message": "Text entered successfully."
                }
    
                browser.close()
    
                return result
    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }