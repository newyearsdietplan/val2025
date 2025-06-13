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

# 티어 필터
tiers = {
    "A": ["강지형", "김뚜띠", "조별하", "짜누"],
    "B": ["감제이", "뱅", "푸린", "핑맨"],
    "C": ["미친개정강지", "눈꽃", "마뫄", "빅헤드"],
    "D": ["아구이뽀", "울프", "유봄냥", "임나은"],
    "E": ["고수달", "따효니", "러너", "백곰파"]
}

# 용병 티어 자동 분류
tiered_streamers = sum(tiers.values(), [])
all_streamers = df["스트리머 이름"].unique()
mercenaries = sorted(list(set(all_streamers) - set(tiered_streamers)))
if mercenaries:
    tiers["용병"] = mercenaries

streamer_tier_map = {}
for tier, streamers in tiers.items():
    for s in streamers:
        streamer_tier_map[s] = tier

selected_tiers = st.sidebar.multiselect("티어 필터", list(tiers.keys()), default=[t for t in tiers.keys() if t != "용병"])
selected_tier_streamers = sum([tiers[tier] for tier in selected_tiers], [])
all_maps = sorted(df["맵"].unique())
selected_roles = st.sidebar.multiselect("요원 역할 필터", agent_roles.keys(), default=list(agent_roles.keys()))
selected_agents = sum([agent_roles[role] for role in selected_roles], [])
selected_maps = st.sidebar.multiselect("맵 필터", all_maps, default=all_maps)

# 선택된 요원과 맵만 포함
# 티어 필터 적용
df = df[df["스트리머 이름"].isin(selected_tier_streamers)]
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

menu = st.sidebar.radio("보기 항목을 선택하세요", (
    "1. 스트리머별 종합 스탯",
    "2. 맵별 스트리머 스탯",
    "3. 스트리머의 요원별 스탯",
    "5. 스트리머의 맵별 스탯",
    "6. 스트리머의 맵-요원별 스탯",
    "4. 경기별 스트리머 스탯"
))

# 컬럼 순서
column_order = ["총 경기 수", "승률", "평균 전투 점수", "평균 효율", "평균 첫 킬", "평균 KD", "평균 KDA", "총 승리 수", "평균 킬", "평균 데스", "평균 어시스트"]

def compute_stats(grouped_df):
    grouped_df.columns = [
        "총 경기 수", "총 킬", "총 데스", "총 어시스트",
        "총 첫 킬", "평균 첫 킬",
        "평균 전투 점수", "평균 효율", "평균 KD", "평균 KDA",
        "총 승리 수", "승률"
    ]
    # 총 킬, 데스, 어시스트를 평균으로 변경
    grouped_df["평균 킬"] = grouped_df["총 킬"] / grouped_df["총 경기 수"]
    grouped_df["평균 데스"] = grouped_df["총 데스"] / grouped_df["총 경기 수"]
    grouped_df["평균 어시스트"] = grouped_df["총 어시스트"] / grouped_df["총 경기 수"]
    grouped_df = grouped_df.drop(columns=["총 킬", "총 데스", "총 어시스트"])
    grouped_df = grouped_df.sort_values("평균 전투 점수")
    return grouped_df

# 포맷 정의
def style_dataframe(df):
    styled = df.style.format({
        "승률": "{:.2f}",
        "평균 전투 점수": "{:.2f}",
        "평균 효율": "{:.2f}",
        "평균 첫 킬": "{:.2f}",
        "평균 KD": "{:.2f}",
        "평균 KDA": "{:.2f}",
        "평균 킬": "{:.1f}",
        "평균 데스": "{:.1f}",
        "평균 어시스트": "{:.1f}"
    })
    return styled

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

def format_streamer_label(name):
    tier = streamer_tier_map.get(name, "-")
    return f"[-] {name}" if tier == "용병" else f"[{tier}] {name}"

def extract_streamer_name(label):
    return label.split("] ")[-1]

if menu == "1. 스트리머별 종합 스탯":
    st.header("📊 스트리머별 종합 스탯")
    stats = df.groupby("스트리머 이름").agg(agg_dict)
    stats = compute_stats(stats)

    streamer_names = stats.index.tolist()
    tiers_for_names = [streamer_tier_map.get(name, "-") for name in streamer_names]
    stats.insert(0, "티어", tiers_for_names)

    stats = stats.sort_values("평균 전투 점수", ascending=False)
    stats.index = [f"[-] {name}" if streamer_tier_map.get(name, "-") == "용병" else f"[{streamer_tier_map.get(name, '-')}] {name}" for name in stats.index]
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "2. 맵별 스트리머 스탯":
    st.header("🗺️ 맵별 스트리머 스탯")
    selected_map = st.selectbox("맵을 선택하세요", sorted(df["맵"].unique()), key="map_select")
    subset = df[df["맵"] == selected_map]
    stats = subset.groupby("스트리머 이름").agg(agg_dict)
    stats = compute_stats(stats)

    streamer_names = stats.index.tolist()
    tiers_for_names = [streamer_tier_map.get(name, streamer_tier_map.get(name, "-")) for name in streamer_names]
    stats.insert(0, "티어", tiers_for_names)

    stats = stats.sort_values("평균 전투 점수", ascending=False)
    stats.index = [f"[-] {name}" if streamer_tier_map.get(name, "-") == "용병" else f"[{streamer_tier_map.get(name, '-')}] {name}" for name in stats.index]
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "3. 스트리머의 요원별 스탯":
    st.header("🧍‍♀️ 스트리머의 요원별 스탯")
    streamer_options = sorted(df["스트리머 이름"].unique())
    label_map = {format_streamer_label(name): name for name in streamer_options}
    selected_label = st.selectbox("스트리머를 선택하세요", list(label_map.keys()), key="streamer_select")
    selected_streamer = label_map[selected_label]
    subset = df[df["스트리머 이름"] == selected_streamer]
    stats = subset.groupby("사용한 요원").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=False)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "4. 경기별 스트리머 스탯":
    st.header("📅 경기별 스트리머 스탯")
    available_dates = sorted(df["날짜"].unique())
    selected_date = st.selectbox("날짜를 선택하세요", available_dates, key="date_select")
    game_ids = df[df["날짜"] == selected_date]["경기 번호"].unique()
    game_options = []
    for gid in sorted(game_ids):
        game_df = df[df["경기 번호"] == gid]
        players = game_df["스트리머 이름"].unique()
        map_name = game_df["맵"].iloc[0]
        label = f"{gid}번 경기 - {map_name} ({', '.join(players)})"
        game_options.append((label, gid))
    selected_label = st.selectbox("경기 번호를 선택하세요", [opt[0] for opt in game_options], key="game_select")
    selected_game = dict(game_options)[selected_label]
    subset = df[df["경기 번호"] == selected_game].copy()
    for col in ["KD", "KDA", "평균 전투 점수", "효율 등급"]:
        subset[col] = subset[col].map(lambda x: f"{x:.2f}")

    def highlight_win(row):
        color = "#d1f0d1" if row["승패"] == "v" else "#f8d0d0"
        return [f"background-color: {color}" for _ in row]

    styled = subset[["날짜", "스트리머 이름", "맵", "사용한 요원", "평균 전투 점수", "킬", "데스", "어시스트", "효율 등급", "첫 킬", "KD", "KDA", "승패"]].style.apply(highlight_win, axis=1)
    display_df = subset[["날짜", "스트리머 이름", "맵", "사용한 요원", "평균 전투 점수", "킬", "데스", "어시스트", "효율 등급", "첫 킬", "KD", "KDA", "승패"]]
    styled = display_df.style.apply(highlight_win, axis=1)
    st.dataframe(styled, use_container_width=True, height=400)
    
    # 이미지 경로 및 출력
    image_filename = f"screenshot/{selected_date}-{selected_game}.png"
    st.image(image_filename, caption=image_filename)

elif menu == "5. 스트리머의 맵별 스탯":
    st.header("🧭 스트리머의 맵별 스탯")  
    streamer_options = sorted(df["스트리머 이름"].unique())
    label_map = {format_streamer_label(name): name for name in streamer_options}
    selected_label = st.selectbox("스트리머를 선택하세요", list(label_map.keys()), key="streamer_map")
    selected_streamer = label_map[selected_label]
    subset = df[df["스트리머 이름"] == selected_streamer]
    stats = subset.groupby("맵").agg(agg_dict)
    stats = compute_stats(stats)
    stats = stats.sort_values("평균 전투 점수", ascending=False)
    styled = style_dataframe(stats[column_order])
    st.dataframe(styled, use_container_width=True, height=800)

elif menu == "6. 스트리머의 맵-요원별 스탯":
    st.header("🧩 스트리머의 맵-요원별 스탯")
    streamer_options = sorted(df["스트리머 이름"].unique())

    if 'selected_streamer_6' not in st.session_state:
        st.session_state.selected_streamer_6 = streamer_options[0]

    selected_streamer = st.selectbox(
        "스트리머를 선택하세요",
        streamer_options,
        index=streamer_options.index(st.session_state.selected_streamer_6),
        key="streamer_map_agent_6"
    )
    if selected_streamer != st.session_state.selected_streamer_6:
        st.session_state.selected_streamer_6 = selected_streamer
        st.rerun()

    subset = df[df["스트리머 이름"] == selected_streamer]
    map_options = sorted(subset["맵"].unique())

    if not map_options:
        st.info("선택한 스트리머가 현재 필터 조건에 해당하는 맵 데이터를 가지고 있지 않습니다.")
    else:
        if 'selected_map_6' not in st.session_state or st.session_state.selected_map_6 not in map_options:
            st.session_state.selected_map_6 = map_options[0]

        selected_map = st.selectbox(
            "맵을 선택하세요",
            map_options,
            index=map_options.index(st.session_state.selected_map_6),
            key="map_by_streamer_6"
        )
        if selected_map != st.session_state.selected_map_6:
            st.session_state.selected_map_6 = selected_map
            st.rerun()

        filtered = subset[subset["맵"] == selected_map]

        if not filtered.empty:
            stats = filtered.groupby("사용한 요원").agg(agg_dict)
            stats = compute_stats(stats)
            stats = stats.sort_values("평균 전투 점수", ascending=True)
            styled = style_dataframe(stats[column_order])
            st.dataframe(styled, use_container_width=True, height=800)
        else:
            st.info("선택된 조건에 해당하는 데이터가 없습니다.")
