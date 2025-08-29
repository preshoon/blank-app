#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Titanic Survival Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Metric 카드 스타일 */
[data-testid="stMetric"] {
    background-color: #1f2937; /* 어두운 회색 */
    color: #ffffff;            /* 기본 글자색 흰색 */
    text-align: center;
    padding: 16px 0;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* 라벨/값/델타 텍스트 모두 흰색으로 강제 */
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #ffffff !important;
}

/* 라벨 정렬 유지 */
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 델타 아이콘 위치 보정 */
[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기

#######################
# Sidebar
with st.sidebar:
    # --- Title & help
    st.title("Titanic Survival Dashboard")
    st.caption("필터를 선택하면 모든 시각화가 갱신됩니다.")

    # --- Color theme (공통)
    color_theme = st.selectbox(
        "Select a color theme",
        options=["blues", "greens", "reds", "viridis", "plasma", "inferno", "magma"],
        index=0,
        help="차트 색상 팔레트"
    )

    cols = df_reshaped.columns

    # --- Sex filter
    selected_sex = None
    if "Sex" in cols:
        sex_options = sorted(df_reshaped["Sex"].dropna().astype(str).unique())
        selected_sex = st.multiselect("Sex", options=sex_options, default=sex_options)

    # --- Embarked filter
    selected_embarked = None
    if "Embarked" in cols:
        emb_options = sorted(df_reshaped["Embarked"].dropna().astype(str).unique())
        selected_embarked = st.multiselect("Embarked (탑승항)", options=emb_options, default=emb_options)

    # --- Pclass filter
    selected_pclass = None
    if "Pclass" in cols:
        pclass_options = sorted(pd.to_numeric(df_reshaped["Pclass"], errors="coerce").dropna().astype(int).unique())
        selected_pclass = st.multiselect("Passenger Class (Pclass)", options=pclass_options, default=pclass_options)

    # --- Age range
    age_range = None
    if "Age" in cols:
        age_series = pd.to_numeric(df_reshaped["Age"], errors="coerce")
        a_min = int(max(0, age_series.min(skipna=True) if age_series.notna().any() else 0))
        a_max = int(min(90, age_series.max(skipna=True) if age_series.notna().any() else 80))
        age_range = st.slider("Age range", min_value=0, max_value=max(1, a_max), value=(0, a_max), step=1)

    # --- Fare range (선택)
    fare_range = None
    if "Fare" in cols:
        fare_series = pd.to_numeric(df_reshaped["Fare"], errors="coerce")
        f_min = float(max(0.0, fare_series.min(skipna=True) if fare_series.notna().any() else 0.0))
        f_max = float(fare_series.max(skipna=True) if fare_series.notna().any() else 100.0)
        fare_range = st.slider("Fare range", min_value=0.0, max_value=round(max(1.0, f_max), 2),
                               value=(0.0, round(max(1.0, f_max), 2)))

    # --- Top N (Top insights/Top states 유사용)
    top_n = st.slider("Top N groups", min_value=5, max_value=20, value=10, step=1)

    # --- Reset filters
    if st.button("Reset filters"):
        st.session_state.clear()
        st.rerun()

    # --- expose selections to session_state (본문에서 활용)
    st.session_state["color_theme"] = color_theme
    st.session_state["selected_sex"] = selected_sex
    st.session_state["selected_embarked"] = selected_embarked
    st.session_state["selected_pclass"] = selected_pclass
    st.session_state["age_range"] = age_range
    st.session_state["fare_range"] = fare_range
    st.session_state["top_n"] = top_n

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.subheader("Overview")

    # --- 필터 적용
    df = df_reshaped.copy()
    if st.session_state.get("selected_sex"):
        df = df[df["Sex"].isin(st.session_state["selected_sex"])]
    if st.session_state.get("selected_embarked"):
        df = df[df["Embarked"].isin(st.session_state["selected_embarked"])]
    if st.session_state.get("selected_pclass"):
        df = df[df["Pclass"].isin(st.session_state["selected_pclass"])]
    if st.session_state.get("age_range"):
        age_min, age_max = st.session_state["age_range"]
        df = df[(df["Age"] >= age_min) & (df["Age"] <= age_max)]
    if st.session_state.get("fare_range"):
        fare_min, fare_max = st.session_state["fare_range"]
        df = df[(df["Fare"] >= fare_min) & (df["Fare"] <= fare_max)]

    # --- 기본 지표
    total_passengers = len(df)
    survived = int(df["Survived"].sum()) if "Survived" in df.columns else 0
    not_survived = total_passengers - survived
    survival_rate = (survived / total_passengers * 100) if total_passengers > 0 else 0

    st.metric("Total Passengers", total_passengers)
    st.metric("Survived", survived)
    st.metric("Did not Survive", not_survived)
    st.metric("Survival Rate", f"{survival_rate:.1f}%")

    st.markdown("---")
    st.subheader("Survival by Sex")

    # --- 성별 생존률
    if "Sex" in df.columns and "Survived" in df.columns and total_passengers > 0:
        sex_stats = (
            df.groupby("Sex")["Survived"]
            .agg(["mean", "count"])
            .reset_index()
        )
        for _, row in sex_stats.iterrows():
            sex_label = str(row["Sex"]).capitalize()
            rate = row["mean"] * 100
            st.metric(f"{sex_label} Survival Rate", f"{rate:.1f}% ({int(row['count'])})")
    else:
        st.info("성별 데이터가 부족합니다.")

with col[1]:
    st.subheader("Main Visualizations")

    # --- 필터 적용
    df = df_reshaped.copy()
    if st.session_state.get("selected_sex"):
        df = df[df["Sex"].isin(st.session_state["selected_sex"])]
    if st.session_state.get("selected_embarked"):
        df = df[df["Embarked"].isin(st.session_state["selected_embarked"])]
    if st.session_state.get("selected_pclass"):
        df = df[df["Pclass"].isin(st.session_state["selected_pclass"])]
    if st.session_state.get("age_range"):
        age_min, age_max = st.session_state["age_range"]
        df = df[(df["Age"] >= age_min) & (df["Age"] <= age_max)]
    if st.session_state.get("fare_range"):
        fare_min, fare_max = st.session_state["fare_range"]
        df = df[(df["Fare"] >= fare_min) & (df["Fare"] <= fare_max)]

    # --- 시각화 1: Age vs Survival (히스토그램)
    st.markdown("### Age Distribution by Survival")
    if "Age" in df.columns and "Survived" in df.columns:
        fig_age = px.histogram(
            df, 
            x="Age", 
            color="Survived",
            nbins=30,
            barmode="overlay",
            color_discrete_map={0: "red", 1: "green"},
            labels={"Survived": "Survival"}
        )
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("Age 또는 Survived 컬럼이 없어 그래프를 표시할 수 없습니다.")

    # --- 시각화 2: Fare vs Survival (박스플롯)
    st.markdown("### Fare Distribution by Survival")
    if "Fare" in df.columns and "Survived" in df.columns:
        fig_fare = px.box(
            df,
            x="Survived",
            y="Fare",
            color="Survived",
            color_discrete_map={0: "red", 1: "green"},
            labels={"Survived": "Survival"}
        )
        st.plotly_chart(fig_fare, use_container_width=True)
    else:
        st.info("Fare 또는 Survived 컬럼이 없어 그래프를 표시할 수 없습니다.")

    # --- 시각화 3: Pclass + Sex vs Survival (누적 막대그래프)
    st.markdown("### Survival by Pclass and Sex")
    if {"Pclass", "Sex", "Survived"}.issubset(df.columns):
        grouped = (
            df.groupby(["Pclass", "Sex", "Survived"])
            .size()
            .reset_index(name="count")
        )
        fig_stack = px.bar(
            grouped,
            x="Pclass",
            y="count",
            color="Survived",
            facet_col="Sex",
            barmode="stack",
            color_discrete_map={0: "red", 1: "green"},
            labels={"count": "Passengers", "Survived": "Survival"}
        )
        st.plotly_chart(fig_stack, use_container_width=True)
    else:
        st.info("Pclass, Sex, Survived 컬럼이 부족합니다.")

with col[2]:
    st.subheader("Top Insights")

    # --- 필터 적용
    df = df_reshaped.copy()
    if st.session_state.get("selected_sex"):
        df = df[df["Sex"].isin(st.session_state["selected_sex"])]
    if st.session_state.get("selected_embarked"):
        df = df[df["Embarked"].isin(st.session_state["selected_embarked"])]
    if st.session_state.get("selected_pclass"):
        df = df[df["Pclass"].isin(st.session_state["selected_pclass"])]
    if st.session_state.get("age_range"):
        age_min, age_max = st.session_state["age_range"]
        df = df[(df["Age"] >= age_min) & (df["Age"] <= age_max)]
    if st.session_state.get("fare_range"):
        fare_min, fare_max = st.session_state["fare_range"]
        df = df[(df["Fare"] >= fare_min) & (df["Fare"] <= fare_max)]

    # --- Top groups by survival rate
    if {"Pclass", "Sex", "Survived"}.issubset(df.columns) and len(df) > 0:
        grouped = (
            df.groupby(["Pclass", "Sex"])["Survived"]
            .agg(["mean", "count"])
            .reset_index()
        )
        grouped["SurvivalRate"] = grouped["mean"] * 100
        grouped = grouped.sort_values("SurvivalRate", ascending=False)

        top_n = st.session_state.get("top_n", 10)
        top_groups = grouped.head(top_n)

        st.markdown("### Top Groups by Survival Rate")
        # 연속 팔레트 대신 범주형 색상을 사용
        fig_top = px.bar(
            top_groups,
            x="SurvivalRate",
            y="Sex",
            color="Pclass",
            orientation="h",
            text=top_groups["SurvivalRate"].apply(lambda x: f"{x:.1f}%"),
            labels={"SurvivalRate": "Survival Rate (%)", "Sex": "Sex", "Pclass": "Class"}
        )
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("필요한 컬럼이 부족해 Top 그룹 분석을 표시할 수 없습니다.")

    st.markdown("---")
    st.subheader("About")

    st.markdown("""
    **Dataset:** Titanic Passenger Dataset  
    **Target Variable:** `Survived` (1 = 생존, 0 = 사망)  

    **Columns 주요 설명**  
    - `Pclass`: 객실 등급 (1 = 1등석, 2 = 2등석, 3 = 3등석)  
    - `Sex`: 성별  
    - `Age`: 나이  
    - `Fare`: 운임 요금  
    - `Embarked`: 승선항 (C = Cherbourg, Q = Queenstown, S = Southampton)  

    **분석 지표**  
    - *Survival Rate*: 특정 그룹 내 생존자 비율  
    - *Top Groups*: 필터링된 조건에서 생존률이 높은/낮은 그룹  
    """)
