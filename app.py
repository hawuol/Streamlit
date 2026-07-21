import streamlit as st
from openai import OpenAI

ai_client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

if 'todo_list' not in st.session_state:
    st.session_state.todo_list = [
        ["옴의 법칙(V=IR) 정리하기", False],
        ["키르히호프 법칙 문제 풀기", False],
        ["P형/N형 반도체 차이점 공부하기", False]
    ]
if 'user_motto' not in st.session_state:
    st.session_state.user_motto = "오늘도 전기전자 마스터!"
if 'motto_updated' not in st.session_state:
    st.session_state.motto_updated = False
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 고등학생을 위한 전기전자공학 친절한 AI 튜터야. 고1 수준에 맞게 쉽고 친절하게 답해줘."}
    ]

def add_todo():
    task = st.session_state.todo_input
    if task:
        st.session_state.todo_list.append([task, False])
        st.toast("학습 항목이 추가되었습니다!")
        st.session_state.todo_input = ""

@st.dialog("오늘의 다짐 수정")
def edit_motto():
    motto = st.text_input("나의 한 줄 학습 목표를 적어주세요.")
    if st.button("목표 저장"):
        st.session_state.user_motto = motto
        st.session_state.motto_updated = True
        st.rerun()

def page_motto():
    st.header("📣 1. 오늘의 학습 다짐")
    st.info(f"현재 목표: {st.session_state.user_motto}")
    if st.button("목표 수정하기"):
        edit_motto()
    if st.session_state.motto_updated:
        st.success("새로운 학습 목표가 등록되었습니다!")
        st.session_state.motto_updated = False
    st.markdown("---")
    st.subheader("💡 고1 통합과학/공학 핵심 요약")
    st.markdown("""
    * **전압 ($V$)**: 전하를 흐르게 하는 능력 (단위: $V$)
    * **전류 ($I$)**: 전하의 흐름 (단위: $A$)
    * **저항 ($R$)**: 전류의 흐름을 방해하는 작용 (단위: $\Omega$)
    * **옴의 법칙**: $V = I \\cdot R$
    """)

def page_todo():
    st.header("✅ 2. 전기전자 학습 체크리스트")
    st.write(f"현재 목표: **{st.session_state.user_motto}**")
    st.text_input("추가할 학습 주제를 입력하세요", key="todo_input")
    st.button("추가하기", on_click=add_todo)
    st.markdown("---")
    for i in range(len(st.session_state.todo_list)):
        col_task, col_btn, col_status = st.columns([4, 1, 1])
        with col_task:
            st.write(f"{i+1}. {st.session_state.todo_list[i][0]}")
        with col_btn:
            if st.button("완료", key=f"btn_{i}"):
                st.session_state.todo_list[i][1] = True
                st.rerun()
        with col_status:
            if st.session_state.todo_list[i][1]:
                st.write("✅ **달성!**")
    st.markdown("---")

def page_report():
    st.header("📈 3. 나의 학습 달성률")
    if not st.session_state.todo_list:
        st.write("아직 등록된 학습 항목이 없습니다.")
    else:
        total = len(st.session_state.todo_list)
        count = sum(1 for item in st.session_state.todo_list if item[1])
        progress = (count / total) * 100
        st.metric("오늘의 학습 달성률", f"{progress:.1f}%")
        st.progress(progress / 100)
        
        if progress == 100:
            st.snow()
            st.toast("🎉 축하합니다! 모든 목표를 달성했습니다!", icon="🏆")
            st.success("오늘의 모든 공학 목표를 달성했습니다! 🏆")
            
        if st.button("기록 전체 초기화"):
            st.session_state.todo_list = []
            st.rerun()

def page_quiz():
    st.header("🧐 4. 전기전자 기초 퀴즈")
    
    q1 = st.radio("1. 전압($V$)이 10V이고 저항($R$)이 5$\Omega$일 때, 전류($I$)는 얼마일까요?", ["1A", "2A", "50A"])
    if st.button("1번 정답 확인"):
        if q1 == "2A":
            st.snow()
            st.toast("정답입니다! 👏")
            st.success("정답입니다! ($I = V / R = 10 / 5 = 2A$)")
        else:
            st.error("다시 생각해보세요!")
            
    st.markdown("---")
    
    q2 = st.radio("2. P형 반도체와 N형 반도체를 접합하여 한쪽 방향으로만 전류가 흐르게 하는 부품은?", ["저항", "다이오드", "트랜지스터"])
    if st.button("2번 정답 확인"):
        if q2 == "다이오드":
            st.snow()
            st.toast("정답입니다! 👏")
            st.success("정답입니다! 다이오드는 한쪽 방향으로만 전류를 흐르게 합니다.")
        else:
            st.error("다시 생각해보세요!")

    st.markdown("---")

    q3 = st.radio("3. 전류의 단위를 나타내는 기호는 무엇일까요?", ["V (볼트)", "A (암페어)", "$\Omega$ (옴)"])
    if st.button("3번 정답 확인"):
        if q3 == "A (암페어)":
            st.snow()
            st.toast("정답입니다! 👏")
            st.success("정답입니다! 전류의 단위는 A(암페어)입니다.")
        else:
            st.error("다시 생각해보세요!")

    st.markdown("---")

    q4 = st.radio("4. 키르히호프 전류 법칙(KCL)에 따라, 회로의 한 마디로 들어오는 전류의 합과 나가는 전류의 합은?", ["같다", "들어오는 전류가 더 크다", "나가는 전류가 더 크다"])
    if st.button("4번 정답 확인"):
        if q4 == "같다":
            st.snow()
            st.toast("정답입니다! 👏")
            st.success("정답입니다! 들어오는 전류의 합과 나가는 전류의 합은 항상 같습니다.")
        else:
            st.error("다시 생각해보세요!")

    st.markdown("---")

    q5 = st.radio("5. 저항을 직렬로 연결하면 전체 저항의 크기는 어떻게 될까요?", ["작아진다", "커진다", "변하지 않는다"])
    if st.button("5번 정답 확인"):
        if q5 == "커진다":
            st.snow()
            st.toast("정답입니다! 👏")
            st.success("정답입니다! 직렬연결 시 전체 저항은 각 저항의 합과 같으므로 커집니다.")
        else:
            st.error("다시 생각해보세요!")


def page_ai_coach():
    st.header("🤖 5. AI 코칭 & 질문하기")
    st.caption("전기전자공학 개념이나 공부법에 대해 무엇이든 질문해보세요!")
    
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_query := st.chat_input("질문을 입력하세요 (예: 반도체가 왜 중요한가요?)"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("AI 튜터가 생각 중..."):
                try:
                    response = ai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages
                    )
                    reply = response.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error("AI 연결 설정(API Key)을 확인해 주세요.")

def page_job_info():
    st.header("💼 6. 전기전자 진로 & 직업 정보")
    st.write("전기전자공학 분야를 공부하면 어떤 직업을 가질 수 있는지 알아봅시다!")
    
    tab1, tab2, tab3 = st.tabs(["💡 대표 직업군", "🎓 관련 학과", "🛠️ 필요 역량"])
    
    with tab1:
        st.subheader("대표 직업 분야")
        st.markdown("""
        * **반도체 공학자**: 스마트폰, 컴퓨터 등에 들어가는 반도체 칩을 설계하고 제조 공정을 연구합니다.
        * **로봇 / 제어 공학자**: 자율주행차, 산업용 로봇, 드론의 회로 및 제어 시스템을 개발합니다.
        * **전력 / 에너지 엔지니어**: 신재생에너지(태양광, 풍력) 및 스마트 그리드 전력망을 연구하고 관리합니다.
        * **임베디드 시스템 개발자**: 가전제품이나 자동차 내부의 하드웨어 제어 소프트웨어를 만듭니다.
        """)
        
    with tab2:
        st.subheader("진학 가능 학과")
        st.markdown("""
        * 전기공학과 / 전자공학과 / 전기전자공학부
        * 반도체공학과 / 시스템반도체공학과
        * 제어계측공학과 / 로봇공학과
        * 정보통신공학과
        """)
        
    with tab3:
        st.subheader("고교 수준 추천 준비 활동")
        st.markdown("""
        * **물리학I, II 학습**: 전류, 전자기장, 파동 기초 개념 튼튼히 쌓기
        * **수학 기초**: 함수, 수열, 미적분 개념 다지기
        * **프로그래밍 기초**: 파이썬(Python) 또는 아두이노(Arduino) 코딩 실습해보기
        """)

pg = st.navigation([
    st.Page(page_motto, title="오늘의 목표", icon="📣"),
    st.Page(page_todo, title="학습 체크리스트", icon="✅"),
    st.Page(page_report, title="학습 달성률", icon="📈"),
    st.Page(page_quiz, title="기초 퀴즈", icon="🧐"),
    st.Page(page_ai_coach, title="AI 코칭", icon="🤖"),
    st.Page(page_job_info, title="직업 정보", icon="💼")
], position="top")

st.title("⚡ 고교 전기전자 기초 플래너")
pg.run()
