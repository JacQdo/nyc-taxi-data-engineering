import streamlit as st
import pandas as pd
import snowflake.connector


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NYC Taxi Analytics",
    page_icon="🚕",
    layout="wide",
)


# ============================================================
# CONNEXION SNOWFLAKE
# ============================================================

@st.cache_resource
def get_snowflake_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"],
    )


@st.cache_data(ttl=600)
def execute_query(query):
    conn = get_snowflake_connection()

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetch_pandas_all()
    finally:
        cursor.close()


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data(ttl=600)
def load_daily_data():
    query = """
        SELECT
            PICKUP_DATE,
            TRIP_COUNT,
            TOTAL_DISTANCE,
            AVG_TRIP_DISTANCE,
            TOTAL_REVENUE,
            AVG_TRIP_AMOUNT,
            AVG_TRIP_DURATION_MINUTES,
            AVG_SPEED_KMH,
            AVG_TIP_RATE,
            TOTAL_PASSENGERS
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        ORDER BY PICKUP_DATE
    """

    df = execute_query(query)
    df["PICKUP_DATE"] = pd.to_datetime(df["PICKUP_DATE"])

    return df


@st.cache_data(ttl=600)
def load_hourly_data():
    query = """
        SELECT
            PICKUP_HOUR,
            TIME_PERIOD,
            DAY_TYPE,
            TRIP_COUNT,
            TOTAL_DISTANCE,
            AVG_TRIP_DISTANCE,
            TOTAL_REVENUE,
            AVG_TRIP_AMOUNT,
            AVG_TRIP_DURATION_MINUTES,
            AVG_SPEED_KMH,
            AVG_TIP_RATE,
            TOTAL_PASSENGERS
        FROM NYC_TAXI.FINAL.HOURLY_PATTERNS
        ORDER BY PICKUP_HOUR, DAY_TYPE
    """

    return execute_query(query)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚕 NYC Taxi Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive",
        "💰 Revenue",
        "🚦 Operations",
    ],
)


# ============================================================
# CHARGEMENT
# ============================================================

try:
    daily = load_daily_data()
    hourly = load_hourly_data()

except Exception as e:
    st.error("Impossible de charger les données Snowflake.")
    st.exception(e)
    st.stop()


# ============================================================
# KPI GLOBAUX
# ============================================================

total_trips = daily["TRIP_COUNT"].sum()
total_revenue = daily["TOTAL_REVENUE"].sum()

revenue_per_trip = (
    total_revenue / total_trips
    if total_trips
    else 0
)

avg_distance = (
    (daily["AVG_TRIP_DISTANCE"] * daily["TRIP_COUNT"]).sum()
    / total_trips
    if total_trips
    else 0
)

avg_duration = (
    (daily["AVG_TRIP_DURATION_MINUTES"] * daily["TRIP_COUNT"]).sum()
    / total_trips
    if total_trips
    else 0
)

avg_speed = (
    (daily["AVG_SPEED_KMH"] * daily["TRIP_COUNT"]).sum()
    / total_trips
    if total_trips
    else 0
)

avg_tip_rate = (
    (daily["AVG_TIP_RATE"] * daily["TRIP_COUNT"]).sum()
    / total_trips
    if total_trips
    else 0
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "🏠 Executive":

    st.title("🏠 Executive Dashboard")
    st.caption("NYC Yellow Taxi — 2022 à 2024")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Courses",
        f"{total_trips:,.0f}",
    )

    col2.metric(
        "Chiffre d'affaires",
        f"${total_revenue:,.0f}",
    )

    col3.metric(
        "CA / course",
        f"${revenue_per_trip:,.2f}",
    )

    col4.metric(
        "Distance moyenne",
        f"{avg_distance:.2f} km",
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📈 Volume quotidien")

        chart_data = daily.set_index("PICKUP_DATE")[
            ["TRIP_COUNT"]
        ]

        st.line_chart(chart_data)

    with col2:

        st.subheader("💰 Chiffre d'affaires quotidien")

        revenue_chart = daily.set_index("PICKUP_DATE")[
            ["TOTAL_REVENUE"]
        ]

        st.line_chart(revenue_chart)

    st.divider()

    st.subheader("📊 Indicateurs opérationnels")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Durée moyenne",
        f"{avg_duration:.2f} min",
    )

    col2.metric(
        "Vitesse moyenne",
        f"{avg_speed:.2f} km/h",
    )

    col3.metric(
        "Taux de pourboire",
        f"{avg_tip_rate:.2f} %",
    )

    st.divider()

    with st.expander("🔎 Données quotidiennes"):

        st.dataframe(
            daily,
            use_container_width=True,
        )


# ============================================================
# REVENUE DASHBOARD
# ============================================================

elif page == "💰 Revenue":

    st.title("💰 Revenue Analytics")

    st.caption(
        "Analyse du chiffre d'affaires et de la performance économique"
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "CA total",
        f"${total_revenue:,.0f}",
    )

    col2.metric(
        "CA / course",
        f"${revenue_per_trip:,.2f}",
    )

    col3.metric(
        "Courses",
        f"{total_trips:,.0f}",
    )

    col4.metric(
        "Pourboire moyen",
        f"{avg_tip_rate:.2f} %",
    )

    st.divider()

    # --------------------------------------------------------
    # CA mensuel
    # --------------------------------------------------------

    st.subheader("📅 Chiffre d'affaires mensuel")

    monthly = (
        daily
        .set_index("PICKUP_DATE")
        .resample("ME")["TOTAL_REVENUE"]
        .sum()
    )

    st.line_chart(monthly)

    # --------------------------------------------------------
    # CA quotidien
    # --------------------------------------------------------

    st.subheader("📈 Evolution quotidienne du CA")

    st.line_chart(
        daily.set_index("PICKUP_DATE")[
            ["TOTAL_REVENUE"]
        ]
    )

    st.divider()

    # --------------------------------------------------------
    # Top journées
    # --------------------------------------------------------

    st.subheader("🏆 Top 10 journées par chiffre d'affaires")

    top_days = (
        daily[
            [
                "PICKUP_DATE",
                "TRIP_COUNT",
                "TOTAL_REVENUE",
                "AVG_TRIP_AMOUNT",
            ]
        ]
        .sort_values(
            "TOTAL_REVENUE",
            ascending=False,
        )
        .head(10)
        .copy()
    )

    top_days["PICKUP_DATE"] = (
        top_days["PICKUP_DATE"]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        top_days,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --------------------------------------------------------
    # Revenue par période
    # --------------------------------------------------------

    st.subheader("🕐 CA par période de la journée")

    period_revenue = (
        hourly
        .groupby("TIME_PERIOD", as_index=True)
        .agg(
            TOTAL_REVENUE=("TOTAL_REVENUE", "sum"),
            TRIP_COUNT=("TRIP_COUNT", "sum"),
        )
        .sort_values(
            "TOTAL_REVENUE",
            ascending=False,
        )
    )

    st.bar_chart(
        period_revenue[["TOTAL_REVENUE"]]
    )

    st.dataframe(
        period_revenue,
        use_container_width=True,
    )


# ============================================================
# OPERATIONS DASHBOARD
# ============================================================

elif page == "🚦 Operations":

    st.title("🚦 Operations Analytics")

    st.caption(
        "Analyse des volumes, horaires et performances opérationnelles"
    )

    st.divider()

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    peak_day = daily.loc[
        daily["TRIP_COUNT"].idxmax()
    ]

    peak_hour = hourly.loc[
        hourly["TRIP_COUNT"].idxmax()
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pic journalier",
        f"{peak_day['TRIP_COUNT']:,.0f}",
    )

    col2.metric(
        "Date du pic",
        peak_day["PICKUP_DATE"].strftime("%d/%m/%Y"),
    )

    col3.metric(
        "Heure de pointe",
        f"{int(peak_hour['PICKUP_HOUR']):02d}h",
    )

    col4.metric(
        "Courses à cette heure",
        f"{peak_hour['TRIP_COUNT']:,.0f}",
    )

    st.divider()

    # --------------------------------------------------------
    # Volume par heure
    # --------------------------------------------------------

    st.subheader("🕐 Volume des courses par heure")

    hourly_volume = (
        hourly
        .groupby("PICKUP_HOUR")["TRIP_COUNT"]
        .sum()
        .sort_index()
    )

    st.bar_chart(hourly_volume)

    st.divider()

    # --------------------------------------------------------
    # Performance horaire
    # --------------------------------------------------------

    st.subheader("📊 Performance opérationnelle par heure")

    hourly_perf = (
        hourly
        .groupby("PICKUP_HOUR")
        .agg(
            TRIP_COUNT=("TRIP_COUNT", "sum"),
            TOTAL_REVENUE=("TOTAL_REVENUE", "sum"),
            AVG_TRIP_DISTANCE=("AVG_TRIP_DISTANCE", "mean"),
            AVG_TRIP_DURATION_MINUTES=(
                "AVG_TRIP_DURATION_MINUTES",
                "mean",
            ),
            AVG_SPEED_KMH=("AVG_SPEED_KMH", "mean"),
            AVG_TIP_RATE=("AVG_TIP_RATE", "mean"),
        )
        .sort_index()
    )

    st.dataframe(
        hourly_perf,
        use_container_width=True,
    )

    st.divider()

    # --------------------------------------------------------
    # Jour de la semaine
    # --------------------------------------------------------

    st.subheader("📆 Semaine vs week-end")

    day_type = (
        hourly
        .groupby("DAY_TYPE")
        .agg(
            TRIP_COUNT=("TRIP_COUNT", "sum"),
            TOTAL_REVENUE=("TOTAL_REVENUE", "sum"),
            AVG_TRIP_DISTANCE=("AVG_TRIP_DISTANCE", "mean"),
            AVG_SPEED_KMH=("AVG_SPEED_KMH", "mean"),
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            day_type[["TRIP_COUNT"]]
        )

    with col2:

        st.bar_chart(
            day_type[["TOTAL_REVENUE"]]
        )

    st.dataframe(
        day_type,
        use_container_width=True,
    )

    st.divider()

    # --------------------------------------------------------
    # Insights
    # --------------------------------------------------------

    st.subheader("💡 Operational Insights")

    peak_day_date = peak_day["PICKUP_DATE"].strftime(
        "%d/%m/%Y"
    )

    peak_hour_value = int(
        peak_hour["PICKUP_HOUR"]
    )

    st.info(
        f"""
        **Pic journalier :** {peak_day_date} avec
        **{peak_day['TRIP_COUNT']:,.0f} courses**.

        **Heure de pointe :** {peak_hour_value:02d}h avec
        **{peak_hour['TRIP_COUNT']:,.0f} courses**
        sur l'ensemble de la période analysée.

        **Durée moyenne globale :**
        {avg_duration:.2f} minutes.

        **Vitesse moyenne globale :**
        {avg_speed:.2f} km/h.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "NYC Taxi Data Engineering • Snowflake + dbt + Streamlit"
)