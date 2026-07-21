import re
import urllib.parse
import streamlit as st
from openai import OpenAI

def reset_all():
    st.session_state.user_name = ""
    st.session_state.weather = "☀️ 화창하고 밝음"
    st.session_state.feel = "텐션 최고! 🥳"
    st.session_state.genre = "힙합"
    st.session_state.with_whom = "👤 나 혼자만의 시간"
    st.session_state.extra_info = ""

ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="기분 맞춤 추천기", page_icon="🍕", layout="centered")

st.title("🎧 오늘 뭐 먹고 뭐 듣지?")
st.caption("현재 당신의 상황과 기분에 딱 맞는 음식과 노래를 추천해 드려요!")

with st.sidebar:
    st.header("프로필")
    user_name = st.text_input("닉네임", key="user_name")
    weather = st.selectbox("오늘 날씨", ["☀️ 화창하고 밝음", "🌧️ 비가 내림", "☁️ 흐리고 꿀꿀함", "❄️ 춥거나 눈이 옴", "🌙 센치한 밤"], key="weather")
    feel = st.selectbox("당신의 기분은 어떤가요?",["최악 😭", "우울/지침 😮‍💨", "평범 😐", "기분 좋음 😊", "텐션 최고! 🥳"], key="feel")
    with_whom = st.selectbox("👥 누구와 함께 있나요?", ["👤 나 혼자만의 시간", "👥 친구들과 함께", "💕 연인과 데이트", "🏠 가족들과 함께"], key="with_whom")
    genre = st.selectbox("🎶 어떤 장르의 노래를 듣고싶나요?", ["힙합", "발라드", "트로트", "팝송","동요"], key="genre")
    extra_info = st.text_input("💡 추가로 들려주고 싶은 이야기가 있나요? (선택)", placeholder="예: 오늘 시험이 끝났어요, 외국 힙합이 듣고싶어요 등", key="extra_info")
    st.markdown("---")
    st.info(f"반가워요, {user_name}님! 오늘 날씨는 '{weather}'이네요. 당신의 기분은 '{feel}'이신가요? 그렇다면 이 기분과 '{with_whom}'일때에 맞는 노래와 음식을 추천해 드릴게요!")

if st.button("✨ 맞춤 추천 받기", use_container_width=True):
    prompt = f"""
    기분이랑 날씨, 함께 있는 사람, 그리고 원하는 장르({genre})에 따라 음식과 노래 3곡을 추천해주세요!
    
    [사용자 상황]
    - 날씨: {weather}
    - 함께 있는 사람: {with_whom}
    - 현재 기분: {feel}
    - 선호 장르: {genre}
    - 추가 정보: {extra_info if extra_info else '없음'}

    [출력 형식]
    1. 🍽️ **오늘의 추천 음식**: (음식 이름)
       - 추천 이유: (다정한 어조로 2~3줄 설명)

    2. 🎵 **기분 맞춤 플레이리스트**:
       - 곡 1: [가수 - 노래 제목]
         > 추천 이유: (줄바꿈 후 한 줄 설명)
       - 곡 2: [가수 - 노래 제목]
         > 추천 이유: (줄바꿈 후 한 줄 설명)
       - 곡 3: [가수 - 노래 제목]
         > 추천 이유: (줄바꿈 후 한 줄 설명)

    3. 💡 **음악 배경 지식 & 선곡 이유**:
       (설명 작성)
    """

    # 2. 버튼 안쪽(들여쓰기 적용)에서 API 호출 및 spinner 실행
    with st.spinner("당신의 기분에 딱 맞는 조합을 찾고 있어요... 🔮"):
        try:
            response = ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )

            result = response.choices[0].message.content

            st.success("🎉 추천이 도착했습니다!")
            st.markdown(result)

            st.markdown("---")
            st.subheader("🎬 추천된 노래 바로 듣기")

            import re

            songs = re.findall(r"\[(.*?)\]", result)

            if songs:
                for song in songs:
                    encoded_song = urllib.parse.quote(f"{song} 오피셜 음원")
                    yt_url = f"https://www.youtube.com/results?search_query={encoded_song}"

                    with st.expander(f"🎵 '{song}' 바로 재생 링크 & 검색"):
                        st.write(
                            f"클릭하면 **{song}**의 최신 음원/뮤직비디오를 바로 들으실 수 있습니다."
                        )
                        st.link_button(
                            f"▶️ YouTube에서 {song} 바로 틀기",
                            yt_url,
                            use_container_width=True,
                        )
            else:
                default_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(genre + ' 추천 노래')}"
                st.link_button(
                    "▶️ YouTube에서 플레이리스트 틀기",
                    default_url,
                    use_container_width=True,
                )

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
st.button("전체 초기화", on_click=reset_all)
