# 📍 Saihat Market Data Project

A comprehensive web scraping and data pipeline project designed to collect, clean, and analyze business directory data for **Saihat City** (Eastern Province, Saudi Arabia) using **Playwright** and **Pandas**.

---

## 🚀 Project Overview
This project automates the extraction of localized business data across **30 different commercial and industrial categories**. It includes a smart geo-filtering mechanism to ensure 100% data accuracy for the target locality.

### ⚙️ System Workflow
1. **Data Collection:** Automated infinite scrolling and dynamic link extraction using `Playwright`.
2. **Smart Filtering:** Instant validation of business location (Saihat filter).
3. **Data Pipeline:** Cleaning, deduplication, and parsing into a unified CSV format.

---

## 📂 Repository Structure
* 📄 `scraperCode.py` — The core asynchronous web scraper script.
* 📊 `saihat_google_maps_dataset.csv` — The raw initial dataset collected.
* 🛠️ `data_cleaning.py` — *(Next Step)* Script for data cleaning and exploration.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Automation:** Playwright (Chromium Async)
* **Data Manipulation:** Pandas & Regex
