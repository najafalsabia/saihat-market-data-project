import asyncio
import os
import json
import re
import pandas as pd
from playwright.async_api import async_playwright

# File paths
INPUT_CSV_PATH = os.path.join(os.getcwd(), 'saihat_google_maps_deduplicated.csv')
OUTPUT_CSV_PATH = os.path.join(os.getcwd(), 'saihat_google_maps_updated.csv')

async def extract_reviews_count(page):
    """Extracts the number of reviews (e.g., 30) from the main header"""
    try:
        # Selector targeting the reviews text container next to the rating stars
        # Google Maps usually uses specific labels containing "مراجعة" or "reviews"
        review_selectors = [
            'button[jsaction*="pane.rating.moreReviews"]',
            'span[aria-label*="مراجعة"]',
            'span[aria-label*="reviews"]',
            'div.F7nice' # Common class container for rating and reviews count
        ]
        
        for selector in review_selectors:
            el = await page.query_selector(selector)
            if el:
                text = await el.inner_text()
                if text:
                    # Clean text to extract only the number (e.g., "(30)" or "30 مراجعة" -> "30")
                    numbers = re.findall(r'\d+', text.replace(',', '').replace('.', ''))
                    if numbers:
                        return int(numbers[0])
                        
        # Fallback using aria-label directly
        elements = await page.query_selector_all('span[aria-label]')
        for el in elements:
            label = await el.get_attribute('aria-label')
            if label and ("مراجعة" in label or "reviews" in label):
                numbers = re.findall(r'\d+', label.replace(',', ''))
                if numbers:
                    return int(numbers[0])
                    
        return 0 # Default to 0 if no reviews found
    except Exception:
        return 0

async def scrape_full_times_and_reviews(page, url):
    """Navigates to URL, extracts full 7 days schedule and reviews count"""
    try:
        await page.goto(url, timeout=45000)
        await page.wait_for_selector('h1', timeout=15000)
        await page.wait_for_timeout(1500)
        
        # --- 1. EXTRACT REVIEWS COUNT ---
        reviews_count = await extract_reviews_count(page)
        
        # --- 2. EXTRACT OPENING TIMES ---
        click_targets = [
            'button[data-item-id="oh"]',
            'div.OqYfcc',
            'span.ZDu9vd',
            'img[src*="schedule"]'
        ]
        
        for selector in click_targets:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.scroll_into_view_if_needed()
                    await button.click()
                    await page.wait_for_timeout(2000) # Wait for animation to fully expand
                    break
            except Exception:
                continue

        rows = await page.locator('table.eK4R0e tr, table.eKsn8e tr, tr.y0skZc').all()
        
        hours_data = {}
        if rows and len(rows) > 0:
            for row in rows:
                cells = await row.locator('td').all_text_contents()
                if len(cells) >= 2:
                    day_name = cells[0].strip().replace('：', '').replace(':', '')
                    hours_value = cells[1].strip().replace('\n', ' ')
                    if day_name and hours_value:
                        hours_data[day_name] = hours_value
                        
        if not hours_data and rows:
            for row in rows:
                text = await row.inner_text()
                if ":" in text or "：" in text or "\t" in text:
                    cleaned_text = text.replace('\t', ': ')
                    parts = [p.strip() for p in cleaned_text.split(':', 1) if p.strip()]
                    if len(parts) == 2:
                        hours_data[parts[0]] = parts[1].replace('\n', ' ')

        opening_times = "N/A"
        if hours_data and len(hours_data) > 1:
            opening_times = json.dumps(hours_data, ensure_ascii=False)
        else:
            for fallback_selector in ['span.ZDu9vd', 'div.OqYfcc']:
                element = await page.query_selector(fallback_selector)
                if element:
                    visible_text = await element.inner_text()
                    if visible_text and visible_text.strip():
                        opening_times = visible_text.strip()
                        break

        return opening_times, reviews_count
    except Exception as e:
        print(f" -> [ERROR] Failed to extract details: {e}")
        return "N/A", 0

async def main():
    if not os.path.exists(INPUT_CSV_PATH):
        print(f"[ERROR] Input file not found at: {INPUT_CSV_PATH}")
        return
    
    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"[INFO] Successfully loaded CSV file. Total rows to process: {len(df)}")
    
    if 'google_maps_url' not in df.columns:
        print("[ERROR] Column 'google_maps_url' is missing from the file!")
        return

    # Create the new column if it doesn't exist
    if 'reviews_count' not in df.columns:
        df['reviews_count'] = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="ar-SA", viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        print("\n[START] Iterating URLs to update opening_times and reviews_count...")
        
        for index, row in df.iterrows():
            url = row['google_maps_url']
            
            if pd.isna(url) or not str(url).startswith('http'):
                continue
                
            name = row.get('name_ar', f'Row {index + 1}')
            print(f"[{index + 1}/{len(df)}] Processing: {name}")
            
            # Scrape full schedule and reviews count in a single page load
            full_times, reviews_count = await scrape_full_times_and_reviews(page, url)
            
            # Update cells (opening_times updated, and reviews_count assigned)
            df.at[index, 'opening_times'] = full_times
            df.at[index, 'reviews_count'] = reviews_count
            print(f"    -> [SUCCESS] Times: {full_times[:30]}... | Reviews: {reviews_count}")
            
            # Auto-save every 5 rows
            if index % 5 == 0:
                df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
        
        await browser.close()
    
    # Save final complete output dataset
    df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"\n[FINISHED] Process completed successfully!")
    print(f"[INFO] File containing full updates has been created at:\n📁 {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    asyncio.run(main())