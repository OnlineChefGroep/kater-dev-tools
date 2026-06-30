from playwright.sync_api import sync_playwright, expect
import time

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Go to dashboard
        page.goto("http://localhost:9091/dashboard")

        # Wait for boot screen to disappear
        page.wait_for_selector("#boot", state="hidden", timeout=10000)

        # Verify placeholder text
        search_input = page.get_by_label("Search servers")
        expect(search_input).to_have_attribute("placeholder", "Search servers (e.g. search, github)...")
        print("Placeholder verified")

        # Take screenshot of Dashboard view
        page.screenshot(path="verification/dashboard_view.png")

        # Switch to Catalog view
        catalog_tab = page.get_by_role("tab", name="Catalog")
        catalog_tab.click()
        expect(catalog_tab).to_have_attribute("aria-selected", "true")
        expect(catalog_tab).to_have_attribute("tabindex", "0")
        print("Catalog tab verified")
        page.screenshot(path="verification/catalog_view.png")

        # Switch to Deploy view
        deploy_tab = page.get_by_role("tab", name="Deploy")
        deploy_tab.click()
        expect(deploy_tab).to_have_attribute("aria-selected", "true")
        print("Deploy tab verified")

        # Test copy button interaction
        time.sleep(2)

        # The copy button text change depends on successful clipboard write
        # In headless environment without a real clipboard, navigator.clipboard.writeText might fail
        # but the catch block in copyDeployCode uses toast instead.
        # However, I want to see if it even gets clicked.

        copy_btn = page.get_by_label("Copy deployment code")
        if copy_btn.is_visible():
            print("Copy button is visible")
            copy_btn.click()
            # Wait a bit for the async click handler to run
            time.sleep(0.5)
            page.screenshot(path="verification/deploy_after_click.png")

        browser.close()

if __name__ == "__main__":
    verify()
