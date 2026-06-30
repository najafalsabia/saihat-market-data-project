# 📍 Saihat Geospatial Market Data Pipeline

A comprehensive data engineering and geospatial analysis project designed to collect, clean, and visualize establishment and business directory data for **Saihat City** (Eastern Province, Saudi Arabia) using **Playwright** and **Pandas**.

---

## 🚀 Project Overview
This project automates the extraction of localized data across **60 different commercial, municipal, and infrastructural categories** using a distributed parallel approach between team members to optimize execution time. The finalized pipeline translates high-purity cleaned data into interactive geospatial maps.

### ⚙️ System Workflow
1. **Data Collection & Smart Filtering:** Automated dynamic scrolling and link extraction using an asynchronous `Playwright` scraper running across distributed nodes, featuring on-the-fly validation to isolate records strictly within the geographic boundaries of Saihat during this initial extraction.
2. **Iterative Re-scraping:** A secondary targeted pipeline to capture full 7-day schedules and extract consumer engagement metrics (`reviews_count`).
3. **Data Preprocessing:** Two-phase de-duplication, Saudi phone type categorization (`phone_type`), float-to-string type cast correction, and 100% manual geospatial coordinate imputation for missing data (16 missing pairs resolved).
4. **Geospatial Insights:** Processing the engineered spatial metrics to render interactive HTML maps featuring automatic marker clustering, thematic sector color-coding, and rich metadata popups.

---

## 📂 Repository Structure
* 📁 `google-maps-scraper/` — Core folder containing the main scraper components.
* 📄 `scraperCode.py` — The core asynchronous web scraper script (Initial phase with smart filtering).
* 📄 `update_opening_times.py` — Secondary targeted scraper for retrieving full 7-day schedules and reviews.
* 📄 `integration.py` — Script executed to integrate components or manage the pipeline flow.
* 🛠️ `Data_Cleaning.ipynb` — Jupyter Notebook detailing the data engineering, transformation, and cleaning logic.
* 🛠️ `geographical_analysis.ipynb` — Jupyter Notebook dedicated to processing coordinates and generating visual spatial maps.
* 🗺️ `locations_map.html` — Generated interactive geospatial marker map with dynamic clustering.
* 🗺️ `coverage_map.html` — Generated analytical geospatial layout map evaluating localized sector densities.
* 📊 **Dataset Files (`.csv`):**
  * `saihat_google_maps_dataset1.csv` & `saihat_google_maps_dataset2.csv` — Raw partial data from both execution nodes.
  * `saihat_google_maps_merged.csv` — The initial compiled raw dataset combining both nodes.
  * `saihat_google_maps_deduplicated.csv` — Dataset state after completing initial de-duplication phases.
  * `saihat_google_maps_updated.csv` — The finalized, high-purity production dataset ready for analytical mapping.
* 📄 `Documentation.md` — Comprehensive academic and technical lifecycle report.
* 📄 `README.md` — Short summary and repository overview guide.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Automation & Concurrency:** Playwright (Chromium Async) & Asyncio
* **Data Manipulation:** Pandas & Regular Expressions (Regex)
* **Geospatial Visualization:** Folium (Leaflet.js)
