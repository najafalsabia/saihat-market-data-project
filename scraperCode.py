import asyncio
import re
import json
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


def normalize_text(value):
    if value is None:
        return 'N/A'
    cleaned = re.sub(r'\s+', ' ', str(value)).strip()
    return cleaned or 'N/A'


async def extract_plus_code(detail_page):
    selector = 'div.Io6YTe.fontBodyMedium.kR99db.fdkmkc'
    
    try:
        await detail_page.locator(selector).first.wait_for(state="visible", timeout=5000)
        
        elements = detail_page.locator(selector)
        count = await elements.count()
        plus_code_pattern = re.compile(r'[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}')
        
        for i in range(count):
            text = await elements.nth(i).inner_text()
            match = plus_code_pattern.search(text)
            
            if match:
                just_the_code = match.group(0).strip()
                return just_the_code
        return 'N/A'
        
    except Exception as e:
        return 'N/A'


async def extract_opening_times(detail_page):
    rows = detail_page.locator('table.eK4R0e.fontBodyMedium tr.y0skZc')
    row_count = await rows.count()
    hours_data = {}

    for idx in range(row_count):
        row = rows.nth(idx)
        cells = await row.locator('td').all_text_contents()
        if len(cells) >= 2:
            day_name = normalize_text(cells[0])
            hours_value = normalize_text(cells[1])
            if day_name and hours_value:
                hours_data[day_name] = hours_value

    if hours_data:
        return json.dumps(hours_data, ensure_ascii=False)
    return 'N/A'


async def extract_price_range(detail_page):
    await detail_page.wait_for_timeout(2000)

    price_map = {
        '$': 'رخيص',
        '$$': 'متوسط',
        '$$$': 'غالي',
        '$$$$': 'مكلف',
        'cheap': 'رخيص',
        'inexpensive': 'رخيص',
        'رخيص': 'رخيص',
        'moderate': 'متوسط',
        'متوسط': 'متوسط',
        'معتدل': 'متوسط',
        'expensive': 'غالي',
        'غالي': 'غالي',
        'very expensive': 'مكلف',
        'مكلف': 'مكلف',
    }

    selectors = [
        'span.mgr77e',
        'span[role="img"]',
        '[aria-label*="expensive" i]',
        '[aria-label*="moderate" i]',
        '[aria-label*="cheap" i]',
        '[aria-label*="inexpensive" i]',
        '[aria-label*="price" i]',
    ]

    for selector in selectors:
        try:
            locator = detail_page.locator(selector)
            if await locator.count() > 0:
                raw_html = await locator.first.evaluate("el => (el.outerHTML || el.innerHTML || el.textContent || '')")
                raw_text = normalize_text(raw_html).lower()

                price_match = re.search(r'(\${1,4})', raw_text)
                if price_match:
                    return price_map.get(price_match.group(1), 'N/A')

                for keyword, label in price_map.items():
                    if keyword in raw_text:
                        return label
        except Exception:
            continue

    try:
        body_text = normalize_text(await detail_page.locator('body').inner_text()).lower()
        price_match = re.search(r'(\${1,4})', body_text)
        if price_match:
            return price_map.get(price_match.group(1), 'N/A')

        for keyword, label in price_map.items():
            if keyword in body_text:
                return label
    except Exception:
        pass

    return 'N/A'


async def extract_open_status(detail_page):
    status_el = detail_page.locator('span.ZDu9vd')
    if await status_el.count() > 0:
        return normalize_text(await status_el.first.inner_text())
    return 'N/A'


async def scrape_location(detail_page, p_url):
    try:
        await detail_page.goto(p_url, timeout=45000)
        await detail_page.wait_for_selector('h1.DUwDvf', timeout=10000)
        await detail_page.wait_for_timeout(1000)
        
        title_el = await detail_page.query_selector('h1.DUwDvf')
        title = await title_el.inner_text() if title_el else 'N/A'
        
        category_el = await detail_page.query_selector('button.DkEaL')
        category = await category_el.inner_text() if category_el else 'N/A'
        
        address_el = await detail_page.query_selector('button[data-item-id="address"]')
        address = await address_el.get_attribute('aria-label') if address_el else 'N/A'
        
        phone_el = await detail_page.query_selector('button[data-item-id^="phone:tel:"]')
        phone = await phone_el.get_attribute('aria-label') if phone_el else 'N/A'
        
        website_el = await detail_page.query_selector('a[data-item-id="authority"]')
        website = await website_el.get_attribute('href') if website_el else 'N/A'
        
        rating_el = await detail_page.query_selector('div.F7nice span')
        rating = await rating_el.inner_text() if rating_el else 'N/A'

        plus_code = await extract_plus_code(detail_page)
        opening_times = await extract_opening_times(detail_page)
        price_range = await extract_price_range(detail_page)
        opening_status = await extract_open_status(detail_page)

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
            'plus_code': plus_code,
            'opening_times': opening_times,
            'opening_status': opening_status,
            'price_range': price_range,
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

#_____________________________________________________________________

async def scrape_keyword(browser, keyword):
    # Prepare the url, open a new page, and go to the url.
    print(f"\n[START] Searching for: {keyword}")
    page = await browser.new_page()
    
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.google.com/maps/search/{encoded_kw}?hl=ar"
    
    try:
        await page.goto(url, timeout=10000)
    except Exception as e:
        print(f"[ERROR] Cannot load URL: {e}")
        await page.close()
        return

    # Wait for the sidebar to load and determine which selector is active.
    sidebar_selector = '.m6U6Mc, div[role="feed"]'
    try:
        await page.wait_for_selector(sidebar_selector, timeout=15000)
        active_sidebar = '.m6U6Mc' if await page.query_selector('.m6U6Mc') else 'div[role="feed"]'
    except Exception:
        print(f"[SKIP] Sidebar container not found for '{keyword}'. Skipping...")
        await page.close()
        return

    print(f"Scrolling down to get ALL places for ({keyword})...")
    
    # Scroll down the sidebar until we reach the end or hit the max attempts.
    scroll_attempts = 0
    max_scroll_attempts = 40  
    while scroll_attempts < max_scroll_attempts:
        await page.evaluate(f"document.querySelector('{active_sidebar}').scrollBy(0, 10000)")
        await page.wait_for_timeout(2000)
        
        end_visible = await page.locator('text="وصلت إلى نهاية القائمة"').is_visible() or \
                      await page.locator('text="نهاية القائمة"').is_visible() or \
                      await page.locator('text="You\'ve reached the end of the list."').is_visible()
        if end_visible:
            print("Reached the very end of the list!")
            break
        scroll_attempts += 1

    # After scrolling, extract all the place links from the sidebar.
    # 'hfpxzc' is the class for the anchor tags of the places in the sidebar.
    place_elements = await page.query_selector_all('a.hfpxzc')
    place_urls = []
    # extract the individual place URLs from the anchor elements.
    for el in place_elements:
        href = await el.get_attribute('href')
        if href:
            place_urls.append(href)

    print(f"Found total of {len(place_urls)} links for {keyword}. Starting full extraction...")
    await page.close()

    # for each place URL, open a new page and extract the required details.
    for idx, p_url in enumerate(place_urls):
        detail_page = await browser.new_page()
        await scrape_location(detail_page, p_url)



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