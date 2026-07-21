import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage
import json
from openai import OpenAI

ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY1"])

local_storage = LocalStorage()

st.title("AI Task Manager")

def pg1():
    if st.button("전체 제거"):
        local_storage.setItem("tasks", [])
        st.rerun()
    # 저장된 작업 가져오기
    tasks = local_storage.getItem("tasks")
    
    if tasks is None:
        tasks = []
    
    # 입력
    task = st.text_input(
        "앞으로 해야 할 일을 입력하세요",
        placeholder="여기에 입력해주세요. "
    )
    
    # 추가
    if st.button("추가"):
        if task:
            tasks.append(task)
    
            data = {
                "main_goal": task,
                "tasks": tasks
            }
    
            local_storage.setItem("app_data", data)
            local_storage.setItem("tasks", tasks)
    
            st.success("저장되었습니다.")
            st.rerun()
        else:
            st.warning("할 일을 입력해주세요.")
    
    st.subheader("해야 할 일")
    
    for i, t in enumerate(tasks):
        col1, col2 = st.columns([4, 1])
    
        with col1:
            st.write(f"{i+1}. {t}")
    
        with col2:
            if st.button("제거", key=f"remove_{i}"):
                tasks.pop(i)
                local_storage.setItem("tasks", tasks)
                st.rerun()

def pg2():
    st.title("1-4-7 체계적 목표 설계")

    # 저장된 tasks 불러오기
    tasks = local_storage.getItem("tasks")
    if not tasks:
        tasks = []

    if not tasks:
        st.info("먼저 1페이지에서 큰 목표들을 입력해주세요.")
        return

    st.write("1페이지에 등록된 목표들 중 하나를 선택해 **1-4-7 구조**로 세부 계획을 세워보세요.")
    
    # 선택 박스로 어떤 목표를 1-4-7 구조로 짤지 고르기
    selected_main_goal = st.selectbox("목표 선택", tasks)

    if st.button("1-4-7 구조 생성하기"):
        with st.spinner("AI가 1-4-7 목표 구조를 분석 및 설계 중입니다..."):
            response = ai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": """
                        너는 전문 목표 설계 AI다.
                        사용자가 선택한 1개의 큰 목표를 바탕으로 '1-4-7 체계'에 맞춰 세부 목표를 구성하라.
                        
                        - 1: 큰 목표 (Main Goal)
                        - 4: 중간 목표 (4개)
                        - 7: 각각의 중간 목표마다 딸려 있는 작은 실행 목표 (각각 정확히 7개씩, 총 28개 혹은 구조화된 형태)
                        
                        반드시 아래 JSON 형식으로만 응답한다.
                        {
                          "main_goal": "선택된 큰 목표",
                          "middle_goals": [
                            {
                              "middle_title": "중간 목표 1 제목",
                              "small_goals": [
                                "작은 목표 1",
                                "작은 목표 2",
                                "작은 목표 3",
                                "작은 목표 4",
                                "작은 목표 5",
                                "작은 목표 6",
                                "작은 목표 7"
                              ]
                            }
                          ]
                        }
                        
                        중간 목표는 정확히 4개를 만들고, 각 중간 목표 하위의 small_goals는 반드시 7개를 채워라.
                        설명은 실천 가능한 구체적 행동으로 작성한다.
                        """
                    },
                    {
                        "role": "user",
                        "content": selected_main_goal
                    }
                ]
            )

            result = response.choices[0].message.content

            st.session_state["ai_result_147"] = result
            
            # pg3에서 사용
            local_storage.setItem(
                "goal_plan",
                json.loads(result)
            )

    # 저장된 결과 렌더링
    if "ai_result_147" in st.session_state:
        try:
            result_data = json.loads(st.session_state["ai_result_147"])
            
            st.markdown(f"### **[1단계] 큰 목표**: {result_data.get('main_goal', selected_main_goal)}")
            st.markdown("---")

            middle_goals = result_data.get("middle_goals", [])
            
            for m_idx, m_goal in enumerate(middle_goals, 1):
                with st.container(border=True):
                    st.markdown(f"#### **[4단계 중 중간 목표 {m_idx}]** {m_goal.get('middle_title', '')}")
                    
                    small_goals = m_goal.get("small_goals", [])
                    
                    # 7개의 작은 목표를 깔끔하게 리스트 형태로 출력
                    for s_idx, s_goal in enumerate(small_goals, 1):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;ㄴ **{s_idx}.** {s_goal}")

        except json.JSONDecodeError:
            st.error("JSON 파싱 중 오류가 발생했습니다.")
            st.text(st.session_state["ai_result_147"])
def pg3():
    st.title("AI와 함께 목표 달성하기")

    plan = local_storage.getItem("goal_plan")
    checked = local_storage.getItem("checked")

    if not plan:
        st.warning("먼저 2페이지에서 목표 계획을 만들어주세요.")
        return

    if checked is None:
        checked = {}


    # 현재 진행 상태 계산
    total = 0
    done = 0
    unfinished = []

    for m_idx, middle in enumerate(plan["middle_goals"]):
    
        st.subheader(middle["middle_title"])
    
        for s_idx, small in enumerate(middle["small_goals"]):
    
            key = f"{m_idx}_{s_idx}"
    
            total += 1
    
            checked[key] = st.checkbox(
                small,
                value=checked.get(key, False),
                key=f"check_{key}"
            )
    
            if checked[key]:
                done += 1
            else:
                unfinished.append(small)
    local_storage.setItem(
    "checked",
    checked
)
    rate = int(done / total * 100) if total else 0
    st.progress(rate / 100)
    st.write(f"완료율 : {rate}% ({done}/{total})")

    # -------------------
    # AI 채팅
    # -------------------

    st.header("AI 코치와 대화하기")


    if "coach_messages" not in st.session_state:

        st.session_state.coach_messages = [
            {
                "role": "system",
                "content": """
                너는 사용자의 목표 달성을 돕는 AI 코치다.
                사용자의 목표와 진행 상황을 보고
                구체적인 행동 계획과 조언을 제공한다.
                """
            }
        ]


    # 이전 대화 출력

    for message in st.session_state.coach_messages:

        if message["role"] != "system":

            with st.chat_message(message["role"]):
                st.markdown(message["content"])



    question = st.chat_input(
        "목표 달성에 대해 물어보세요"
    )


    if question:

        st.session_state.coach_messages.append(
            {
                "role":"user",
                "content":question
            }
        )


        with st.chat_message("user"):
            st.markdown(question)



        with st.chat_message("assistant"):

            context = f"""
                    [큰 목표]
                    {plan["main_goal"]}
                    
                    [세부 목표]
                    {json.dumps(plan["middle_goals"], ensure_ascii=False)}
                    
                    [진행 상황]
                    완료: {done}/{total}
                    완료율: {rate}%
                    
                    [남은 목표]
                    {json.dumps(unfinished, ensure_ascii=False)}
                    
                    [사용자 질문]
                    {question}
                    """


            with st.spinner("AI 코치가 생각 중...🤔"):

                response = ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role":"system",
                            "content":
                            """
                            너는 사용자의 목표 달성을 돕는 AI 코치다.
                            진행 상황을 보고 구체적인 행동 계획,
                            동기부여, 개선 방법을 알려준다.
                            """
                        },
                        {
                            "role":"user",
                            "content":context
                        }
                    ]
                )

                ai_response = response.choices[0].message.content


                st.markdown(ai_response)



        st.session_state.coach_messages.append(
            {
                "role":"assistant",
                "content":ai_response
            }
        )
pg = st.navigation(
    [
        st.Page(pg1, title="앞으로 해야할 큰 목표"),
        st.Page(pg2, title="AI가 짜주는 1-4-7 세부 목표"),
        st.Page(pg3, title="AI와 얘기하며 목표 달성")
    ],
    position="top"
)

pg.run()
