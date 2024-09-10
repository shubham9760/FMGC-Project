import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# Streamlit app title
st.title("FMGC Product Orders Analysis")

df_dim_customer = pd.read_pickle(r"dataframes/df_dim_customer.pkl")

# Fetch remaining tables
df_dim_date = pd.read_pickle(r"dataframes/df_dim_date.pkl")
df_dim_products = pd.read_pickle(r"dataframes/df_dim_products.pkl")
df_dim_targets_orders = pd.read_pickle(r"dataframes/df_dim_targets_orders.pkl")
df_fact_order_lines = pd.read_pickle(r"dataframes/df_fact_order_lines.pkl")

# Data preprocessing
df_fact_order_lines['order_placement_date'] = pd.to_datetime(df_fact_order_lines['order_placement_date'], errors='coerce')
df_dim_date['date'] = pd.to_datetime(df_dim_date['date'], errors='coerce')

# Merge DataFrames
df_fact_order_lines = df_fact_order_lines.merge(df_dim_targets_orders, on="customer_id", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_products, on="product_id", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_date, left_on="order_placement_date", right_on="date", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_customer, on="customer_id", how="left")

# Create 'month' column from 'order_placement_date'
df_fact_order_lines["month"] = df_fact_order_lines["order_placement_date"].dt.month_name()

# Sidebar options
st.sidebar.title("Select a View")
option = st.sidebar.selectbox(
    "Choose a view",
    [
        "Orders by City",
        "Target by City",
        "Quantity by Customer",
        "Quantity by Category",
        "On-time vs In-full Delivery by City"
    ]
)

view_type = st.sidebar.radio("View Type", ["Chart", "Table"])

def add_bar_labels(ax):
    """Add labels on top of bars in a plot."""
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 5), 
                    textcoords='offset points')

# Display selected option
if option == "Orders by City":
    st.header("Orders by City")
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(10, 3))
        df_fact_order_lines.groupby("city")[["In Full", "On Time", "On Time In Full"]].sum().plot(kind="bar", ax=ax)
        ax.set_title("Orders by City")
        add_bar_labels(ax)
        st.pyplot(fig)
    else:
        st.write("This table shows the orders by city.")
        st.dataframe(df_fact_order_lines.groupby("city")[["In Full", "On Time", "On Time In Full"]].sum())

elif option == "Target by City":
    st.header("Target by City")
    df_city_pct = df_fact_order_lines.groupby("city")[["ontime_target%", "otif_target%"]].mean().round(2)
    if view_type == "Chart":
        fig_target_city = px.bar(df_city_pct, title="Target by City", labels={"value": "Percentage", "index": "City"})
        st.plotly_chart(fig_target_city)
    else:
        st.write("This table shows the target by city.")
        st.dataframe(df_city_pct)

elif option == "Quantity by Customer":
    st.header("Quantity by Customer")
    df_customer_qty = df_fact_order_lines.groupby("customer_name")[["order_qty"]].sum().sort_values(by="order_qty", ascending=False)
    if view_type == "Chart":
        fig_customer_qty = px.bar(df_customer_qty, log_y=True, title="Quantity by Customer", labels={"order_qty": "Quantity", "customer_name": "Customer"})
        st.plotly_chart(fig_customer_qty)
    else:
        st.write("This table shows the quantity ordered by each customer.")
        st.dataframe(df_customer_qty)

elif option == "Quantity by Category":
    st.header("Quantity by Category")
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(10, 4))
        df_fact_order_lines.groupby("category")[["order_qty", "delivery_qty"]].sum().plot(kind="bar", ax=ax)
        ax.set_title("Quantity by Category")
        add_bar_labels(ax)
        st.pyplot(fig)
    else:
        st.write("This table shows the quantity by category.")
        st.dataframe(df_fact_order_lines.groupby("category")[["order_qty", "delivery_qty"]].sum())

elif option == "On-time vs In-full Delivery by City":
    st.header("On-time vs In-full Delivery by City")
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(x="On Time", y="In Full", hue="city", data=df_fact_order_lines, ax=ax)
        ax.set_title("On-time vs In-full Delivery by City")
        st.pyplot(fig)
    else:
        st.write("This table shows the on-time vs in-full delivery by city.")
        st.dataframe(df_fact_order_lines.groupby("city")[["On Time", "In Full"]].sum())