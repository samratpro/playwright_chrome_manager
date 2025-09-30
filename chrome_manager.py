import os
import subprocess
import time
import platform
import socket
import psutil
from playwright.sync_api import sync_playwright

class ChromeManager:
    def __init__(self, base_profile_dir=None, browser_path=None, debug_port=9222):
        """
        Initialize the ChromeManager.
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
        """Find browser executable path."""
        if platform.system() == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                os.path.expanduser("~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            ]
        else:  # Windows
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
            ]

        # Check standard locations first
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found Chrome at: {path}")
                return path

        # If not found, prompt user
        print("❌ Chrome executable not found. Please input your Chrome path.")
        if platform.system() == "Darwin":
            print("Example: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        else:
            print("Example: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

        while True:
            user_path = input("Enter Chrome path: ").strip().strip('"')
            if not user_path:
                print("❌ Path cannot be empty. Please try again.")
                continue
            if os.path.exists(user_path):
                if user_path.lower().endswith(('chrome', 'chrome.exe', 'msedge', 'msedge.exe')):
                    print(f"✅ Chrome/Edge path verified: {user_path}")
                    return user_path
                print("❌ Path should point to Chrome or Edge executable. Please try again.")
                continue
            print(f"❌ File not found at: {user_path}")
            retry = input("Would you like to try again? (y/n): ").lower().strip()
            if retry not in ['y', 'yes']:
                raise FileNotFoundError("❌ Chrome path not found. Exiting...")

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

    def connect_to_browser(self, profile_name, url=None, headless=False):
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
                self.page.goto(url, timeout=60000)
                self.page.wait_for_load_state('load', timeout=60000)
            return self.page
        except Exception as e:
            print(f"Failed to connect to browser: {e}")
            self.close_browser()
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
        return False