# example_proxy_uses.py
from playwright_browser_manager.browser_manager import BrowserManager

with BrowserManager(debug_port=9225) as bm:
    page = bm.connect_to_browser_with_proxy(
        profile_name="france_profile",
        proxy={
            "server": "http://gw.dataimpulse.com:823",
            "username": "xxx5505791abd0cd522901c__crxxx.fr",   # ← France
            "password": "xxxf5d3919c504d8fc9xxx"
        },
        url="https://iphey.com",
        headless=False
    )

    page.wait_for_timeout(5000)
    page.screenshot(path="france_proof.png", full_page=True)
    print("You are in France! Check the screenshot.")
    input("Press Enter to exit...")