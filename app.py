import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="NYC Airbnb", layout="wide")
st.title("NYC Airbnb Dashboard")

@st.cache_data
def load():
    return pd.read_csv("data/clean.csv")

df = load()

st.sidebar.header("Filters")
boroughs = st.sidebar.multiselect(
    "Borough", sorted(df["neighbourhood_group"].unique()),
    default=sorted(df["neighbourhood_group"].unique()))
rooms = st.sidebar.multiselect(
    "Room type", sorted(df["room_type"].unique()),
    default=sorted(df["room_type"].unique()))
pmin, pmax = int(df["price"].min()), int(df["price"].max())
price = st.sidebar.slider("Price (USD)", pmin, pmax, (pmin, pmax))
nights = st.sidebar.slider("Max minimum nights", 1, 365, 365)

f = df[
    df["neighbourhood_group"].isin(boroughs)
    & df["room_type"].isin(rooms)
    & df["price"].between(price[0], price[1])
    & (df["minimum_nights"] <= nights)
].copy()

if f.empty:
    st.warning("No listings match the filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(f):,}")
c2.metric("Median price", f"${f['price'].median():.0f}")
c3.metric("Avg availability (days)", f"{f['availability_365'].mean():.0f}")
c4.metric("Avg reviews / month", f"{f['reviews_per_month'].mean():.2f}")

a, b = st.columns(2)
with a:
    d = f.groupby("neighbourhood_group")["price"].median().reset_index()
    st.plotly_chart(px.bar(d, x="neighbourhood_group", y="price",
        title="Median Price by Borough",
        labels={"neighbourhood_group": "Borough", "price": "Median price (USD)"}),
        use_container_width=True)
with b:
    d = f.groupby("room_type")["price"].median().reset_index()
    st.plotly_chart(px.bar(d, x="room_type", y="price",
        title="Median Price by Room Type",
        labels={"room_type": "Room type", "price": "Median price (USD)"}),
        use_container_width=True)

f["min_group"] = pd.cut(f["minimum_nights"], [0, 1, 3, 7, 30, 1500],
                        labels=["1", "2-3", "4-7", "8-30", "30+"])
d = f.groupby("min_group", observed=True)["reviews_per_month"].mean().reset_index()
st.plotly_chart(px.bar(d, x="min_group", y="reviews_per_month",
    title="Avg Reviews per Month by Minimum Nights",
    labels={"min_group": "Minimum nights", "reviews_per_month": "Reviews per month"}),
    use_container_width=True)
