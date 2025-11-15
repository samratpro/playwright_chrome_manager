import os
import subprocess
import time
import platform
import socket
import psutil
from playwright.sync_api import sync_playwright

class BrowserManager:
    def __init__(self, base_profile_dir=None, browser_path=None, debug_port=9222):
        """
        Initialize the BrowserManager.
        :param base_profile_dir: Base directory for profile folders (default: ~/ChromeProfiles or C:\ChromeProfiles).
        :param browser_path: Path to browser executable (auto-detected if None).
        :param debug_port: Port for remote debugging (default: 9222).
        """
        if base_profile_dir is None:
            base_profile_dir = "C:\\ChromeProfiles" if platform.system() != "Darwin" else os.path.expanduser("~/ChromeProfiles")
        self.base_profile_dir = base_profile_dir
        os.makedirs(self.base_profile_dir, exist_ok=True)
        self.browser_path = browser_path or self._find_browser_path()
        self.debug_port = debug_port
        self.browser_process = None
        self.playwright_instance = None
        self.browser = None
        self.page = None
        self.process_pid = None

    def _find_browser_path(self):
        """
        Find browser executable with priority:
            1. Brave
            2. Comet
            3. Edge
            4. Chrome
            5. Chromium
        Returns the first existing path or prompts the user.
        """
        import sys
        system = platform.system()
        possible_paths = []
    
        # --------------------------------------------------------------------- macOS
        if system == "Darwin":
            possible_paths = [
                # 1. Brave
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                os.path.expanduser("~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
                # 2. Comet
                "/Applications/Comet Browser.app/Contents/MacOS/Comet Browser",
                os.path.expanduser("~/Applications/Comet Browser.app/Contents/MacOS/Comet Browser"),
                # 3. Edge
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                os.path.expanduser("~/Applications/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
                # 4. Chrome
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                # 5. Chromium
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                os.path.expanduser("~/Applications/Chromium.app/Contents/MacOS/Chromium"),
            ]
    
        # --------------------------------------------------------------------- Windows
        elif system == "Windows":
            possible_paths = [
                # 1. Brave
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
                # 2. Comet
                r"C:\Program Files\CometBrowser\Application\comet.exe",
                r"C:\Program Files (x86)\CometBrowser\Application\comet.exe",
                os.path.expanduser(r"~\AppData\Local\CometBrowser\Application\comet.exe"),
                # 3. Edge
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
                # 4. Chrome (stable + beta + canary)
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                r"C:\Program Files\Google\Chrome Canary\Application\chrome.exe",
                # 5. Chromium
                r"C:\Program Files\Chromium\Application\chromium.exe",
                r"C:\Program Files (x86)\Chromium\Application\chromium.exe",
                os.path.expanduser(r"~\AppData\Local\Chromium\Application\chromium.exe"),
            ]
    
        # --------------------------------------------------------------------- Linux
        elif system == "Linux":
            possible_paths = [
                # 1. Brave
                "/usr/bin/brave-browser",
                "/usr/bin/brave",
                "/usr/local/bin/brave-browser",
                "/usr/local/bin/brave",
                os.path.expanduser("~/.local/bin/brave-browser"),
                # 2. Comet
                "/usr/bin/comet-browser",
                "/usr/bin/comet",
                "/usr/local/bin/comet-browser",
                "/usr/local/bin/comet",
                os.path.expanduser("~/.local/bin/comet-browser"),
                # 3. Edge
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable",
                "/usr/local/bin/microsoft-edge",
                # 4. Chrome
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/local/bin/google-chrome",
                # 5. Chromium
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/local/bin/chromium",
                os.path.expanduser("~/.local/bin/chromium"),
            ]
    
        # --------------------------------------------------------------------- Scan
        print("\nScanning for browser executable (priority order)...", flush=True)
        for p in possible_paths:
            exists = os.path.exists(p)
            print(f"  {'Found' if exists else 'Not found'} {p}", flush=True)
            if exists:
                print(f"\nSELECTED: {p}\n", flush=True)
                return p
    
        # --------------------------------------------------------------------- Prompt user
        print("\nNo supported browser found in standard locations.", flush=True)
        print("Please paste the **full path** to the executable (e.g. brave.exe, comet.exe, chrome.exe.exe, chrome.exe).", flush=True)
        print("Tip: right-click the browser shortcut → Properties → copy the 'Target' field.\n", flush=True)
    
        while True:
            try:
                user_path = input("BROWSER PATH: ").strip().strip('"\'')
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled by user.", flush=True)
                sys.exit(1)
    
            if not user_path:
                print("Empty input – try again.", flush=True)
                continue
    
            if os.path.exists(user_path):
                name = os.path.basename(user_path).lower()
                if any(exe in name for exe in ("brave", "comet", "msedge", "chrome", "chromium")):
                    print(f"\nACCEPTED: {user_path}\n", flush=True)
                    return user_path
                else:
                    print("File name does not look like a supported browser.", flush=True)
            else:
                print(f"File not found: {user_path}", flush=True)
    
            retry = input("Try another path? (y/n): ").strip().lower()
            if retry not in ("y", "yes"):
                print("No path provided – exiting.", flush=True)
                sys.exit(1)

    def _is_port_open(self, port):
        """Check if the specified port is available."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) != 0

    def _kill_child_processes(self, pid):
        """Kill all child processes of the given PID."""
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                try:
                    child.kill()
                    print(f"Killed child process: {child.pid}")
                except psutil.NoSuchProcess:
                    pass
            parent.kill()
            print(f"Killed parent process: {pid}")
        except psutil.NoSuchProcess:
            print(f"Process {pid} no longer exists")
        except Exception as e:
            print(f"Error killing processes: {e}")

    def get_profile_path(self, profile_name):
        """Get the full path to the profile directory."""
        return os.path.join(self.base_profile_dir, profile_name)

    def profile_exists(self, profile_name):
        """Check if a profile exists."""
        return os.path.exists(self.get_profile_path(profile_name))

    def setup_profile(self, profile_name, url=None, wait_message="Perform manual actions, then close the browser to save.", headless=False):
        """Start browser for manual interaction to create or update a profile."""
        user_data_dir = self.get_profile_path(profile_name)
        if not self._is_port_open(self.debug_port):
            raise RuntimeError(f"Port {self.debug_port} is in use. Choose another port.")
        args = [
            self.browser_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        if url:
            args.append(url)
        if headless:
            args.append("--headless=new")
        print(f"Starting browser for profile '{profile_name}'")
        print(wait_message)
        process = subprocess.Popen(args, shell=False)
        process.wait()
        self.close_browser()
        print(f"✅ Profile '{profile_name}' saved.")

    def connect_to_browser(self, profile_name, url=None, headless=False, timeout=60000):
        """Start browser with the specified profile and connect via Playwright."""
        if not self.profile_exists(profile_name):
            raise ValueError(f"Profile '{profile_name}' does not exist. Create it first.")
        if not self._is_port_open(self.debug_port):
            raise RuntimeError(f"Port {self.debug_port} is in use. Choose another port.")
        user_data_dir = self.get_profile_path(profile_name)
        args = [
            self.browser_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        """
        example PowerShell command here:
            & "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" `
              --remote-debugging-port=9222 `
              --user-data-dir="C:\ChromeProfiles\wp_profile_jobboardai" `
              --no-first-run `
              --no-default-browser-check `
              "https://docs.python.org/3/library/subprocess.html"
        """
        if headless:
            args.append("--headless=new")
        self.browser_process = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process_pid = self.browser_process.pid
        time.sleep(3)  # Wait for browser to start
        print(f"✅ Browser started for profile '{profile_name}' (PID: {self.process_pid}).")
        try:
            self.playwright_instance = sync_playwright().start()
            self.browser = self.playwright_instance.chromium.connect_over_cdp(f"http://127.0.0.1:{self.debug_port}")
            contexts = self.browser.contexts
            self.page = contexts[0].pages[0] if contexts and contexts[0].pages else self.browser.new_page()
            if url:
                self.page.goto(url, timeout=timeout)
                self.page.wait_for_load_state('load', timeout=timeout)
            return self.page
        except Exception as e:
            print(f"Failed to connect to browser: {e}")
            self.close_browser()
            raise
            
        async def connect_to_browser_async(self, profile_name, url=None, headless=False, timeout=60000):
            """Start browser with the specified profile and connect via Playwright (async)."""
            if not self.profile_exists(profile_name):
                raise ValueError(f"Profile '{profile_name}' does not exist. Create it first.")
            if not self._is_port_open(self.debug_port):
                raise RuntimeError(f"Port {self.debug_port} is in use. Choose another port.")
            user_data_dir = self.get_profile_path(profile_name)
            args = [
                self.browser_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-features=BraveShields",
                "--brave-ads-service-enabled=0",
            ]
            if headless:
                args.append("--headless=new")
            self.browser_process = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
            self.process_pid = self.browser_process.pid
            print(f"✅ Browser started for profile '{profile_name}' (PID: {self.process_pid}).")
    
            # Wait a moment for browser to start
            time.sleep(2)
    
            try:
                self.playwright_instance = await async_playwright().start()
                self.browser = await self.playwright_instance.chromium.connect_over_cdp(
                    f"http://127.0.0.1:{self.debug_port}")
                contexts = self.browser.contexts
                if contexts and contexts[0].pages:
                    self.page = contexts[0].pages[0]
                else:
                    self.page = await self.browser.new_page()
    
                if url:
                    await self.page.goto(url, timeout=timeout)
                    await self.page.wait_for_load_state('load', timeout=timeout)
                return self.page
            except Exception as e:
                print(f"Failed to connect to browser: {e}")
                await self.close_browser_async()
                raise

    def close_browser(self):
        """Close the browser and clean up all resources."""
        if self.page:
            try:
                self.page.close()
                print("Closed page")
            except Exception as e:
                print(f"Error closing page: {e}")
            self.page = None
        if self.browser:
            try:
                self.browser.close()
                print("Closed Playwright browser instance")
            except Exception as e:
                print(f"Error closing browser: {e}")
            self.browser = None
        if self.playwright_instance:
            try:
                self.playwright_instance.stop()
                print("Stopped Playwright instance")
            except Exception as e:
                print(f"Error stopping Playwright: {e}")
            self.playwright_instance = None
        if self.browser_process and self.process_pid:
            try:
                self._kill_child_processes(self.process_pid)
            except Exception as e:
                print(f"Error killing browser process: {e}")
            finally:
                try:
                    self.browser_process.stdin.close()
                    self.browser_process.stdout.close()
                    self.browser_process.stderr.close()
                except Exception:
                    pass
            self.browser_process = None
            self.process_pid = None
        print("✅ Browser closed.")

        async def close_browser_async(self):
            """Close the browser and clean up all resources (async)."""
            if self.page:
                try:
                    await self.page.close()
                    print("Closed page")
                except Exception as e:
                    print(f"Error closing page: {e}")
                self.page = None
            if self.browser:
                try:
                    await self.browser.close()
                    print("Closed Playwright browser instance")
                except Exception as e:
                    print(f"Error closing browser: {e}")
                self.browser = None
            if self.playwright_instance:
                try:
                    await self.playwright_instance.stop()
                    print("Stopped Playwright instance")
                except Exception as e:
                    print(f"Error stopping Playwright: {e}")
                self.playwright_instance = None
            if self.browser_process and self.process_pid:
                try:
                    self._kill_child_processes(self.process_pid)
                except Exception as e:
                    print(f"Error killing browser process: {e}")
                finally:
                    try:
                        self.browser_process.stdin.close()
                        self.browser_process.stdout.close()
                        self.browser_process.stderr.close()
                    except Exception:
                        pass
                self.browser_process = None
                self.process_pid = None
            print("✅ Browser closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
        return False





