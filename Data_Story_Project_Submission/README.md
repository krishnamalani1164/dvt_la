# NYC Airbnb Data Story Project

## Project Overview

This project presents a comprehensive data story built around the **New York City Airbnb Open Data (2019)**, a public dataset from Kaggle containing approximately 49,000 short-term rental listings across all five NYC boroughs. The analysis integrates data visualisation principles, interactive dashboards, and storytelling techniques to deliver actionable insights for hosts, policy makers, and the Airbnb platform.

**Dataset:** [New York City Airbnb Open Data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)

---

## Project Structure

```
Data_Story_Project_Submission/
|
|-- Executive_Summary_Report.txt      Written data story with findings and recommendations
|-- Presentation_Deck.html            Stakeholder-ready slide deck (open in browser, print to PDF)
|
|-- Dashboard/
|   |-- dashboard_app.py              Streamlit interactive dashboard (5 tabs, sidebar filters)
|   |-- Live_Dashboard_Link.txt       Instructions to launch the dashboard
|
|-- Code_and_Data/
|   |-- Data_Cleaning_and_EDA.ipynb   Python notebook: cleaning, EDA, 15+ visualisations
|   |-- dataset_source_link.txt       Kaggle dataset source URL and column descriptions
|
|-- README.md                         This file
```

---

## Analytical Approach

### Data Cleaning

The raw dataset was cleaned through the following steps:

1. **Missing values** -- Listing names (16 records) and host names (21 records) were filled with placeholder values. The `reviews_per_month` field was set to 0 for the 10,052 listings that had never been reviewed.
2. **Invalid records** -- 11 listings with a price of $0 were removed as likely data entry errors.
3. **Extreme values** -- 53 listings with minimum night requirements exceeding 365 days were excluded, as these represent long-term leases rather than short-term rentals.
4. **Date parsing** -- The `last_review` column was converted to proper datetime format for temporal analysis.

### Feature Engineering

Three new features were created to support deeper analysis:

- **Price Category**: Budget ($0-50), Economy ($51-100), Mid-Range ($101-200), Premium ($201-500), Luxury ($500+)
- **Host Type**: Individual Host (1 listing), Small Portfolio (2-5 listings), Professional Host (6+ listings)
- **Estimated Annual Revenue**: Derived from review frequency, price, and average stay length using Airbnb's published review-to-booking ratio

### Analysis Dimensions

The exploratory analysis covers seven dimensions:

| Dimension | Questions Addressed |
|-----------|-------------------|
| Geographic Distribution | Where are listings concentrated? Which neighbourhoods dominate? |
| Pricing Dynamics | How do prices vary by borough, room type, and neighbourhood? |
| Room Type Composition | What types of spaces are offered? How does this vary by area? |
| Host Landscape | Who are the hosts? How concentrated is the market? |
| Review Patterns | What do review trends reveal about guest engagement? |
| Revenue Estimates | Which areas generate the most revenue? |
| Text Analysis | What themes emerge from listing names? |

---

## Key Findings

1. **Manhattan and Brooklyn dominate**, accounting for roughly 85% of all listings. Williamsburg, Bedford-Stuyvesant, and Harlem are the three densest neighbourhoods.

2. **The median nightly price is $106**, but the mean ($152) is pulled up by luxury outliers. About 50% of listings fall under $100/night, indicating a competitive budget market.

3. **Entire homes (52%) and private rooms (46%)** account for nearly all listings. Shared rooms are rare at 2.3%.

4. **Professional hosts (3% of all hosts)** control approximately 15% of listings, signalling meaningful market concentration.

5. **Review activity grew steadily through 2019**, peaking in summer months. Higher-priced listings tend to receive fewer reviews.

6. **Roughly 4-5% of listings** require 30+ night minimums, potentially circumventing short-term rental regulations.

---

## How to Use This Project

### Running the EDA Notebook

```bash
# Navigate to the Code_and_Data directory
cd Data_Story_Project_Submission/Code_and_Data/

# Open the notebook in Jupyter
jupyter notebook Data_Cleaning_and_EDA.ipynb
```

**Dependencies:**
```
pandas
numpy
matplotlib
seaborn
plotly
wordcloud
```

### Launching the Interactive Dashboard

```bash
# Navigate to the Dashboard directory
cd Data_Story_Project_Submission/Dashboard/

# Install Streamlit if not already installed
pip install streamlit

# Launch the dashboard
streamlit run dashboard_app.py
```

The dashboard will open at `http://localhost:8501` and provides:
- Geographic mapping of all listings
- Price distribution analysis with interactive filters
- Room type breakdowns
- Host concentration insights
- Neighbourhood deep-dive with treemaps and scatter plots

### Viewing the Presentation Deck

Open `Presentation_Deck.html` in any web browser. To create a PDF:
1. Open the file in Chrome or Firefox
2. Press Ctrl+P (or Cmd+P on Mac)
3. Select "Save as PDF" as the destination
4. Set margins to "None" for best results

---

## Tools and Technologies

| Component | Tool |
|-----------|------|
| Data Cleaning and EDA | Python (Pandas, NumPy) |
| Static Visualisations | Matplotlib, Seaborn |
| Interactive Visualisations | Plotly |
| Dashboard | Streamlit |
| Text Analysis | WordCloud |
| Presentation | HTML/CSS |
| Report | Plain text (convertible to PDF) |

---

## Dataset Details

- **Source:** Kaggle -- New York City Airbnb Open Data
- **URL:** https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data
- **Records:** 48,895 listings
- **Columns:** 16 (id, name, host_id, host_name, neighbourhood_group, neighbourhood, latitude, longitude, room_type, price, minimum_nights, number_of_reviews, last_review, reviews_per_month, calculated_host_listings_count, availability_365)
- **Time Period:** 2019 snapshot

---

## Author

Data Story Project -- Comprehensive Analysis and Visualisation
September 2026
