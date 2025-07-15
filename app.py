import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.set_page_config(page_title="CSV Cleaner, Sorter & Visualizer", layout="wide")
sns.set_theme(style="whitegrid")

st.title("CSV Cleaner, Sorter & Visualizer")

file = st.file_uploader("Upload your CSV file", type=["csv"])

if file:
    try:
        df = pd.read_csv(file)
        st.success("CSV loaded successfully.")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

    st.subheader("Raw Data Preview")
    st.dataframe(df, use_container_width=True)

    st.subheader("Data Cleaning")
    df.dropna(axis=1, how='all', inplace=True)
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()

    missing_option = st.radio(
        "Handle missing values by:",
        ["Drop rows with missing values", "Fill missing with 0", "Fill missing with column mean"]
    )
    if missing_option == "Drop rows with missing values":
        df_clean = df.dropna()
    elif missing_option == "Fill missing with 0":
        df_clean = df.fillna(0)
    elif missing_option == "Fill missing with column mean":
        df_clean = df.fillna(df.mean(numeric_only=True))

    st.success("Data cleaned successfully.")
    st.subheader("Cleaned Data Preview")
    st.dataframe(df_clean, use_container_width=True)

    st.subheader("Sorting Options")
    sort_col = st.selectbox("Select column to sort by:", df_clean.columns)
    sort_order = st.radio("Sort order:", ["Ascending", "Descending"], horizontal=True)
    df_sorted = df_clean.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))
    st.subheader("Sorted Data")
    st.dataframe(df_sorted, use_container_width=True)

    csv_download = df_sorted.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned & Sorted CSV",
        data=csv_download,
        file_name="cleaned_sorted_data.csv",
        mime="text/csv"
    )

    st.subheader("Visualization Options")
    numeric_cols = df_sorted.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_cols) > 0:
        graph_type = st.selectbox("Select graph type:", ["Line", "Bar", "Scatter"])

        x_col = st.selectbox("Select X-axis column:", df_sorted.columns)
        y_col = st.selectbox("Select Y-axis column:", numeric_cols)
        color = st.color_picker("Pick a color", "#1f77b4")
        marker_size = st.slider("Marker size", 5, 20, 8)
        alpha = st.slider("Transparency (alpha)", 0.1, 1.0, 0.8)
        rotate_angle = st.slider("X-axis label rotation angle", 0, 90, 45)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Replace categorical x-axis with numeric references
        if df_sorted[x_col].dtype == 'object' or df_sorted[x_col].dtype.name == 'category':
            unique_vals = df_sorted[x_col].unique()
            mapping_dict = {name: idx + 1 for idx, name in enumerate(unique_vals)}
            df_sorted['x_numeric'] = df_sorted[x_col].map(mapping_dict)

            # Display reference table
            ref_df = pd.DataFrame(list(mapping_dict.items()), columns=[x_col, 'Reference_Number'])
            st.subheader("Reference Table for X-axis Labels")
            st.dataframe(ref_df)

            x_data = df_sorted['x_numeric']
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            ax.set_xticks(list(mapping_dict.values()))
            ax.set_xticklabels(list(mapping_dict.values()), rotation=rotate_angle, fontsize=8)
            xlabel_display = f"{x_col} (Number Reference)"
        else:
            x_data = df_sorted[x_col]
            xlabel_display = x_col

        # Plot based on graph type
        if graph_type == "Scatter":
            sns.scatterplot(
                x=x_data,
                y=df_sorted[y_col],
                ax=ax,
                color=color,
                s=marker_size * 5,
                alpha=alpha
            )
        elif graph_type == "Bar":
            sns.barplot(
                x=x_data,
                y=df_sorted[y_col],
                ax=ax,
                color=color,
                alpha=alpha
            )
        elif graph_type == "Line":
            sns.lineplot(
                x=x_data,
                y=df_sorted[y_col],
                marker="o",
                markersize=marker_size,
                ax=ax,
                color=color,
                alpha=alpha
            )

        ax.set_xlabel(xlabel_display, fontsize=14)
        ax.set_ylabel(y_col, fontsize=14)
        ax.grid(True)

        st.pyplot(fig)

    else:
        st.info("No numeric columns available for visualization in this CSV.")

else:
    st.info("Please upload a CSV file to proceed.")
