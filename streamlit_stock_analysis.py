import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt

# MySQL connection setup
engine = create_engine("mysql+pymysql://root:root@localhost:3306/stock_analysis_db")

# Page title
st.title("📊 Stock Market Analysis Dashboard")

# Sidebar navigation
option = st.sidebar.selectbox(
    "Select Analysis View",
    ("Cumulative Return", "Volatility", "Sector-wise Performance", "Correlation", "Top 5 Gainers & Losers2")
)

# Load data functions
@st.cache_data
def load_data(table_name):
    return pd.read_sql(f"SELECT * FROM {table_name}", con=engine)

# Views
if option == "Cumulative Return":
    # ✅ Load all cumulative return data
    df = load_data("cumulative_return_overtime")
    df["date"] = pd.to_datetime(df["date"])
    st.subheader("📈 Cumulative Return Over Time")
    st.line_chart(df.set_index("date")[["cumulative_return"]])

    # ✅ Optional: Top 5 Cumulative Return Plot
    st.subheader("🔥 Cumulative Return of Top 5 Performing Stocks")

    # ✅ Group by 'Stock Symbol'
    cumulative_returns_dict = {
        symbol: group.sort_values("date") for symbol, group in df.groupby("Stock Symbol")  # Changed 'symbol' to 'Stock Symbol'
    }

    # ✅ Calculate last return per symbol
    last_cumulative_returns = {
        symbol: df_["cumulative_return"].iloc[-1]
        for symbol, df_ in cumulative_returns_dict.items()
    }

    # ✅ Get top 5 symbols
    top_5 = sorted(last_cumulative_returns.items(), key=lambda x: x[1], reverse=True)[:5]

    # ✅ Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    for symbol, _ in top_5:
        plot_df = cumulative_returns_dict[symbol]
        ax.plot(plot_df["date"], plot_df["cumulative_return"], label=symbol)

    ax.set_title("Cumulative Return for Top 5 Performing Stocks")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.grid(True)
    ax.legend(title="Stock Symbols")
    fig.tight_layout()

    st.pyplot(fig)

    

elif option == "Volatility":
    df = load_data("volatility_analysis")

    st.subheader("📉 Volatility Analysis")

    # ✅ Clean column names if needed
    df.columns = [col.strip() for col in df.columns]

    # ✅ Top 10 Most Volatile Stocks
    top_10 = df.sort_values(by='Volatility', ascending=False).head(10)

    # ✅ Plot using matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(top_10['Stock Symbol'], top_10['Volatility'], color='skyblue', edgecolor='black')
    ax.set_title("Top 10 Most Volatile Stocks (1-Year Volatility)")
    ax.set_xlabel("Stock Symbol")
    ax.set_ylabel("Volatility (Std Dev of Daily Returns)")
    ax.set_xticklabels(top_10['Stock Symbol'], rotation=45)
    ax.grid(axis='y')
    fig.tight_layout()

    st.pyplot(fig)

elif option == "Sector-wise Performance":
    df = load_data("sector_wise_performance")
    
    # ✅ Clean column names
    df.columns = df.columns.str.strip().str.lower()

    st.subheader("🏢 Sector-wise Performance")

    # ✅ Check required columns
    if not {"sector", "avg_yearly_return"}.issubset(df.columns):
        st.error("❌ Required columns missing in the dataset.")
        st.write("Available columns:", df.columns.tolist())
    else:
        # ✅ Create bar plot using Seaborn
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(data=df, x="sector", y="avg_yearly_return", ax=ax, color='skyblue', edgecolor='black')
        
        ax.set_title("Average Yearly Return by Sector")
        ax.set_xlabel("Sector")
        ax.set_ylabel("Average Yearly Return")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        st.pyplot(fig)


elif option == "Correlation":
    df = load_data("correlation_analysis")
    st.subheader("🔗 Correlation Heatmap")
    numeric_df = df.select_dtypes(include="number")
    correlation_matrix = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(20, 16))  # create a Matplotlib figure
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap='coolwarm',
        fmt='.2f',
        linewidths=0.5,
        cbar=True,
        ax=ax
    )

    ax.set_title("📊 Stock Price Correlation Heatmap", fontsize=16)
    ax.set_xlabel("Stocks", fontsize=12)
    ax.set_ylabel("Stocks", fontsize=12)

    # Display in Streamlit
    st.pyplot(fig)

elif option == "Top 5 Gainers & Losers2":
    df = load_data("top_5_gainers_and_losers2")

    st.subheader("🚀 Top 5 Gainers and 📉 Losers by Month")
    df.columns = [col.strip() for col in df.columns]  # Clean column names

    month_list = sorted(df["month"].unique())
    selected_month = st.selectbox("Select Month", month_list)

    filtered = df[df["month"] == selected_month]
    filtered = filtered.sort_values("monthly_return", ascending=True)

    # 🎨 Plot with seaborn for better styling
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        x="monthly_return",
        y="symbol",
        hue="type",
        data=filtered,
        dodge=False,
        palette={"Gainer": "green", "Loser": "red"},
        ax=ax
    )

    ax.set_title(f"Top 5 Gainers and Losers2 - {selected_month}")
    ax.set_xlabel("Monthly Return")
    ax.set_ylabel("Stock Symbol")
    ax.axvline(0, color='gray', linestyle='--')
    ax.legend(title="Type")
    plt.tight_layout()

    st.pyplot(fig)
