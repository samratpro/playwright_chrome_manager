# ChromeManager for Browser Automation

**ChromeManager** is a Python utility for automating browser interactions using Playwright. It allows you to create, manage, and reuse browser profiles (with persistent sessions) to interact with websites programmatically. This is particularly useful for tasks like web scraping, automated testing, or managing logged-in sessions across multiple websites.

The project includes a `ChromeManager` class that handles launching browsers, connecting to them via Playwright, and ensuring proper cleanup of browser processes and Playwright resources. It supports both Chrome and Edge browsers on Windows and macOS.

## Features
- **Persistent Browser Profiles**: Save and reuse browser sessions (e.g., logged-in states) for websites like Facebook or Twitter.
- **Automated Browser Management**: Launch browsers with custom profiles and connect via Playwright for automation.
- **Robust Process Cleanup**: Ensures all browser processes are terminated using `psutil` to prevent lingering processes.
- **Cross-Platform Support**: Works on Windows and macOS, with automatic detection of Chrome or Edge executables.
- **Simple API**: Easy-to-use methods for profile setup, browser connection, and cleanup.

## Prerequisites
- **Python**: Version 3.7 or higher.
- **Dependencies**:
  - `playwright`: For browser automation.
  - `psutil`: For process management.
- **Browser**: Google Chrome or Microsoft Edge installed.
- **Playwright Browser Binaries**: Installed via `playwright install`.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/samratpro/playwright_chrome_manager.git
   cd chrome-manager
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install Dependencies**:
   ```bash
   pip install playwright psutil
   playwright install
   ```

4. **Verify Browser Path**:
   - Ensure Chrome or Edge is installed at a standard location (e.g., `C:\Program Files\Google\Chrome\Application\chrome.exe` on Windows).
   - If the browser is not found, the script will prompt you to provide the path.

## Usage
The `ChromeManager` class provides methods to set up browser profiles, connect to browsers, and perform automated tasks. The `example_usage_sync.py` script demonstrates how to use it.

### Example: Setting Up and Using Browser Profiles
1. **Create or Update Profiles**:
   - Run `example_usage_sync.py` to set up profiles for websites like Facebook or Twitter.
   - The script checks if profiles (`my_facebook_profile` and `my_facebook_profile2`) exist and prompts for updates if needed.
   - During setup, a browser window opens for manual login. Close the browser to save the session.

2. **Run the Example Script**:
   ```bash
   python example_usage_sync.py
   ```

   **Sample Output**:
   ```
   ✅ Found Chrome at: C:\Program Files\Google\Chrome\Application\chrome.exe
   Profile 'my_facebook_profile' exists. Do you want to update it? (y/n): n
   Profile 'my_facebook_profile2' exists. Do you want to update it? (y/n): n
   ✅ Browser started for profile 'my_facebook_profile' (PID: 1234).
   Page Title: Facebook
   Press Enter to close the browser...
   Closed page
   Closed Playwright browser instance
   Stopped Playwright instance
   Killed child process: 5678
   Killed parent process: 1234
   ✅ Browser closed.
   ✅ Browser started for profile 'my_facebook_profile' (PID: 3456).
   Page Title: Twitter
   Press Enter to close the browser...
   Closed page
   Closed Playwright browser instance
   Stopped Playwright instance
   Killed child process: 7890
   Killed parent process: 3456
   ✅ Browser closed.
   ```

### Key Files
- **`chrome_manager.py`**: The core `ChromeManager` class for managing browser profiles and Playwright connections.
- **`example_usage_sync.py`**: A sample script demonstrating profile setup and browser automation for Facebook and Twitter.

### How It Works
1. **Profile Setup**:
   - `setup_profile`: Launches a browser with a specified profile directory, allowing manual login to save cookies and session data.
   - Profiles are stored in `C:\ChromeProfiles` (Windows) or `~/ChromeProfiles` (macOS).

2. **Browser Connection**:
   - `connect_to_browser`: Starts a browser with the specified profile and connects via Playwright for automation.
   - Supports navigating to URLs and interacting with pages (e.g., retrieving page titles).

3. **Cleanup**:
   - `close_browser`: Closes the Playwright connection and terminates all browser processes using `psutil`, ensuring no lingering processes.

## Troubleshooting
- **Empty Page Title**:
  - Ensure you log in during `setup_profile` if the website requires authentication.
  - Increase the `time.sleep(3)` in `connect_to_browser` to `time.sleep(5)` if pages load slowly.
  - Verify the URL (e.g., `https://www.twitter.com` is now `https://x.com`).

- **Port in Use Error**:
  - If you see `Port 9222 is in use`, ensure no other Chrome instances are running with remote debugging enabled.
  - Use a different `debug_port` in `ChromeManager` (e.g., `ChromeManager(debug_port=9223)`).

- **Lingering Processes**:
  - The script uses `psutil` to kill all browser processes. If processes persist, check Task Manager (Windows) and share details.

- **Dependencies**:
  - Verify installation of `playwright` and `psutil`:
    ```bash
    pip list
    ```
  - Check Playwright version:
    ```bash
    pip show playwright
    ```

## Contributing
Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or issues, please open an issue on GitHub or contact [your-email@example.com].
