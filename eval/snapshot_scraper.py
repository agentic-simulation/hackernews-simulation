from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import re
from datetime import datetime
import time
import random

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Run in headless mode
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Add human-like characteristics
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def extract_number(text):
    # Extract numbers from strings like "123 points" or "45 comments"
    match = re.search(r'(\d+)', text or '0')
    return int(match.group(1)) if match else 0

def extract_time_delta(text):
    # Extract time from strings like "7 hours ago" or "1 hour ago"
    if not text:
        return 0
    
    match = re.search(r'(\d+)\s*(hour|minute|day|month|year)s?\s+ago', text.lower())
    if not match:
        return 0
        
    value = int(match.group(1))
    unit = match.group(2)
    
    # Convert all units to hours
    multipliers = {
        'minute': 1/60,
        'hour': 1,
        'day': 24,
        'month': 24 * 30,  # approximate
        'year': 24 * 365   # approximate
    }
    
    return int(value * multipliers.get(unit, 0))

def get_post_text(driver, comments_url):
    print(f"\nAttempting to get text from: {comments_url}")
    original_window = driver.current_window_handle
    
    try:
        # Random sleep before opening new tab
        time.sleep(random.uniform(1, 3))
        
        # Open link in new tab
        print("Opening new tab...")
        driver.execute_script(f'window.open("{comments_url}","_blank");')
        driver.switch_to.window(driver.window_handles[-1])
        
        # Random sleep after page load
        time.sleep(random.uniform(2, 4))
        
        # Look for text content
        print("Looking for text elements...")
        text_elements = driver.find_elements(By.CLASS_NAME, 'toptext')
        print(f"Found {len(text_elements)} text elements")
        
        if text_elements:
            text = text_elements[0].text.strip()
            print(f"Extracted text: {text[:100]}...")  # Print first 100 chars
        else:
            text = ""
            print("No text elements found")
            
        # Close tab and switch back
        print("Closing tab and switching back...")
        driver.close()
        driver.switch_to.window(original_window)
        return text
        
    except Exception as e:
        print(f"Error getting post text: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        # Make sure we switch back to original window even if there's an error
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(original_window)
        return ""

def scrape_show_hn():
    driver = setup_driver()
    posts = []
    
    try:
        # Navigate to Show HN page
        print("\nNavigating to Show HN page...")
        driver.get('https://news.ycombinator.com/show')
        
        # Initial sleep after loading main page
        time.sleep(random.uniform(2, 4))
        
        # Find all post rows
        post_rows = driver.find_elements(By.CLASS_NAME, 'athing')
        print(f"Found {len(post_rows)} posts")
        
        for index, row in enumerate(post_rows, 1):
            try:
                print(f"\nProcessing post {index}...")
                
                # Get title and URL
                title_element = row.find_element(By.CLASS_NAME, 'titleline').find_element(By.TAG_NAME, 'a')
                title = title_element.text
                url = title_element.get_attribute('href')
                print(f"Title: {title}")
                
                # Get subtext row
                print("Getting subtext...")
                subtext = driver.find_element(By.ID, f'score_{row.get_attribute("id")}').find_element(By.XPATH, '..')
                
                # Extract points
                points_text = subtext.find_element(By.CLASS_NAME, 'score').text
                points = extract_number(points_text)
                print(f"Points: {points}")
                
                # Extract comments
                comments_link = subtext.find_elements(By.TAG_NAME, 'a')[-1]
                comments = extract_number(comments_link.text)
                print(f"Comments: {comments}")
                
                # Extract time delta
                time_element = subtext.find_element(By.CLASS_NAME, 'age').text
                time_delta = extract_time_delta(time_element)
                print(f"Time delta: {time_delta}")
                
                # Get comments URL for text extraction
                comments_url = comments_link.get_attribute('href')
                print(f"Comments URL: {comments_url}")
                text = get_post_text(driver, comments_url)
                
                post_data = {
                    "title": title,
                    "url": url,
                    "text": text,
                    "upvotes": points,
                    "comments": comments,
                    "time_delta": time_delta,
                    "rank": index,
                    "score": 0
                }
                
                posts.append(post_data)
                print("Post processed successfully")
                
            except Exception as e:
                print(f"Error processing post {index}: {str(e)}")
                continue
                
    finally:
        driver.quit()
    
    # Save to JSON file
    print("\nSaving to JSON file...")
    with open('show_hn_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    return posts

if __name__ == "__main__":
    posts = scrape_show_hn()
    print(f"Successfully scraped {len(posts)} posts")
