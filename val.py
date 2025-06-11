import streamlit as st
import pandas as pd

# 화면 너비 조정
st.set_page_config(layout="wide")

# 데이터
df = pd.read_csv("data.csv")

# 승패 변환
df["승리"] = df["승패"].map({"v": 1, "l": 0})

# KDA 및 KD 계산
def compute_kda(row):
    return (row["킬"] + row["어시스트"]) / row["데스"] if row["데스"] != 0 else row["킬"] + row["어시스트"]

def compute_kd(row):
    return row["킬"] / row["데스"] if row["데스"] != 0 else row["킬"]

df["KDA"] = df.apply(compute_kda, axis=1)
df["KD"] = df.apply(compute_kd, axis=1)

st.title("🎮 발낳대 2025 내전 통계")

menu = st.sidebar.radio("통계 항목 선택", (
    "1. 스트리머별 종합 스탯",
    "2. 맵별 스트리머 스탯",
    "3. 스트리머의 요원별 스탯",
    "4. 경기별 스트리머 스탯",
    "5. 스트리머의 맵별 스탯",
    "6. 스트리머의 맵-요원별 스탯"
))

# 컬럼 순서
column_order = ["총 경기 수", "승률", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "총 킬", "총 데스", "총 어시스트"]

# 포맷 함수 정의
float_columns = ["승률", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA"]
int_columns = ["총 경기 수", "총 승리 수", "총 킬", "총 데스", "총 어시스트"]

def format_mixed(val, col):
    if col in float_columns:
        return f"{val:.2f}"
    elif col in int_columns:
        return f"{int(val)}"
    else:
        return val

def format_dataframe(df):
    formatted_df = df.copy()
    for col in formatted_df.columns:
        if col in float_columns:
            formatted_df[col] = formatted_df[col].map(lambda x: f"{x:.2f}")
        elif col in int_columns:
            formatted_df[col] = formatted_df[col].astype(int)
    return formatted_df

if menu == "1. 스트리머별 종합 스탯":
    st.header("📊 스트리머별 종합 스탯")
    streamer_stats = df.groupby("스트리머 이름").agg({
        "경기 번호": "nunique",
        "킬": "sum",
        "데스": "sum",
        "어시스트": "sum",
        "평균 전투 점수": "mean",
        "효율 등급": "mean",
        "KD": "mean",
        "KDA": "mean",
        "승리": ["sum", "mean"]
    })
    streamer_stats.columns = ["총 경기 수", "총 킬", "총 데스", "총 어시스트", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "승률"]
    styled = format_dataframe(streamer_stats[column_order])
    st.data_editor(styled, use_container_width=True, height=800)

elif menu == "2. 맵별 스트리머 스탯":
    st.header("🗺️ 맵별 스트리머 스탯")
    selected_map = st.selectbox("맵을 선택하세요", sorted(df["맵"].unique()))
    map_df = df[df["맵"] == selected_map]
    map_stats = map_df.groupby("스트리머 이름").agg({
        "경기 번호": "nunique",
        "킬": "sum",
        "데스": "sum",
        "어시스트": "sum",
        "평균 전투 점수": "mean",
        "효율 등급": "mean",
        "KD": "mean",
        "KDA": "mean",
        "승리": ["sum", "mean"]
    })
    map_stats.columns = ["총 경기 수", "총 킬", "총 데스", "총 어시스트", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "승률"]
    styled = format_dataframe(map_stats[column_order])
    st.data_editor(styled, use_container_width=True, height=800)

elif menu == "3. 스트리머의 요원별 스탯":
    st.header("🧍‍♀️ 스트리머의 요원별 스탯")
    selected_streamer = st.selectbox("스트리머를 선택하세요", sorted(df["스트리머 이름"].unique()))
    agent_df = df[df["스트리머 이름"] == selected_streamer]
    agent_stats = agent_df.groupby("사용한 요원").agg({
        "경기 번호": "nunique",
        "킬": "sum",
        "데스": "sum",
        "어시스트": "sum",
        "평균 전투 점수": "mean",
        "효율 등급": "mean",
        "KD": "mean",
        "KDA": "mean",
        "승리": ["sum", "mean"]
    })
    agent_stats.columns = ["총 경기 수", "총 킬", "총 데스", "총 어시스트", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "승률"]
    styled = format_dataframe(agent_stats[column_order])
    st.data_editor(styled, use_container_width=True, height=800)

elif menu == "4. 경기별 스트리머 스탯":
    st.header("📅 경기별 스트리머 스탯")
    selected_game = st.selectbox("경기 번호를 선택하세요", sorted(df["경기 번호"].unique()))
    game_df = df[df["경기 번호"] == selected_game].copy()
    game_df["KD"] = game_df["KD"].apply(lambda x: f"{x:.2f}")
    game_df["KDA"] = game_df["KDA"].apply(lambda x: f"{x:.2f}")
    game_df["평균 전투 점수"] = game_df["평균 전투 점수"].apply(lambda x: f"{x:.2f}")
    game_df["효율 등급"] = game_df["효율 등급"].apply(lambda x: f"{x:.2f}")
    st.data_editor(game_df[["날짜", "스트리머 이름", "맵", "사용한 요원", "평균 전투 점수", "킬", "데스", "어시스트", "효율 등급", "KD", "KDA", "첫 킬", "승패"]], use_container_width=True, height=800)

elif menu == "5. 스트리머의 맵별 스탯":
    st.header("🧭 스트리머의 맵별 스탯")
    selected_streamer = st.selectbox("스트리머를 선택하세요", sorted(df["스트리머 이름"].unique()))
    streamer_df = df[df["스트리머 이름"] == selected_streamer]
    map_stats = streamer_df.groupby("맵").agg({
        "경기 번호": "nunique",
        "킬": "sum",
        "데스": "sum",
        "어시스트": "sum",
        "평균 전투 점수": "mean",
        "효율 등급": "mean",
        "KD": "mean",
        "KDA": "mean",
        "승리": ["sum", "mean"]
    })
    map_stats.columns = ["총 경기 수", "총 킬", "총 데스", "총 어시스트", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "승률"]
    styled = format_dataframe(map_stats[column_order])
    st.data_editor(styled, use_container_width=True, height=800)

elif menu == "6. 스트리머의 맵-요원별 스탯":
    st.header("🧩 스트리머의 맵-요원별 스탯")
    selected_streamer = st.selectbox("스트리머를 선택하세요", sorted(df["스트리머 이름"].unique()), key="streamer_map_agent")
    streamer_df = df[df["스트리머 이름"] == selected_streamer]
    selected_map = st.selectbox("맵을 선택하세요", sorted(streamer_df["맵"].unique()), key="map_by_streamer")
    filtered_df = streamer_df[streamer_df["맵"] == selected_map]
    agent_stats = filtered_df.groupby("사용한 요원").agg({
        "경기 번호": "nunique",
        "킬": "sum",
        "데스": "sum",
        "어시스트": "sum",
        "평균 전투 점수": "mean",
        "효율 등급": "mean",
        "KD": "mean",
        "KDA": "mean",
        "승리": ["sum", "mean"]
    })
    agent_stats.columns = ["총 경기 수", "총 킬", "총 데스", "총 어시스트", "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA", "총 승리 수", "승률"]
    styled = format_dataframe(agent_stats[column_order])
    st.data_editor(styled, use_container_width=True, height=800)
