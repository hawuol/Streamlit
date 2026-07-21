import streamlit as st
from openai import OpenAI

ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "acid_type" not in st.session_state:
    st.session_state.acid_type = "HCl (염산)"
if "acid_vol" not in st.session_state:
    st.session_state.acid_vol = 20
if "base_type" not in st.session_state:
    st.session_state.base_type = "NaOH (수산화 나트륨)"
if "base_vol" not in st.session_state:
    st.session_state.base_vol = 10
if "indicator" not in st.session_state:
    st.session_state.indicator = "BTB 용액"

@st.dialog("⚙️ 실험 조건 상세 설정")
def edit_experiment_settings():
    st.write("기본 산/염기 용액의 종류를 변경합니다.")
    st.session_state.acid_type = st.selectbox(
        "산성 용액 선택",
        ["HCl (염산 - 1가)", "H2SO4 (황산 - 2가)"],
    )
    st.session_state.base_type = st.selectbox(
        "염기성 용액 선택", ["NaOH (수산화 나트륨 - 1가)"]
    )
    if st.button("설정 저장"):
        st.toast("실험 조건이 변경되었습니다!")
        st.rerun()

def page_concept():
    st.header("📣 1. 중화반응 핵심 개념 요약")
    st.info(
        f"현재 설정된 용액: **{st.session_state.acid_type}** & **{st.session_state.base_type}**"
    )

    if st.button("용액 종류 변경하기"):
        edit_experiment_settings()

    st.markdown("""
    ### 💡 핵심 정리
    * **중화반응**: 산의 $\\text{H}^+$ 이온과 염기의 $\\text{OH}^-$ 이온이 $1:1$ 개수 비로 반응하여 **물($\\text{H}_2\\text{O}$)**과 **열(중화열)**을 발생하는 반응입니다.
    * **알짜 이온 반응식**: $\\text{H}^+ + \\text{OH}^- \\rightarrow \\text{H}_2\\text{O}$
    * **지시약의 색 변화 (BTB)**: 산성(노란색) $\\rightarrow$ 중성(초록색) $\\rightarrow$ 염기성(파란색)
    """)
    st.markdown("---")


def page_lab():
    st.header("🧪 2. 중화반응 가상 실험실")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔴 산성 용액")
        st.write(f"종류: **{st.session_state.acid_type}**")
        st.session_state.acid_vol = st.slider(
            "산 부피 (mL)", 10, 50, st.session_state.acid_vol
        )

    with col2:
        st.subheader("🔵 염기성 용액")
        st.write(f"종류: **{st.session_state.base_type}**")
        st.session_state.base_vol = st.slider(
            "추가할 염기 부피 (mL)", 0, 50, st.session_state.base_vol
        )

    st.markdown("---")
    st.session_state.indicator = st.selectbox(
        "사용할 지시약 선택",
        ["BTB 용액", "페놀프탈레인 용액"],
        key="ind_select",
    )

    n_a = 2 if "H2SO4" in st.session_state.acid_type else 1
    n_b = 1  # NaOH

    h_count = n_a * st.session_state.acid_vol
    oh_count = n_b * st.session_state.base_vol

    st.subheader("📊 반응 시뮬레이션 결과")
    if h_count > oh_count:
        st.warning("현재 용액: 산성 🔴 (H+ 이온 남음)")
    elif oh_count > h_count:
        st.info("현재 용액: 염기성 🔵 (OH- 이온 남음)")
    else:
        st.balloons()
        st.success("🎉 중화점 달성! (H+ 와 OH- 수가 일치하여 완벽한 중성 🟢)")

def page_report():
    st.header("📈 3. 이온 수 & 반응 분석 리포트")

    n_a = 2 if "H2SO4" in st.session_state.acid_type else 1
    n_b = 1

    h_moles = n_a * st.session_state.acid_vol
    oh_moles = n_b * st.session_state.base_vol

    rem_h = max(0, h_moles - oh_moles)
    rem_oh = max(0, oh_moles - h_moles)
    cl_ion = h_moles
    na_ion = oh_moles

    ion_data = {
        "수소 이온(H+)": rem_h,
        "수산화 이온(OH-)": rem_oh,
        "음이온(Cl-/SO42-)": cl_ion,
        "나트륨 이온(Na+)": na_ion,
    }

    st.subheader("📊 혼합 용액 내 이온 수 분포")
    st.bar_chart(ion_data)

    st.markdown("---")
    if st.button("실험 조건 전체 초기화"):
        st.session_state.acid_vol = 20
        st.session_state.base_vol = 10
        st.rerun()

def page_ai_tutor():
    st.header("🧐 AI 화학 선생님에게 질문하기")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": "너는 고등학교 통합과학 2 '산·염기와 중화반응' 단원을 친절하게 설명해주는 AI 화학 선생님이야. 학생이 친근하게 느낄 수 있도록 칭찬과 함께 쉬운 예시를 들어 질문에 답해줘.",
            }
        ]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    question = st.chat_input("중화반응에 대해 궁금한 점을 질문하세요!")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            status_context = f"현재 학생의 실험 상황: 산 부피={st.session_state.acid_vol}mL, 염기 부피={st.session_state.base_vol}mL"
            prompt = st.session_state.messages + [
                {"role": "system", "content": status_context}
            ]

            with st.spinner("AI 선생님이 답변을 작성 중입니다...🤔"):
                try:
                    response = ai_client.chat.completions.create(
                        model="gpt-4o-mini", messages=prompt
                    )
                    ai_response = response.choices[0].message.content
                except Exception as e:
                    ai_response = "API 키 문제로 답변을 불러올 수 없습니다. secrets 설정을 확인해주세요."

                st.markdown(ai_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": ai_response}
        )


pg = st.navigation(
    [
        st.Page(page_concept, title="개념 정리", icon="📣"),
        st.Page(page_lab, title="가상 실험실", icon="🧪"),
        st.Page(page_report, title="이온 분석", icon="📈"),
        st.Page(page_ai_tutor, title="AI 화학 튜터", icon="🧐"),
    ],
    position="top",
)

st.title("🔬 통합과학 2: 중화반응 탐구 플래너")
pg.run()
