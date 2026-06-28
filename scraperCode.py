import asyncio
import re
import os
import pandas as pd
import urllib.parse
from playwright.async_api import async_playwright

scraped_places = []
CSV_FILE_PATH = os.path.join(os.getcwd(), 'saihat_google_maps_dataset.csv')

def append_to_csv(place_data):
    """Save the place immediately after scraping, only if it is inside Saihat"""
    global scraped_places
    
    address = str(place_data.get('full_address', '')).lower()
    name = str(place_data.get('name_ar', '')).lower()
    
    # Skip if "سيهات" or "saihat" is not in the address or name
    if "سيهات" not in address and "سيهات" not in name and "saihat" not in address and "saihat" not in name:
        print(f" [SKIPPED] -> {place_data.get('name_ar')} (Location outside Saihat)")
        return

    scraped_places.append(place_data)
    df = pd.DataFrame(scraped_places)
    
    # Remove duplicates based on Google Maps URL
    df.drop_duplicates(subset=['google_maps_url'], keep='first', inplace=True)
    df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8-sig')
    print(f" [SAVED] -> {place_data.get('name_ar')}")

async def scrape_keyword(browser, keyword):
    print(f"\n[START] Searching for: {keyword}")
    page = await browser.new_page()
    
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.google.com/maps/search/{encoded_kw}?hl=ar"
    
    try:
        await page.goto(url, timeout=60000)
    except Exception as e:
        print(f"[ERROR] Cannot load URL: {e}")
        await page.close()
        return

    sidebar_selector = '.m6U6Mc, div[role="feed"]'
    try:
        await page.wait_for_selector(sidebar_selector, timeout=15000)
        active_sidebar = '.m6U6Mc' if await page.query_selector('.m6U6Mc') else 'div[role="feed"]'
    except Exception:
        print(f"[SKIP] Sidebar container not found for '{keyword}'. Skipping...")
        await page.close()
        return

    print(f"Scrolling down to get ALL places for ({keyword})...")
    
    scroll_attempts = 0
    max_scroll_attempts = 40  
    while scroll_attempts < max_scroll_attempts:
        await page.evaluate(f"document.querySelector('{active_sidebar}').scrollBy(0, 10000)")
        await page.wait_for_timeout(2000)
        
        end_visible = await page.locator('text="وصلت إلى نهاية القائمة"').is_visible() or \
                      await page.locator('text="You\'ve reached the end of the list."').is_visible()
        if end_visible:
            print("Reached the very end of the list!")
            break
        scroll_attempts += 1

    place_elements = await page.query_selector_all('a.hfpxzc')
    place_urls = []
    for el in place_elements:
        href = await el.get_attribute('href')
        if href:
            place_urls.append(href)

    print(f"Found total of {len(place_urls)} links for {keyword}. Starting full extraction...")
    await page.close()

    for idx, p_url in enumerate(place_urls):
        detail_page = await browser.new_page()
        try:
            await detail_page.goto(p_url, timeout=45000)
            await detail_page.wait_for_selector('h1.DUwDvf', timeout=10000)
            await detail_page.wait_for_timeout(1000)
            
            title_el = await detail_page.query_selector('h1.DUwDvf')
            title = await title_el.inner_text() if title_el else 'N/A'
            
            category_el = await detail_page.query_selector('button.DkEaGf')
            category = await category_el.inner_text() if category_el else 'N/A'
            
            address_el = await detail_page.query_selector('button[data-item-id="address"]')
            address = await address_el.get_attribute('aria-label') if address_el else 'N/A'
            
            phone_el = await detail_page.query_selector('button[data-item-id^="phone:tel:"]')
            phone = await phone_el.get_attribute('aria-label') if phone_el else 'N/A'
            
            website_el = await detail_page.query_selector('a[data-item-id="authority"]')
            website = await website_el.get_attribute('href') if website_el else 'N/A'
            
            rating_el = await detail_page.query_selector('div.F7nice span')
            rating = await rating_el.inner_text() if rating_el else 'N/A'

            lat, lon = 'N/A', 'N/A'
            match = re.search(r'@([-0-9.]+),([-0-9.]+)', detail_page.url)
            if match:
                lat, lon = match.group(1), match.group(2)

            place_data = {
                'name_ar': title.strip(),
                'category': category.strip(),
                'full_address': address.replace('العنوان: ', '').replace('Address: ', '').strip(),
                'phone_number': phone.replace('الهاتف: ', '').replace('Phone: ', '').strip(),
                'website': website,
                'rating': rating,
                'city_ar': 'سيهات',
                'region_ar': 'المنطقة الشرقية',
                'latitude': lat,
                'longitude': lon,
                'google_maps_url': detail_page.url,
            }
            
            append_to_csv(place_data)
            
        except Exception:
            pass
        finally:
            await detail_page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        keywords = [
            "شركات في سيهات", "مكاتب استشارات في سيهات", "شركات مقاولات في سيهات", 
            "مكاتب توظيف في سيهات", "شركات شحن في سيهات", "مكاتب عقارية في سيهات",
            "مكاتب محاماة في سيهات", "مكاتب محاسبة في سيهات", "حلاق في سيهات", 
            "صالون تجميل في سيهات", "صيدليات في سيهات", "مستوصفات في سيهات", 
            "سوبرماركت في سيهات", "مخابز في سيهات", "محطات وقود في سيهات", 
            "مساجد في سيهات", "صالات رياضية في سيهات", "مكتبات في سيهات", 
            "محلات ملابس في سيهات", "ورش سيارات في سيهات", "مراكز تسوق في سيهات", 
            "عيادات أسنان في سيهات", "خياط في سيهات", "محلات عطور في سيهات", 
            "مغاسل سيارات في سيهات", "محلات جوالات في سيهات", "مطابع في سيهات", 
            "مراكز تدريب في سيهات", "محلات أثاث في سيهات", "مغاسل ملابس في سيهات"
        ]
        
        try:
            for kw in keywords:
                await scrape_keyword(browser, kw)
        finally:
            await browser.close()
            print(f"\n--- Process Finished! All data has been successfully collected and saved ---")

if __name__ == '__main__':
    try:
        print("Starting Google Maps Scraper...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[STOP] Process interrupted manually. All scraped data remains saved in the CSV file.")