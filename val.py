import streamlit as st
import pandas as pd

# 화면 너비 조정
st.set_page_config(layout="wide")

# 데이터
df = pd.read_csv("data.csv")

# 요원 역할 분류
agent_roles = {
    "타격대": ["네온", "레이나", "레이즈", "아이소", "요루", "웨이레이", "제트", "피닉스"],
    "척후대": ["게코", "브리치", "소바", "스카이", "케이/오", "테호", "페이드"],
    "감시자": ["데드록", "바이스", "사이퍼", "세이지", "체임버", "킬조이"],
    "전략가": ["바이퍼", "브림스톤", "아스트라", "오멘", "클로브", "하버"]
}

# 필터 체크박스
all_maps = sorted(df["맵"].unique())
selected_maps = st.sidebar.multiselect("맵 필터", all_maps, default=all_maps)
selected_roles = st.sidebar.multiselect("요원 역할 필터", agent_roles.keys(), default=list(agent_roles.keys()))
selected_agents = sum([agent_roles[role] for role in selected_roles], [])

# 요원, 맵 필터
df = df[df["사용한 요원"].isin(selected_agents)]
df = df[df["맵"].isin(selected_maps)]
df = df[df["사용한 요원"].isin(selected_agents)]

# 승패 변환
df["승리"] = df["승패"].map({"v": 1, "l": 0})

# 공통 함수: KDA 및 KD 계산
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
column_order = ["총 경기 수", "승률", "평균 전투 점수", "평균 효율", "평균 첫 킬", "평균 KD", "평균 KDA", "총 승리 수", "총 킬", "총 데스", "총 어시스트"]

# 공통 처리 함수
def compute_stats(grouped_df):
    grouped_df.columns = [
        "총 경기 수", "총 킬", "총 데스", "총 어시스트",
        "총 첫 킬", "평균 첫 킬",
        "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA",
        "총 승리 수", "승률"
    ]
    grouped_df = grouped_df.sort_values("평균 전투 점수")
    return grouped_df

# 포맷 정의
def style_dataframe(df):
    return df.style.format({
        "승률": "{:.2f}",
        "평균 전투 점수": "{:.2f}",
        "평균 효율": "{:.2f}",
        "평균 첫 킬": "{:.2f}",
        "평균 KD": "{:.2f}",
        "평균 KDA": "{:.2f}"
    })

agg_dict = {
    "경기 번호": "nunique",
    "킬": "sum",
    "데스": "sum",
    "어시스트": "sum",
    "첫 킬": ["sum", "mean"],
    "평균 전투 점수": "mean",
    "효율 등급": "mean",
    "KD": "mean",
    "KDA": "mean",
    "승리": ["sum", "mean"]
}

if menu == "1. 스트리머별 종합 스탯":
    st.header("📊 스트리머별 종합 스탯")
    stats = df.groupby("스트리머 이름").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=True)
    stats = stats.sort_values("평균 전투 점수", ascending=True)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "2. 맵별 스트리머 스탯":
    st.header("🗺️ 맵별 스트리머 스탯")
    selected_map = st.selectbox("맵을 선택하세요", sorted(df["맵"].unique()), key="map_select")
    subset = df[df["맵"] == selected_map]
    stats = subset.groupby("스트리머 이름").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=True)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "3. 스트리머의 요원별 스탯":
    st.header("🧍‍♀️ 스트리머의 요원별 스탯")
    selected_streamer = st.selectbox("스트리머를 선택하세요", sorted(df["스트리머 이름"].unique()), key="streamer_select")
    subset = df[df["스트리머 이름"] == selected_streamer]
    stats = subset.groupby("사용한 요원").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=True)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "4. 경기별 스트리머 스탯":
    st.header("📅 경기별 스트리머 스탯")
    selected_game = st.selectbox("경기 번호를 선택하세요", sorted(df["경기 번호"].unique()), key="game_select")
    subset = df[df["경기 번호"] == selected_game].copy()
    for col in ["KD", "KDA", "평균 전투 점수", "효율 등급"]:
        subset[col] = subset[col].map(lambda x: f"{x:.2f}")
    st.data_editor(subset[["날짜", "스트리머 이름", "맵", "사용한 요원", "평균 전투 점수", "킬", "데스", "어시스트", "효율 등급", "KD", "KDA", "첫 킬", "승패"]], use_container_width=True, height=800)

elif menu == "5. 스트리머의 맵별 스탯":
    st.header("🧭 스트리머의 맵별 스탯")
    selected_streamer = st.selectbox("스트리머를 선택하세요", sorted(df["스트리머 이름"].unique()))
    subset = df[df["스트리머 이름"] == selected_streamer]
    stats = subset.groupby("맵").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=True)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "6. 스트리머의 맵-요원별 스탯":
    st.header("🧩 스트리머의 맵-요원별 스탯")
    streamer_options = sorted(df["스트리머 이름"].unique())

    if not streamer_options:
        st.info("선택된 조건에 해당하는 스트리머가 없습니다.")
    else:
        if 'selected_streamer_6' not in st.session_state or st.session_state.selected_streamer_6 not in streamer_options:
            st.session_state.selected_streamer_6 = streamer_options[0]

        selected_streamer = st.selectbox(
            "스트리머를 선택하세요",
            streamer_options,
            key="streamer_map_agent_6",
            index=streamer_options.index(st.session_state.selected_streamer_6)
        )
        st.session_state.selected_streamer_6 = selected_streamer

        subset = df[df["스트리머 이름"] == selected_streamer]
        map_options = sorted(subset["맵"].unique())

        if not map_options:
            st.info("선택된 스트리머에 해당하는 맵이 없습니다.")
        else:
            if 'selected_map_6' not in st.session_state or st.session_state.selected_map_6 not in map_options:
                st.session_state.selected_map_6 = map_options[0]

            selected_map = st.selectbox(
                "맵을 선택하세요",
                map_options,
                key="map_by_streamer_6",
                index=map_options.index(st.session_state.selected_map_6)
            )
            st.session_state.selected_map_6 = selected_map

            filtered = subset[subset["맵"] == selected_map]
            stats = filtered.groupby("사용한 요원").agg(agg_dict)
            stats = compute_stats(stats)
            stats = stats.sort_values("평균 전투 점수", ascending=True)
            styled = style_dataframe(stats[column_order])
            st.dataframe(styled, use_container_width=True, height=800)

