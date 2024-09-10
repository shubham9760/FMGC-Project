import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# Streamlit app title
st.set_page_config(page_title="FMGC Product Orders Analysis", page_icon="📊", layout="wide")
st.title("FMGC Product Orders Analysis")

# Add GitHub icon with link to the top right
st.markdown(
    """
    <style>
    .github-link {
        position: absolute;
        right: 20px;
        top: 10px;
        text-decoration: none;
    }
    .github-link:hover {
        opacity: 0.8;
    }
    .github-link img {
        width: 32px;
    }
    </style>
    <a href="https://github.com/yourusername/yourrepository" class="github-link">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub Link">
    </a>
    """, 
    unsafe_allow_html=True
)

# Load DataFrames from pickle files
df_dim_customer = pd.read_pickle(r"df_dim_customer.pkl")
df_dim_date = pd.read_pickle(r"df_dim_date.pkl")
df_dim_products = pd.read_pickle(r"df_dim_products.pkl")
df_dim_targets_orders = pd.read_pickle(r"df_dim_targets_orders.pkl")
df_fact_order_lines = pd.read_pickle(r"df_fact_order_lines.pkl")


# Data preprocessing
df_fact_order_lines['order_placement_date'] = pd.to_datetime(df_fact_order_lines['order_placement_date'], errors='coerce')
df_dim_date['date'] = pd.to_datetime(df_dim_date['date'], errors='coerce')

# Merge DataFrames
df_fact_order_lines = df_fact_order_lines.merge(df_dim_targets_orders, on="customer_id", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_products, on="product_id", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_date, left_on="order_placement_date", right_on="date", how="left")
df_fact_order_lines = df_fact_order_lines.merge(df_dim_customer, on="customer_id", how="left")

# Rename columns if necessary
df_fact_order_lines.rename(columns={"wrong_name": "customer_id"}, inplace=True)
df_dim_targets_orders.rename(columns={"wrong_name": "customer_id"}, inplace=True)

# Create 'month' column from 'order_placement_date'
df_fact_order_lines["month"] = df_fact_order_lines["order_placement_date"].dt.month_name()

# Sidebar options
st.sidebar.header("Navigation")
st.sidebar.markdown(
    """
    Use the sidebar to navigate through different views of the FMGC product orders data. 
    Select a view and choose how you would like to visualize the data.
    """
)
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
    grouped_orders_by_city = df_fact_order_lines.groupby("city")[["In Full", "On Time", "On Time In Full"]].sum()
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(14, 6))
        grouped_orders_by_city.plot(kind="bar", ax=ax, color=sns.color_palette("husl", 3))
        ax.set_title("Orders by City", fontsize=18, weight='bold')
        ax.set_xlabel("City", fontsize=14)
        ax.set_ylabel("Count", fontsize=14)
        add_bar_labels(ax)
        st.pyplot(fig)
    else:
        st.write("This table shows the orders by city.")
        st.dataframe(grouped_orders_by_city.style.set_properties(**{'text-align': 'left'}).background_gradient(cmap='Blues').set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('font-weight', 'bold')]}]
        ))

elif option == "Target by City":
    st.header("Target by City")
    df_city_targets = df_fact_order_lines.groupby("city")[["ontime_target%", "otif_target%"]].mean().round(2)
    if view_type == "Chart":
        fig_target_city = px.bar(df_city_targets, title="Target by City", labels={"value": "Percentage", "index": "City"}, color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_target_city.update_layout(title_text='Target by City', title_x=0.5, title_font_size=18)
        st.plotly_chart(fig_target_city)
    else:
        st.write("This table shows the target by city.")
        st.dataframe(df_city_targets.style.set_properties(**{'text-align': 'left'}).background_gradient(cmap='Greens').set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('font-weight', 'bold')]}]
        ))

elif option == "Quantity by Customer":
    st.header("Quantity by Customer")
    df_customer_quantity = df_fact_order_lines.groupby("customer_name")[["order_qty"]].sum().sort_values(by="order_qty", ascending=False)
    if view_type == "Chart":
        fig_customer_quantity = px.bar(df_customer_quantity, log_y=True, title="Quantity by Customer", labels={"order_qty": "Quantity", "customer_name": "Customer"}, color_discrete_sequence=px.colors.sequential.Viridis)
        fig_customer_quantity.update_layout(title_text='Quantity by Customer', title_x=0.5, title_font_size=18)
        st.plotly_chart(fig_customer_quantity)
    else:
        st.write("This table shows the quantity ordered by each customer.")
        st.dataframe(df_customer_quantity.style.set_properties(**{'text-align': 'left'}).background_gradient(cmap='Purples').set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('font-weight', 'bold')]}]
        ))

elif option == "Quantity by Category":
    st.header("Quantity by Category")
    grouped_quantity_by_category = df_fact_order_lines.groupby("category")[["order_qty", "delivery_qty"]].sum()
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(14, 6))
        grouped_quantity_by_category.plot(kind="bar", ax=ax, color=sns.color_palette("viridis", 2))
        ax.set_title("Quantity by Category", fontsize=18, weight='bold')
        ax.set_xlabel("Category", fontsize=14)
        ax.set_ylabel("Quantity", fontsize=14)
        add_bar_labels(ax)
        st.pyplot(fig)
    else:
        st.write("This table shows the quantity by category.")
        st.dataframe(grouped_quantity_by_category.style.set_properties(**{'text-align': 'left'}).background_gradient(cmap='Oranges').set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('font-weight', 'bold')]}]
        ))

elif option == "On-time vs In-full Delivery by City":
    st.header("On-time vs In-full Delivery by City")
    if view_type == "Chart":
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.scatterplot(x="On Time", y="In Full", hue="city", data=df_fact_order_lines, ax=ax, palette='tab10')
        ax.set_title("On-time vs In-full Delivery by City", fontsize=18, weight='bold')
        ax.set_xlabel("On Time", fontsize=14)
        ax.set_ylabel("In Full", fontsize=14)
        st.pyplot(fig)
    else:
        st.write("This table shows the on-time vs in-full delivery by city.")
        st.dataframe(df_fact_order_lines.groupby("city")[["On Time", "In Full"]].sum().style.set_properties(**{'text-align': 'left'}).background_gradient(cmap='Reds').set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#f1f1f1'), ('font-weight', 'bold')]}]
        ))

# Add custom CSS to style the sidebar
st.markdown(
    """
    <style>
    .css-1d391kg {background-color: #f1f1f1; padding: 20px;}
    .css-1d391kg h1 {color: #333;}
    .css-1d391kg .css-1t8l2s6 {color: #333;}
    .css-1d391kg .css-1n6wz7b {border-color: #ddd;}
    .css-1n6wz7b input {border-color: #ddd;}
    .css-1d391kg .css-1n6wz7b .stButton {color: #333;}
    </style>
    """,
    unsafe_allow_html=True
)