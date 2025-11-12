"""
Async Chrome Manager Use Cases - Multiple Tabs/Pages
"""
import asyncio
from chrome_manager import ChromeManager
from playwright.async_api import async_playwright

# ============================================================================
# USE CASE 1: Multiple tabs with same profile (parallel data collection)
# ============================================================================
async def use_case_1_multiple_tabs_same_profile():
    """
    Open multiple tabs in the same profile and perform parallel operations.
    Example: Scraping multiple Facebook pages simultaneously.
    """
    debug_port = 9221
    profile_name = "my_facebook_profile"
    
    manager = ChromeManager(debug_port=debug_port)
    
    try:
        # Connect to browser with the profile
        page = await manager.connect_to_browser_async(
            profile_name=profile_name, 
            url="https://www.facebook.com"
        )
        
        context = page.context
        
        # Create multiple new pages (tabs)
        page1 = await context.new_page()
        page2 = await context.new_page()
        page3 = await context.new_page()
        
        # Navigate to different URLs in parallel
        urls = [
            "https://www.facebook.com/marketplace",
            "https://www.facebook.com/groups",
            "https://www.facebook.com/watch"
        ]
        
        # Parallel navigation
        await asyncio.gather(
            page1.goto(urls[0], timeout=30000),
            page2.goto(urls[1], timeout=30000),
            page3.goto(urls[2], timeout=30000)
        )
        
        print(f"Page 1 Title: {await page1.title()}")
        print(f"Page 2 Title: {await page2.title()}")
        print(f"Page 3 Title: {await page3.title()}")
        
        # Perform actions on each page in parallel
        async def scrape_page(pg, name):
            await pg.wait_for_load_state('networkidle')
            content = await pg.content()
            print(f"{name} content length: {len(content)}")
            return content
        
        results = await asyncio.gather(
            scrape_page(page1, "Marketplace"),
            scrape_page(page2, "Groups"),
            scrape_page(page3, "Watch")
        )
        
        # Close pages
        await page1.close()
        await page2.close()
        await page3.close()
        
    finally:
        await manager.close_browser_async()


# ============================================================================
# USE CASE 2: Multiple profiles with multiple tabs (different accounts)
# ============================================================================
async def use_case_2_multiple_profiles_multiple_tabs():
    """
    Open multiple browser instances with different profiles, 
    each with multiple tabs. Example: Managing multiple Facebook accounts.
    """
    
    async def manage_profile(profile_name, debug_port, urls):
        """Manage a single profile with multiple tabs"""
        manager = ChromeManager(debug_port=debug_port)
        
        try:
            # Connect to browser
            page = await manager.connect_to_browser_async(
                profile_name=profile_name,
                url=urls[0]
            )
            
            context = page.context
            pages = [page]  # First page already open
            
            # Open additional tabs for remaining URLs
            for url in urls[1:]:
                new_page = await context.new_page()
                await new_page.goto(url, timeout=30000)
                pages.append(new_page)
            
            # Get titles from all pages
            titles = await asyncio.gather(*[p.title() for p in pages])
            
            print(f"\n{profile_name} - Tabs opened:")
            for i, title in enumerate(titles):
                print(f"  Tab {i+1}: {title}")
            
            # Simulate some work
            await asyncio.sleep(2)
            
            # Close all pages
            for p in pages:
                await p.close()
                
            return f"{profile_name} completed"
            
        finally:
            await manager.close_browser_async()
    
    # Define profiles and their URLs
    profiles_config = [
        {
            "profile": "my_facebook_profile",
            "port": 9221,
            "urls": [
                "https://www.facebook.com",
                "https://www.facebook.com/marketplace",
                "https://www.facebook.com/groups"
            ]
        },
        {
            "profile": "my_facebook_profile2",
            "port": 9222,
            "urls": [
                "https://www.facebook.com",
                "https://www.facebook.com/watch",
                "https://www.facebook.com/gaming"
            ]
        }
    ]
    
    # Run all profiles in parallel
    tasks = [
        manage_profile(config["profile"], config["port"], config["urls"])
        for config in profiles_config
    ]
    
    results = await asyncio.gather(*tasks)
    print("\nAll profiles completed:", results)


# ============================================================================
# USE CASE 3: Sequential tab processing with context switching
# ============================================================================
async def use_case_3_sequential_tab_processing():
    """
    Open multiple tabs and process them sequentially with data passing.
    Example: Multi-step workflow across different pages.
    """
    debug_port = 9221
    profile_name = "my_facebook_profile"
    
    manager = ChromeManager(debug_port=debug_port)
    
    try:
        page = await manager.connect_to_browser_async(
            profile_name=profile_name,
            url="https://www.facebook.com"
        )
        
        context = page.context
        
        # Step 1: Search for something
        search_page = await context.new_page()
        await search_page.goto("https://www.facebook.com/search/top/?q=python")
        await search_page.wait_for_load_state('networkidle')
        print(f"Search page loaded: {await search_page.title()}")
        
        # Step 2: Navigate to a group
        group_page = await context.new_page()
        await group_page.goto("https://www.facebook.com/groups")
        await group_page.wait_for_load_state('networkidle')
        print(f"Groups page loaded: {await group_page.title()}")
        
        # Step 3: Check notifications
        notif_page = await context.new_page()
        await notif_page.goto("https://www.facebook.com/notifications")
        await notif_page.wait_for_load_state('networkidle')
        print(f"Notifications page loaded: {await notif_page.title()}")
        
        # Close pages in reverse order
        await notif_page.close()
        await group_page.close()
        await search_page.close()
        
    finally:
        await manager.close_browser_async()


# ============================================================================
# USE CASE 4: Dynamic tab management (open/close as needed)
# ============================================================================
async def use_case_4_dynamic_tab_management():
    """
    Dynamically open and close tabs based on conditions.
    Example: Opening product pages from a list.
    """
    debug_port = 9221
    profile_name = "my_facebook_profile"
    
    manager = ChromeManager(debug_port=debug_port)
    
    try:
        page = await manager.connect_to_browser_async(
            profile_name=profile_name,
            url="https://www.facebook.com/marketplace"
        )
        
        context = page.context
        
        # Simulate a list of items to check
        items_to_check = [
            "https://www.facebook.com/marketplace/item/1",
            "https://www.facebook.com/marketplace/item/2",
            "https://www.facebook.com/marketplace/item/3",
            "https://www.facebook.com/marketplace/item/4",
            "https://www.facebook.com/marketplace/item/5"
        ]
        
        # Process items in batches (max 3 tabs at a time)
        batch_size = 3
        for i in range(0, len(items_to_check), batch_size):
            batch = items_to_check[i:i + batch_size]
            
            # Open tabs for this batch
            tabs = []
            for url in batch:
                tab = await context.new_page()
                tabs.append(tab)
                try:
                    await tab.goto(url, timeout=10000)
                    print(f"Opened: {url}")
                except Exception as e:
                    print(f"Failed to open {url}: {e}")
            
            # Process each tab
            for j, tab in enumerate(tabs):
                try:
                    title = await tab.title()
                    print(f"  Tab {j+1} title: {title}")
                    # Simulate some processing
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"  Error processing tab {j+1}: {e}")
            
            # Close all tabs in this batch
            for tab in tabs:
                await tab.close()
            
            print(f"Batch {i//batch_size + 1} completed\n")
        
    finally:
        await manager.close_browser_async()


# ============================================================================
# USE CASE 5: Real-world example - Multi-account posting
# ============================================================================
async def use_case_5_multi_account_posting():
    """
    Post content to multiple accounts simultaneously.
    Each account opens multiple tabs for different groups/pages.
    """
    
    async def post_to_account(profile_name, debug_port, post_targets):
        """Post to multiple targets in one account"""
        manager = ChromeManager(debug_port=debug_port)
        
        try:
            page = await manager.connect_to_browser_async(
                profile_name=profile_name,
                url="https://www.facebook.com"
            )
            
            context = page.context
            results = []
            
            for target in post_targets:
                tab = await context.new_page()
                try:
                    await tab.goto(target["url"], timeout=30000)
                    await tab.wait_for_load_state('networkidle')
                    
                    # Simulate posting (you'd add actual posting logic here)
                    print(f"[{profile_name}] Posted to: {target['name']}")
                    results.append(f"✓ {target['name']}")
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"[{profile_name}] Failed to post to {target['name']}: {e}")
                    results.append(f"✗ {target['name']}")
                finally:
                    await tab.close()
            
            return {profile_name: results}
            
        finally:
            await manager.close_browser_async()
    
    # Define posting targets for each account
    accounts = [
        {
            "profile": "my_facebook_profile",
            "port": 9221,
            "targets": [
                {"name": "Group A", "url": "https://www.facebook.com/groups/123"},
                {"name": "Group B", "url": "https://www.facebook.com/groups/456"},
                {"name": "Page X", "url": "https://www.facebook.com/page/xyz"}
            ]
        },
        {
            "profile": "my_facebook_profile2",
            "port": 9222,
            "targets": [
                {"name": "Group C", "url": "https://www.facebook.com/groups/789"},
                {"name": "Group D", "url": "https://www.facebook.com/groups/101"},
                {"name": "Page Y", "url": "https://www.facebook.com/page/abc"}
            ]
        }
    ]
    
    # Post to all accounts in parallel
    tasks = [
        post_to_account(acc["profile"], acc["port"], acc["targets"])
        for acc in accounts
    ]
    
    results = await asyncio.gather(*tasks)
    
    print("\n=== Posting Results ===")
    for result in results:
        for profile, posts in result.items():
            print(f"\n{profile}:")
            for post in posts:
                print(f"  {post}")


# ============================================================================
# USE CASE 6: Tab pool management (reuse tabs)
# ============================================================================
async def use_case_6_tab_pool_management():
    """
    Maintain a pool of tabs and reuse them for different tasks.
    Useful for continuous scraping or monitoring.
    """
    debug_port = 9221
    profile_name = "my_facebook_profile"
    
    manager = ChromeManager(debug_port=debug_port)
    
    try:
        page = await manager.connect_to_browser_async(
            profile_name=profile_name,
            url="https://www.facebook.com"
        )
        
        context = page.context
        
        # Create a pool of tabs
        pool_size = 5
        tab_pool = []
        for i in range(pool_size):
            tab = await context.new_page()
            tab_pool.append(tab)
            print(f"Created tab {i+1}")
        
        # Simulate a queue of URLs to process
        urls_to_process = [
            f"https://www.facebook.com/page/{i}" for i in range(15)
        ]
        
        # Process URLs using the tab pool
        for i, url in enumerate(urls_to_process):
            tab = tab_pool[i % pool_size]
            
            try:
                await tab.goto(url, timeout=10000)
                title = await tab.title()
                print(f"Processed {url} in tab {(i % pool_size) + 1}: {title}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
        # Close all tabs in the pool
        for tab in tab_pool:
            await tab.close()
        
    finally:
        await manager.close_browser_async()


# ============================================================================
# Main execution
# ============================================================================
async def main():
    """Run all use cases"""
    print("=" * 80)
    print("USE CASE 1: Multiple tabs with same profile")
    print("=" * 80)
    await use_case_1_multiple_tabs_same_profile()
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("USE CASE 2: Multiple profiles with multiple tabs")
    print("=" * 80)
    await use_case_2_multiple_profiles_multiple_tabs()
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("USE CASE 3: Sequential tab processing")
    print("=" * 80)
    await use_case_3_sequential_tab_processing()
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("USE CASE 4: Dynamic tab management")
    print("=" * 80)
    await use_case_4_dynamic_tab_management()
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("USE CASE 5: Multi-account posting")
    print("=" * 80)
    await use_case_5_multi_account_posting()
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("USE CASE 6: Tab pool management")
    print("=" * 80)
    await use_case_6_tab_pool_management()


if __name__ == "__main__":
    # Run a specific use case or all of them
    
    # Run single use case:
    # asyncio.run(use_case_1_multiple_tabs_same_profile())
    
    # Run all use cases:
    asyncio.run(main())
