# coding=utf-8
# import libraries
import requests
import base64
import pandas as pd
import streamlit as st
import os
import math
import warnings
import numpy as np
from unidecode import unidecode
from sklearn.ensemble import IsolationForest
from rich.console import Console
from pathlib import Path
import shutil

warnings.simplefilter("ignore")
console = Console()

# variables
all_name = "All"
photo_profile_dir = Path("profile_photo")
static_dir = Path("static")
max_k = 10

if photo_profile_dir.exists():
    shutil.rmtree(photo_profile_dir)

photo_profile_dir.mkdir()

# load data

st.set_page_config(
    page_title="Outlier Detector",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("data/sofifa2020.csv")
    df["name"] = df["name"].apply(lambda name: unidecode(name))
    df["contract"] = df["contract"].apply(
        lambda x: int(x) if not math.isnan(x) else 2020
    )
    df["player_hashtags"] = (
        df["player_traits"].apply(
            lambda x: ", ".join([c.replace("(AI)", "").strip() for c in eval(x)])
        )
        + ", "
        + df["player_hashtags"].apply(
            lambda x: ", ".join([c.replace("#", "").strip() for c in eval(x)])
        )
    )

    df["player_hashtags"] = df["player_hashtags"].apply(lambda row: row.rstrip(", "))
    return df


df = load_data()
league_list = list(df["league"].unique())
player_list = list(df["name"].unique())

default_leagues = [
    "Spain Primera Division",
    "Italian Serie A",
    "French Ligue 1",
    "English Premier League",
    "German 1. Bundesliga",
    "Holland Eredivisie",
    "Portuguese Liga ZON SAGRES",
]

default_positions = ["ST", "CF", "LF", "RF", "LS", "RS"]

positions_list = [
    "LW",
    "LS",
    "ST",
    "RW",
    "RS",
    "LF",
    "CF",
    "RF",
    "CAM",
    "LM",
    "CM",
    "RM",
    "CDM",
    "LWB",
    "LB",
    "CB",
    "RB",
    "RWB",
    "GK",
]

show_columns = [
    "photo_url",
    "name",
    "teams",
    "league",
    "age",
    "positions",
    "Overall Rating",
    "Potential",
    "contract",
    "Value",
    "player_hashtags",
]

possible_columns_to_compare = [
    "Overall Rating",
    "Potential",
    "Crossing",
    "Finishing",
    "HeadingAccuracy",
    "ShortPassing",
    "Volleys",
    "Dribbling",
    "Curve",
    "FKAccuracy",
    "LongPassing",
    "BallControl",
    "Acceleration",
    "SprintSpeed",
    "Agility",
    "Reactions",
    "Balance",
    "ShotPower",
    "Jumping",
    "Stamina",
    "Strength",
    "LongShots",
    "Aggression",
    "Interceptions",
    "Positioning",
    "Vision",
    "Penalties",
    "Composure",
    "DefensiveAwareness",
    "StandingTackle",
    "SlidingTackle",
    "GKDiving",
    "GKHandling",
    "GKKicking",
    "GKPositioning",
    "GKReflexes",
]

################################################################
# css style
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

##################################################################
# sidebar filters
st.sidebar.title(":pick: Search Space Filters:")

leagues = st.sidebar.multiselect(
    "League:", [all_name] + league_list, default=default_leagues
)

positions = st.sidebar.multiselect(
    "Position:", positions_list, default=default_positions
)

age = st.sidebar.slider("Age:", min_value=15, max_value=50, value=24)

transfer_fee = 1000000 * float(
    st.sidebar.text_input("Maximum Transfer Fee (€M):", "100")
)
wage = 1000 * float(st.sidebar.text_input("Maximum Wage (€K):", "200"))

is_scan = st.sidebar.button("Detect")

st.sidebar.header("Contact Info")
st.sidebar.info("hadisotudeh1992[at]gmail.com")
st.sidebar.image(
    str(static_dir / "captain.jpg"),
    use_column_width=True,
)

##############################################################################
# if detect button is clicked, then show the main components of the dashboard


def filter_positions(row, positions):
    for p in positions:
        if p in eval(row["positions"]):
            return True
    return False


def upload_local_photo(file):
    file_ = open(file, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    return data_url


def download_photo_url(url):
    photo_name = "_".join(url.split("/")[-3:])

    r = requests.get(url, allow_redirects=True)
    photo_file = photo_profile_dir / photo_name
    open(photo_file, "wb").write(r.content)

    return photo_file


def create_table(data, width=100, class_="", image_height=95, image_width=95):
    if len(class_) > 0:
        table = f'<table class="{class_}" style="text-align: center; width:{width}%">'
    else:
        table = f'<table style="text-align: center; width:{width}%">'

    # create header row
    header_html = "<tr>"
    for col in data.columns:
        if col == "photo_url":
            header_html = header_html + "<th>Photo</th>"
        elif col == "Value":
            header_html = header_html + "<th>Value (€M)</th>"
        elif col == "player_hashtags":
            header_html = header_html + "<th>Description</th>"
        else:
            header_html = header_html + f"<th>{col.capitalize()}</th>"
    header_html = header_html + "<tr>"

    all_rows_html = ""
    for row_index in range(len(data)):
        row_html = "<tr>"
        row = data.iloc[row_index]
        for col in data.columns:
            if col == "photo_url":
                local_photo = download_photo_url(row[col])
                data_url = upload_local_photo(local_photo)
                row_html = (
                    row_html
                    + f'<td><img src="data:image/gif;base64,{data_url}" height="{image_height} width="{image_width}"></img></td>'
                )
            elif row[col] == None:
                row_html = row_html + "<td></td>"
            elif col == "positions":
                row_html = row_html + f'<td>{", ".join(eval(row[col]))}</td>'
            else:
                row_html = row_html + f"<td>{row[col]}</td>"
        row_html = row_html + "</tr>"
        all_rows_html = all_rows_html + row_html

    table = table + header_html + all_rows_html + "</table>"
    st.markdown(table, unsafe_allow_html=True)


def scan(leagues, positions, transfer_fee, wage, age):
    df = load_data()

    df = df[df["age"] <= age]
    if all_name not in leagues:
        df = df[df["league"].isin(leagues)]
    df = df[(df["Value"] <= transfer_fee) & (df["Wage"] <= wage)]

    df["filter_positions"] = df.apply(
        lambda row: filter_positions(row, positions), axis=1
    )
    search_space = df.loc[df["filter_positions"] == True]
    search_space.reset_index(drop=True, inplace=True)

    # find outliers here
    # Returns -1 for outliers and 1 for inliers.

    X = search_space[possible_columns_to_compare].to_numpy()
    clf = IsolationForest(random_state=42, n_jobs=-1)
    search_space["label"] = pd.Series(list(clf.fit_predict(X)))
    search_space["score"] = pd.Series(list(clf.score_samples(X)))

    # The anomaly score of the input samples. The lower, the more outlier.
    search_space.sort_values(by=["score"], inplace=True)

    return search_space


if is_scan:
    search_space = scan(leagues, positions, transfer_fee, wage, age)

    # calculate summaries to show
    number_of_players = search_space.shape[0]
    number_of_outlierPlayers = search_space["label"].value_counts().to_dict()[-1]

    st.markdown(f"The number of players in the search space: {number_of_players}")
    st.markdown(
        f"The number of outlier players in the search space: {number_of_outlierPlayers}"
    )
    st.markdown(f"**Top {max_k} Identified Outliers**:")
    result = search_space[search_space["label"] == -1].head(max_k)

    result["Value"] = result["Value"].apply(lambda v: str(v / 1000000))
    create_table(result[show_columns])
else:
    st.title(":male-detective: Outlier Detector")
    st.markdown(
        ">Being an _outsider_ is fine because they are the ones who **change** the world and make a real and lasting **difference**."
    )
    st.markdown(
        "This app makes use of [EA SPORTS™ FIFA 2020](https://sofifa.com) KPIs to detect outliers. Outlier players are **rare** and have a significantly **different** profile than the majority of the players."
    )

    st.markdown(
        "Select filters such as league, age, and market value on players Then, each remaining player is considered as a vector of their KPIs and afterwards [IsolationForest](https://dl.acm.org/doi/10.1109/ICDM.2008.17) is used to detect outliers."
    )
    col1, col2, col3 = st.beta_columns([1, 2, 1])
    col2.image(
        str(static_dir / "IsolationForest.png"),
        caption="Example picture of IsolationForest in Sikit-learn",
        use_column_width=True,
    )
    st.markdown(
        "Since outliers are **few** and **different**, they are easier to _isolate_ compared to normal instances. Isolation Forest builds an ensemble of `Isolation Trees` for the data set to isolates players by randomly selecting a KPI and then randomly selecting a split value between the maximum and minimum values of that KPI."
    )
    st.markdown(
        "Since recursive partitioning can be represented by a tree structure, the number of splittings required to isolate a player is equivalent to the path length from the root node to the terminating node. This path length, averaged over a forest of such random trees, is a measure of being an outlier."
    )
    st.markdown(
        "When a forest of random trees collectively produce shorter path lengths for particular instances, they are highly likely to be outliers. More on this topic can be found **[here](https://en.wikipedia.org/wiki/Isolation_forest)**."
    )
