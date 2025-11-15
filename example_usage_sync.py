# from playwright_chrome_manager.chrome_manager import BrowserManager
from playwright_browser_manager.browser_manager import BrowserManager
import time

debug_port=9221 # 9222, 9223
manager = BrowserManager(debug_port=debug_port)

# Check if profiles exist, setup/update if needed
profile_name = "my_facebook_profile"
if not manager.profile_exists(profile_name):
    print(f"Profile '{profile_name}' does not exist. Setting it up now.")
    manager.setup_profile(
        profile_name=profile_name,
        url="https://www.facebook.com",
        wait_message="Please login to Facebook, then close the browser to save your session."
    )
else:
    update = input(f"Profile '{profile_name}' exists. Do you want to update it? (y/n): ").lower().strip()
    if update in ['y', 'yes']:
        manager.setup_profile(
            profile_name=profile_name,
            url="https://www.facebook.com",
            wait_message="Please update your Facebook session, then close the browser to save."
        )

profile_name2 = "my_facebook_profile2"
if not manager.profile_exists(profile_name2):
    print(f"Profile '{profile_name2}' does not exist. Setting it up now.")
    manager.setup_profile(
        profile_name=profile_name2,
        url="https://www.facebook.com",
        wait_message="Please login to Facebook, then close the browser to save your session."
    )
else:
    update = input(f"Profile '{profile_name2}' exists. Do you want to update it? (y/n): ").lower().strip()
    if update in ['y', 'yes']:
        manager.setup_profile(
            profile_name=profile_name2,
            url="https://www.facebook.com",
            wait_message="Please update your Facebook session, then close the browser to save."
        )


# page = manager.connect_to_browser(profile_name=profile_name, url="https://www.facebook.com")
# print("Page Title:", page.title())
# input("Press Enter to close the browser...")
# page.close()
# manager.close_browser()
#
# time.sleep(3)
#
# page = manager.connect_to_browser(profile_name=profile_name, url="https://www.twitter.com")
# print("Page Title:", page.title())
# input("Press Enter to close the browser...")
# page.close()
# manager.close_browser()


with BrowserManager(debug_port=debug_port) as manager:
    page = manager.connect_to_browser(profile_name=profile_name, url="https://www.facebook.com")
    context = page.context
    search_page = context.new_page()
    print("Page Title:", search_page.title())
    input("Press Enter to close the browser...")
    search_page.close()
    manager.close_browser()

with BrowserManager(debug_port=debug_port) as manager:
    page = manager.connect_to_browser(profile_name=profile_name2, url="https://www.facebook.com")
    print("Page Title:", page.title())
    input("Press Enter to close the browser...")
    page.close()
    manager.close_browser()






