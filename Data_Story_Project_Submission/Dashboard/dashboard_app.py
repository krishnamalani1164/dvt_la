"""
NYC Airbnb Interactive Dashboard
--------------------------------
A Streamlit-based interactive dashboard for exploring the New York City
Airbnb Open Data (2019). This dashboard provides multiple views into the
data: geographic mapping, pricing analysis, host insights, and neighbourhood
comparisons.

Usage:
    streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="NYC Airbnb Data Explorer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Custom Styling
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Overall theme adjustments */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .stMetric label {
        color: rgba(255,255,255,0.85) !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-weight: 700;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    h2 {
        color: #34495e;
    }
    h3 {
        color: #7f8c8d;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Colour Palette (consistent with the notebook)
# -------------------------------------------------------------------
BOROUGH_COLORS = {
    'Manhattan': '#3498db',
    'Brooklyn': '#e74c3c',
    'Queens': '#2ecc71',
    'Bronx': '#f39c12',
    'Staten Island': '#9b59b6'
}

ROOM_COLORS = {
    'Entire home/apt': '#3498db',
    'Private room': '#2ecc71',
    'Shared room': '#f39c12'
}


# -------------------------------------------------------------------
# Data Loading
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load and prepare the Airbnb dataset."""
    df = pd.read_csv('../archive/AB_NYC_2019.csv')

    # Basic cleaning (mirrors the notebook)
    df['name'] = df['name'].fillna('Unnamed Listing')
    df['host_name'] = df['host_name'].fillna('Unknown Host')
    df['reviews_per_month'] = df['reviews_per_month'].fillna(0)
    df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

    # Remove zero-price and extreme minimum_nights
    df = df[df['price'] > 0]
    df = df[df['minimum_nights'] <= 365]

    # Feature engineering
    price_bins = [0, 50, 100, 200, 500, 10001]
    price_labels = ['Budget ($0-50)', 'Economy ($51-100)', 'Mid-Range ($101-200)',
                    'Premium ($201-500)', 'Luxury ($500+)']
    df['price_category'] = pd.cut(df['price'], bins=price_bins, labels=price_labels, right=True)

    df['estimated_annual_revenue'] = df['reviews_per_month'] * 12 * 2 * df['price'] * 3

    df['host_type'] = df['calculated_host_listings_count'].apply(
        lambda x: 'Individual (1)' if x == 1
        else 'Small Portfolio (2-5)' if x <= 5
        else 'Professional (6+)'
    )

    return df


df = load_data()

# -------------------------------------------------------------------
# Sidebar Filters
# -------------------------------------------------------------------
st.sidebar.title("Filter Controls")
st.sidebar.markdown("Use these controls to narrow the data shown across all dashboard panels.")

# Borough filter
selected_boroughs = st.sidebar.multiselect(
    "Boroughs",
    options=sorted(df['neighbourhood_group'].unique()),
    default=sorted(df['neighbourhood_group'].unique())
)

# Room type filter
selected_rooms = st.sidebar.multiselect(
    "Room Types",
    options=sorted(df['room_type'].unique()),
    default=sorted(df['room_type'].unique())
)

# Price range filter
price_min, price_max = st.sidebar.slider(
    "Price Range ($/night)",
    min_value=int(df['price'].min()),
    max_value=min(int(df['price'].max()), 1000),
    value=(0, 500),
    step=10
)

# Minimum nights filter
min_nights_cap = st.sidebar.slider(
    "Maximum Minimum-Nights",
    min_value=1,
    max_value=60,
    value=30,
    step=1
)

# Apply filters
filtered_df = df[
    (df['neighbourhood_group'].isin(selected_boroughs)) &
    (df['room_type'].isin(selected_rooms)) &
    (df['price'] >= price_min) &
    (df['price'] <= price_max) &
    (df['minimum_nights'] <= min_nights_cap)
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} listings**")

# -------------------------------------------------------------------
# Main Dashboard
# -------------------------------------------------------------------
st.title("New York City Airbnb Data Explorer")
st.markdown(
    "An interactive dashboard for analysing ~49,000 Airbnb listings across "
    "the five NYC boroughs. Use the sidebar filters to focus on specific "
    "segments of the market."
)

# -------------------------------------------------------------------
# Key Metrics Row
# -------------------------------------------------------------------
st.markdown("### Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Listings", f"{len(filtered_df):,}")
with col2:
    st.metric("Median Price", f"${filtered_df['price'].median():,.0f}")
with col3:
    st.metric("Avg. Reviews", f"{filtered_df['number_of_reviews'].mean():,.1f}")
with col4:
    unique_hosts = filtered_df['host_id'].nunique()
    st.metric("Unique Hosts", f"{unique_hosts:,}")
with col5:
    avg_avail = filtered_df['availability_365'].mean()
    st.metric("Avg. Availability", f"{avg_avail:,.0f} days")

st.markdown("---")

# -------------------------------------------------------------------
# Tab Layout for Different Views
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Geographic View", "Pricing Analysis", "Room Types",
    "Host Insights", "Neighbourhood Deep-Dive"
])

# ===================================================================
# TAB 1: Geographic View
# ===================================================================
with tab1:
    st.markdown("### Geographic Distribution of Listings")

    map_col, stat_col = st.columns([3, 1])

    with map_col:
        # Sample for map performance
        map_sample = filtered_df.sample(n=min(5000, len(filtered_df)), random_state=42)

        fig_map = px.scatter_mapbox(
            map_sample,
            lat='latitude',
            lon='longitude',
            color='neighbourhood_group',
            color_discrete_map=BOROUGH_COLORS,
            size='price',
            size_max=8,
            opacity=0.5,
            hover_name='name',
            hover_data={
                'price': ':$,.0f',
                'room_type': True,
                'neighbourhood': True,
                'latitude': False,
                'longitude': False,
                'neighbourhood_group': False
            },
            labels={'neighbourhood_group': 'Borough'},
            mapbox_style='carto-positron',
            zoom=10,
            center={'lat': 40.7128, 'lon': -74.0060},
            height=550
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with stat_col:
        st.markdown("**Listings by Borough**")
        borough_counts = filtered_df['neighbourhood_group'].value_counts()
        for borough, count in borough_counts.items():
            pct = count / len(filtered_df) * 100
            st.markdown(f"**{borough}**: {count:,} ({pct:.1f}%)")

    # Borough comparison bar chart
    st.markdown("### Borough Comparison")
    borough_stats = filtered_df.groupby('neighbourhood_group').agg(
        listings=('id', 'count'),
        median_price=('price', 'median'),
        avg_reviews=('number_of_reviews', 'mean'),
        avg_availability=('availability_365', 'mean')
    ).reset_index()

    fig_borough = make_subplots(rows=1, cols=3,
                                subplot_titles=['Listing Count', 'Median Price ($)', 'Avg Reviews'])

    for i, (col, fmt) in enumerate([
        ('listings', ',.0f'), ('median_price', '$,.0f'), ('avg_reviews', ',.1f')
    ]):
        fig_borough.add_trace(
            go.Bar(
                x=borough_stats['neighbourhood_group'],
                y=borough_stats[col],
                marker_color=[BOROUGH_COLORS.get(b, '#999') for b in borough_stats['neighbourhood_group']],
                text=[f'{v:{fmt}}' for v in borough_stats[col]],
                textposition='outside',
                showlegend=False
            ),
            row=1, col=i+1
        )

    fig_borough.update_layout(height=400, margin=dict(t=40, b=20))
    st.plotly_chart(fig_borough, use_container_width=True)


# ===================================================================
# TAB 2: Pricing Analysis
# ===================================================================
with tab2:
    st.markdown("### Price Distribution")

    price_col1, price_col2 = st.columns(2)

    with price_col1:
        fig_hist = px.histogram(
            filtered_df[filtered_df['price'] <= 500],
            x='price',
            nbins=60,
            color='neighbourhood_group',
            color_discrete_map=BOROUGH_COLORS,
            labels={'price': 'Price per Night ($)', 'neighbourhood_group': 'Borough'},
            title='Price Distribution by Borough',
            opacity=0.7,
            barmode='overlay'
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

    with price_col2:
        fig_box = px.box(
            filtered_df[filtered_df['price'] <= 500],
            x='neighbourhood_group',
            y='price',
            color='neighbourhood_group',
            color_discrete_map=BOROUGH_COLORS,
            labels={'price': 'Price ($)', 'neighbourhood_group': 'Borough'},
            title='Price Box Plot by Borough'
        )
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # Price heatmap: borough vs room type
    st.markdown("### Median Price: Borough vs Room Type")
    heatmap_data = filtered_df.groupby(
        ['neighbourhood_group', 'room_type']
    )['price'].median().unstack(fill_value=0)

    fig_heatmap = px.imshow(
        heatmap_data,
        text_auto=True,
        color_continuous_scale='YlOrRd',
        labels={'color': 'Median Price ($)'},
        title='Median Nightly Price by Borough and Room Type',
        aspect='auto'
    )
    fig_heatmap.update_layout(height=350)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Price category distribution
    st.markdown("### Price Category Breakdown")
    cat_counts = filtered_df['price_category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    cat_counts = cat_counts.sort_values('Category')

    fig_cat = px.bar(
        cat_counts, x='Category', y='Count',
        color='Category',
        color_discrete_sequence=['#27ae60', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'],
        title='Listings by Price Category',
        text='Count'
    )
    fig_cat.update_layout(height=400, showlegend=False)
    fig_cat.update_traces(textposition='outside')
    st.plotly_chart(fig_cat, use_container_width=True)


# ===================================================================
# TAB 3: Room Types
# ===================================================================
with tab3:
    st.markdown("### Room Type Analysis")

    rt_col1, rt_col2 = st.columns(2)

    with rt_col1:
        room_counts = filtered_df['room_type'].value_counts().reset_index()
        room_counts.columns = ['Room Type', 'Count']
        fig_pie = px.pie(
            room_counts, names='Room Type', values='Count',
            color='Room Type',
            color_discrete_map=ROOM_COLORS,
            title='Overall Room Type Distribution'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with rt_col2:
        room_borough = filtered_df.groupby(
            ['neighbourhood_group', 'room_type']
        ).size().reset_index(name='count')

        fig_stack = px.bar(
            room_borough,
            x='neighbourhood_group',
            y='count',
            color='room_type',
            color_discrete_map=ROOM_COLORS,
            labels={'count': 'Listings', 'neighbourhood_group': 'Borough', 'room_type': 'Room Type'},
            title='Room Type Composition by Borough',
            barmode='stack'
        )
        fig_stack.update_layout(height=400)
        st.plotly_chart(fig_stack, use_container_width=True)

    # Room type price comparison
    st.markdown("### Price by Room Type")
    fig_violin = px.violin(
        filtered_df[filtered_df['price'] <= 500],
        x='room_type',
        y='price',
        color='room_type',
        color_discrete_map=ROOM_COLORS,
        box=True,
        labels={'price': 'Price ($)', 'room_type': 'Room Type'},
        title='Price Distribution by Room Type'
    )
    fig_violin.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_violin, use_container_width=True)


# ===================================================================
# TAB 4: Host Insights
# ===================================================================
with tab4:
    st.markdown("### Host Market Concentration")

    host_col1, host_col2 = st.columns(2)

    with host_col1:
        host_type_counts = filtered_df['host_type'].value_counts().reset_index()
        host_type_counts.columns = ['Host Type', 'Listings']

        fig_host_pie = px.pie(
            host_type_counts, names='Host Type', values='Listings',
            title='Listings by Host Type',
            color='Host Type',
            color_discrete_map={
                'Individual (1)': '#27ae60',
                'Small Portfolio (2-5)': '#3498db',
                'Professional (6+)': '#e74c3c'
            }
        )
        fig_host_pie.update_layout(height=400)
        st.plotly_chart(fig_host_pie, use_container_width=True)

    with host_col2:
        # Unique hosts by type
        unique_by_type = filtered_df.groupby('host_type')['host_id'].nunique().reset_index()
        unique_by_type.columns = ['Host Type', 'Unique Hosts']

        fig_host_bar = px.bar(
            unique_by_type, x='Host Type', y='Unique Hosts',
            color='Host Type',
            color_discrete_map={
                'Individual (1)': '#27ae60',
                'Small Portfolio (2-5)': '#3498db',
                'Professional (6+)': '#e74c3c'
            },
            title='Number of Unique Hosts by Type',
            text='Unique Hosts'
        )
        fig_host_bar.update_layout(height=400, showlegend=False)
        fig_host_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_host_bar, use_container_width=True)

    # Top hosts table
    st.markdown("### Top 15 Hosts by Listing Count")
    top_hosts = filtered_df.groupby(['host_id', 'host_name']).agg(
        listings=('id', 'count'),
        avg_price=('price', 'mean'),
        total_reviews=('number_of_reviews', 'sum'),
        boroughs=('neighbourhood_group', lambda x: ', '.join(sorted(x.unique())))
    ).reset_index().sort_values('listings', ascending=False).head(15)

    top_hosts_display = top_hosts[['host_name', 'listings', 'avg_price', 'total_reviews', 'boroughs']].copy()
    top_hosts_display.columns = ['Host Name', 'Listings', 'Avg Price ($)', 'Total Reviews', 'Boroughs']
    top_hosts_display['Avg Price ($)'] = top_hosts_display['Avg Price ($)'].round(0)
    top_hosts_display = top_hosts_display.reset_index(drop=True)
    top_hosts_display.index += 1

    st.dataframe(top_hosts_display, use_container_width=True)


# ===================================================================
# TAB 5: Neighbourhood Deep-Dive
# ===================================================================
with tab5:
    st.markdown("### Neighbourhood Explorer")

    if len(selected_boroughs) == 0:
        st.warning("Please select at least one borough in the sidebar.")
    else:
        # Top neighbourhoods
        top_n = st.slider("Number of neighbourhoods to display", 10, 30, 15)

        top_hoods = filtered_df['neighbourhood'].value_counts().head(top_n).reset_index()
        top_hoods.columns = ['Neighbourhood', 'Listings']

        # Map neighbourhood to borough
        hood_to_borough = filtered_df[['neighbourhood', 'neighbourhood_group']].drop_duplicates()
        top_hoods = top_hoods.merge(hood_to_borough, left_on='Neighbourhood', right_on='neighbourhood', how='left')

        fig_hoods = px.bar(
            top_hoods, x='Listings', y='Neighbourhood',
            color='neighbourhood_group',
            color_discrete_map=BOROUGH_COLORS,
            orientation='h',
            labels={'neighbourhood_group': 'Borough'},
            title=f'Top {top_n} Neighbourhoods by Listing Count'
        )
        fig_hoods.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_hoods, use_container_width=True)

        # Treemap
        st.markdown("### Neighbourhood Treemap")
        treemap_data = filtered_df.groupby(['neighbourhood_group', 'neighbourhood']).agg(
            count=('id', 'count'),
            median_price=('price', 'median')
        ).reset_index()

        fig_tree = px.treemap(
            treemap_data,
            path=['neighbourhood_group', 'neighbourhood'],
            values='count',
            color='median_price',
            color_continuous_scale='YlOrRd',
            labels={'count': 'Listings', 'median_price': 'Median Price ($)'},
            title='Market Size and Pricing by Neighbourhood'
        )
        fig_tree.update_layout(height=550)
        st.plotly_chart(fig_tree, use_container_width=True)

        # Scatter: neighbourhood comparison
        st.markdown("### Neighbourhood Price vs Demand")
        hood_stats = filtered_df.groupby('neighbourhood').agg(
            listings=('id', 'count'),
            median_price=('price', 'median'),
            avg_reviews=('number_of_reviews', 'mean'),
            borough=('neighbourhood_group', 'first')
        ).reset_index()

        hood_stats = hood_stats[hood_stats['listings'] >= 10]  # at least 10 listings

        fig_scatter = px.scatter(
            hood_stats,
            x='median_price',
            y='avg_reviews',
            size='listings',
            color='borough',
            color_discrete_map=BOROUGH_COLORS,
            hover_name='neighbourhood',
            labels={
                'median_price': 'Median Price ($)',
                'avg_reviews': 'Avg Reviews per Listing',
                'listings': 'Total Listings',
                'borough': 'Borough'
            },
            title='Neighbourhood: Price vs Guest Engagement'
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)


# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#7f8c8d; font-size:0.85em;'>"
    "NYC Airbnb Data Explorer | Data Source: "
    "<a href='https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data'>Kaggle</a> | "
    "Built with Streamlit and Plotly"
    "</div>",
    unsafe_allow_html=True
)
