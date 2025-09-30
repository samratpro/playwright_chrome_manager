from chrome_manager import ChromeManager
import time


manager = ChromeManager()

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


with ChromeManager() as manager:
    page = manager.connect_to_browser(profile_name=profile_name, url="https://www.facebook.com")
    print("Page Title:", page.title())
    input("Press Enter to close the browser...")
    page.close()
    manager.close_browser()

with ChromeManager() as manager:
    page = manager.connect_to_browser(profile_name=profile_name2, url="https://www.facebook.com")
    print("Page Title:", page.title())
    input("Press Enter to close the browser...")
    page.close()
    manager.close_browser()

