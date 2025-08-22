import streamlit as st
import random

# 앱의 제목 설정
st.set_page_config(page_title="세상 모든 룰렛")
st.title("🎲 세상 모든 룰렛")
st.subheader("결정을 어려워하는 당신을 위한 선택 도우미")

# 세션 상태 초기화
# 'options' 변수에 룰렛 항목을 저장합니다.
if 'options' not in st.session_state:
    st.session_state.options = []

# 텍스트 입력창
# 사용자가 콤마(,)로 구분된 항목을 입력할 수 있습니다.
options_input = st.text_input(
    "콤마(,)로 구분하여 룰렛 항목을 입력하세요:",
    placeholder="예: 짜장면, 짬뽕, 볶음밥"
)

# "룰렛 돌리기" 버튼
if st.button("룰렛 돌리기"):
    # 입력된 텍스트를 콤마(,) 기준으로 분리하고 공백을 제거합니다.
    items = [item.strip() for item in options_input.split(',') if item.strip()]

    # 입력된 항목이 있는지 확인합니다.
    if items:
        # 항목이 있다면, 그 중 하나를 무작위로 선택합니다.
        st.session_state.chosen_item = random.choice(items)
        st.success(f"🎉 **당신의 선택은... '{st.session_state.chosen_item}' 입니다!** 🎉")
    else:
        # 항목이 없다면 경고 메시지를 표시합니다.
        st.warning("룰렛 항목을 입력해주세요.")

# 선택된 항목이 있다면 화면에 표시합니다.
# if 'chosen_item' in st.session_state:
#     st.info(f"선택된 항목: {st.session_state.chosen_item}")

st.info("룰렛 항목을 입력하고 '룰렛 돌리기' 버튼을 눌러보세요.")