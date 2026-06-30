# Data Pipeline Documentation

This documentation provides a comprehensive and detailed overview of the technical lifecycle of the project. It covers the automated distributed data collection stage (Data Scraping) from Google Maps, followed by the engineering and cleaning phases (Data Cleaning & Preprocessing), and concludes with data insights and Geospatial Graphical Analysis.

---

## 📌 Table of Contents
1. [Data Overview](#1-data-overview)
2. [Data Scraping Phase](#2-data-scraping-phase)
3. [Data Cleaning & Preprocessing](#3-data-cleaning--preprocessing)
4. [Data Analysis & Geospatial Insights](#4-data-analysis--geospatial-insights)

---

## 1. Data Overview
* **Data Description:** This project focuses on building an integrated geospatial dataset for establishments, public services, commercial activities, and government facilities within Saihat City.
* **Target Platform:** Google Maps, accessed via its localized Arabic interface (`hl=ar`) to capture native business naming conventions.
* **Methodological Approach:** Data collection was scaled using a split-workload, distributed processing strategy across multiple local nodes to systematically cover all commercial and municipal sectors of the city.
* **Strategic Objective:** To provide clean, reliable, and highly structured data to perform advanced graphical and geospatial analysis. By mapping precise coordinates and user engagement metrics (ratings and review counts), the project successfully visualizes the geographic density of facilities, discovers commercial sector distributions, and identifies operational patterns across Saihat City to support smart-city infrastructure development.

---

## 2. Data Scraping Phase
In this stage, an advanced custom scraper was engineered for automated data extraction using the modern **Playwright** framework implemented within an asynchronous architecture (`asyncio`).

### A. Tech Stack & Dependencies
* **`Playwright (Async API)`**: Utilized to launch Chromium browser instances and simulate real human browsing behaviors (searching, navigating, and expanding dynamic web pages).
* **`Asyncio`**: Used to manage asynchronous, non-blocking tasks efficiently, maximizing data extraction speed.
* **`Pandas`**: Employed to manage the structured tabular data and incrementally update the dataset.
* **`Regular Expressions (re)`**: Used for initial text normalization, extracting postal Plus Codes, and parsing coordinates from live URLs.

### B. Distributed Execution & Parallel Processing Architecture
To optimize scraping throughput and drastically minimize total collection time, the data collection pipeline was deployed utilizing a **Distributed Parallel Architecture**:
* **Workload Partitioning (60 Total Keywords):** The master search strategy relied on a highly comprehensive dictionary of 60 targeted localized keywords, which was evenly bisected into two distinct workloads (30 unique keywords per node) running simultaneously across two separate machine nodes (the laptops of both development teammates).
  * **Node 1 (Teammate Laptop A):** Focused on localized commercial and standard utility services, executing 30 custom keywords:
    ```python
    keywords_node_1 = [
        "شركات في سيهات", "مكاتب استشارات في سيهات", "شركات مقاولات في سيهات", 
        "مكاتب توظيف في سيهات", "شركات شحن في سيهات", "مكاتب عقارية in سيهات",
        "مكاتب محاماة في سيهات", "مكاتب محاسبة في سيهات", "حلاق في سيهات", 
        "صالون تجميل في سيهات", "صيدليات في سيهات", "مستوصفات في سيهات", 
        "سوبرماركت في سيهات", "مخابز في سيهات", "محطات وقود في سيهات", 
        "مساجد في سيهات", "صالات رياضية في سيهات", "مكتبات في سيهات", 
        "محلات ملابس في سيهات", "ورش سيارات في سيهات", "مراكز تسوق في سيهات", 
        "عيادات أسنان في سيهات", "خياط في سيهات", "محلات عطور في سيهات", 
        "مغاسل سيارات في سيهات", "محلات جوالات في سيهات", "مطابع في سيهات", 
        "مراكز تدريب في سيهات", "محلات أثاث في سيهات", "مغاسل ملابس في سيهات"
    ]
    ```
  * **Node 2 (Teammate Laptop B):** Focused on critical infrastructure, public administration, and specialized amenities, executing 30 custom keywords:
    ```python
    keywords_node_2 = [
        "مراكز شرطة في سيهات", "الدفاع المدني في سيهات", "البريد السعودي في سيهات", "جمعيات خيرية في سيهات", "مستشفيات في سيهات",
        "مدارس بنين في سيهات", "مدارس بنات في سيهات", "رياض أطفال في سيهات", "حدائق عامة في سيهات", "قاعات أفراح في سيهات",
        "كورنيش سيهات", "بنوك ومصارف في سيهات", "فنادق وشقق مفروشة في سيهات", "مكاتب استقدام في سيهات", "محلات نظارات في سيهات",
        "محلات حلويات في سيهات", "كافيهات في سيهات", "مطاعم في سيهات", "محامص ومكسرات في سيهات", "أجهزة صراف آلي في سيهات",
        "مكاتب سفر وسياحة في سيهات", "محلات ألعاب أطفال في سيهات", "ملاعب كرة قدم في سيهات", "نوادي رياضية نسائية في سيهات", "معارض سيارات في سيهات",
        "محلات أسماك في سيهات", "محلات زهور وهدايا في سيهات", "مراكز علاج طبيعي في سيهات", "مختبرات طبية في سيهات", "عيادات بيطرية في سيهات"
    ]
    ```
* **Localized Scraping:** Each independent node processed its target partition asynchronously, generating partial output collections.
* **Pipeline Synthesis (Merging Phase):** A custom compilation script was executed to perform a loss-less structural merge of the localized dataset partitions, synthesis-mapping them into a unified multi-variant database saved as `saihat_google_maps_merged.csv`.

### C. Initial Target Schema
The compiled raw dataset initialized and successfully extracted **15 distinct structural attributes (columns)** directly from the Google Maps interface:
* **Core Entity Information:** `name_ar` (Business Name), `category` (Business Type), `full_address` (Full Text Address), `phone_number` (Raw Contact Number), `website` (Official URL).
* **Consumer Metrics:** `rating` (Star Rating), `price_range` (Initial Price Indicator).
* **Geospatial & Status Metadata:** `latitude` (Latitude Coordinate), `longitude` (Longitude Coordinate), `plus_code` (Google Plus Code), `opening_times` (Single-day Operational Schedule), `opening_status` (Live Status, e.g., "Open Now"), `city_ar` (City - Saihat), `region_ar` (Region - Eastern Province), `Maps_url` (Definitive Map Link).

### D. Data Integrity & Quality Safeguards
* **On-the-fly Geospatial Filtering:** Within the `append_to_csv` function, a strict textual validator checked the address and name fields. If the string "سيهات" or "Saihat" was entirely absent, the script immediately logged a `[SKIPPED]` entry, isolating the records strictly to the targeted geographical boundary.
* **Incremental, Safe Commitments:** Records were committed and saved dynamically using the proper `utf-8-sig` encoding (fully preserving Arabic text formatting) to protect the data from corruption or loss in the event of manual script interruptions (`KeyboardInterrupt`).

---

## 3. Data Cleaning & Preprocessing
After collecting the raw records (`saihat_google_maps_merged.csv`), an extensive, multi-staged data engineering and preprocessing pipeline was executed to guarantee data consistency, integrity, and readiness for graphical analysis.

<details>
<summary><b>🛠️ Click to expand the detailed Data Cleaning steps</b></summary>

### A. Two-Phase De-duplication
Duplicate entries arising from overlapping query categories were thoroughly eliminated using a dual-filtering strategy:
* **Initial Drop:** Redundant rows were evaluated based on the unique `Maps_url`.
* **Secondary Refinement:** A rigorous structural de-duplication cross-referenced business names and spatial properties, resolving any structural overlaps and saving the unified clean state into `saihat_google_maps_deduplicated.csv`.

### B. Feature Standardization & Normalization
* **Phone Numbers:** Contact details were unified into a standardized international string format. 
* **Phone Type Classification:** A new feature mapping column (`phone_type`) was established to categorize contacts systematically into three distinct communication channels based on Saudi local standards: **Mobile**, **Landline**, and **Unified Numbers** (e.g., 9200/800 corporate lines).
* **Websites:** Corporate URLs and anchor links were normalized to fix encoding distortions and ensure standard web protocols.

### C. Addressing Structural Data Gaps (Iterative Targeted Re-scraping)
During initial dataset inspection of `saihat_google_maps_deduplicated.csv`, major structural limitations and missingness were quantified:
1. **Extreme Feature Sparsity (`price_range`):** The `price_range` attribute was highly constrained, resulting in 1,147 out of 1,166 total rows (approximately 98.3%) being null. Retaining a column with this level of missingness introduces structural noise and offers no analytical value.
2. **Incomplete Schedule Information (`opening_times`):** The initial scraping phase only captured operating hours for a single day (the day of execution) instead of extracting the full weekly schedule.

* **The Engineering Solution:** A secondary, targeted scraping pipeline (`update_opening_times.py`) was deployed to overcome these limitations and significantly enhance data quality, producing the updated dataset (`saihat_google_maps_updated.csv`).
* **Feature Substitution (`reviews_count`):** Because the `price_range` column was dropped due to extreme sparsity, the `reviews_count` feature was extracted during the second pipeline execution as a robust alternative to capture consumer engagement and establishment popularity. 
* **Logical Schema Realignment:** To ensure structural consistency and a more logical layout, the newly acquired `reviews_count` column was repositioned directly next to the `rating` feature.
* **Full Schedule Retrieval:** The secondary pipeline successfully resolved the temporal limitation, capturing complete, structured 7-day operational schedules into JSON objects within the `opening_times` column.

### D. Advanced Precision Cleaning & Casting
* **Float-to-String Cast Correction:** Due to the presence of missing values (NaN) in the phone numbers within the initial dataset, Pandas automatically upcasted the column data type to a `float`, appending an undesirable `.0` to the end of the phone digits. This was resolved by explicitly cleaning the digits, casting the column to a pure textual string format, and stripping the trailing `.0` to prevent structural formatting corruption.

### E. Manual Geospatial Ground-Truth Imputation
Because the strategic goal of this project requires highly accurate graphical mapping, missing spatial coordinates could not be ignored:
* The dataset revealed exactly **16 missing coordinate pairs** (Latitude/Longitude).
* Instead of dropping these rows and losing valuable data, a meticulous **manual imputation process** was conducted. Each location was searched manually via Google Maps to retrieve its definitive ground-truth latitude and longitude, achieving 100% geospatial completeness across all rows before finalized textual sanitation.

### F. Unicode Noise Removal & Final Polish
* **Unicode Noise Removal:** As the absolute final polishing layer, hidden formatting characters and structural noise—specifically the Invisible Left-to-Right Mark (`[U+200E]`) caused by bi-directional Arabic/English text wrapping—were stripped entirely from the `full_address` and `name_ar` columns to ensure seamless pattern matching and visual clean rendering.

The finalized, high-purity dataset was saved as `saihat_google_maps_updated.csv`.

</details>

---

## 4. Data Analysis & Geospatial Insights

### A. Interactive Geospatial Mapping Architecture
To translate the cleaned dataset (`saihat_google_maps_updated.csv`) into structured visual intelligence, an advanced geospatial visualization pipeline was engineered using Python's **Folium** framework. This mapping layer acts as the primary graphical analytical output for studying Saihat City's commercial and public density.

### B. Map Technical Configurations & Layout
The implemented graphical map leverages several algorithmic and visual mechanisms to maximize readability and insight extraction:
* **Precise Geographic Coordinates:** Utilizing the 100% complete coordinate matrix (including the 16 manually recovered missing instances), points are plotted via definitive `latitude` and `longitude` fields.
* **Smart Marker Clustering:** To resolve visual crowding and overlapping in high-density commercial centers (e.g., main avenues), markers are systematically encapsulated into dynamic clusters that automatically partition and expand as the evaluator zooms into specific neighborhoods.
* **Thematic Color-Coding (Graphical Analysis):** Establishments are mapped into multi-category layers and color-coded dynamically according to their sector classifications (e.g., *Retail & Shopping / تجزئة وتسوق*, *Restaurants & Cafes / مطاعم ومقاهي*, *Beauty & Personal Care / تجميل وعناية*, *Governmental & Community / جهات حكومية ومجتمعية*).
* **Rich Data Popups:** Clicking on any marker triggers an interactive, real-time popup containing fully structured entity metadata, including:
  * Official Business Name (in native Arabic notation).
  * Specific Sub-Category & General Classification.
  * Live Operational Status (e.g., Open Now / Closed).
  * Consumer Performance Metrics (Exact Google Rating score and total `reviews_count`).
  * Clean Formatted Contact Number.

### C. Analytical Insights Captured
* **Commercial Hotspots:** Immediate graphical discovery of dense business clusters along key corridors and central intersections within Saihat City.
* **Category Dominance Assessment:** Visual evidence confirming the proportional footprint of sectors, showcasing dominant trades like "تجزئة وتسوق" (163 records) and "مطاعم ومقاهي" (138 records) relative to public utilities.
* **Coverage Gap Discovery:** The interactive layer provides immediate geospatial visibility into emerging or underserved operational sectors across the expanding zones of the city.