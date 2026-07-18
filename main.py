from tutor_model import Tutor
import templates
import os
import streamlit as st
import streamlit.components.v1 as components

st.title("TUTOR-AI")

st.sidebar.markdown("# Setup\n")
api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    placeholder="Paste your OpenAI API key here (sk-...)",
    help="You can get your API key from https://platform.openai.com/account/api-keys.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("Made by drakathakash@gmail.com")
st.sidebar.markdown("---")

role_input = st.selectbox(
    "Select a Situation",
    options=templates.role_list,
)
if role_input == "Learn":
    Learn = st.text_input(
        "learning level:",
        placeholder="subject",
        help="Enter the subject which you want to learn",
    )
    st.session_state["Learn"] = (
        Learn if Learn else "math"
    )


if "started" not in st.session_state:
    st.session_state.started = False


def start():
    st.session_state.started = True
    st.session_state.ques_num = 0


st.button(label=f"Start {role_input}", type="primary", on_click=start)

st.markdown("\n---\n")

if st.session_state.started:
    if not api_key_input:
        st.error("Please enter your Open AI API key")
        st.stop()

    if role_input == "Learn":
        tutor = Tutor(api_key_input, role_input, st.session_state.Learn)
    else:
        tutor = Tutor(api_key_input, role_input)

    if "questions" not in st.session_state:
        with st.spinner("Generating Questions..."):
            questions = tutor.get_questions()
        st.session_state.questions = questions
    else:
        questions = st.session_state.questions

    questions = list(
        filter(lambda x: (x.strip() != "" and x.strip() != "."), questions)
    )

    if st.session_state.ques_num >= len(questions):
        st.success("Congratulation. You have Completed the tution.")
        st.markdown("Your Score is:")
        st.markdown(f"## {st.session_state.cumulative_score/15} / 10")
        st.stop()

    def update_ques_num():
        st.session_state.ques_num += 1

    with st.chat_message("tutor"):
        st.markdown("**Question**")
        st.write(questions[st.session_state.ques_num])

    if "answer" not in st.session_state:
        st.text_area("Write your answer here...", key="answer")
        st.button(
            label="Submit",
            type="primary",
        )

    else:
        with st.chat_message("user"):
            st.markdown("**Answer**")
            st.write(st.session_state.answer)
        with st.spinner("Analyzing Your Answer..."):
            rating = tutor.rate_answer(
                questions[st.session_state.ques_num], st.session_state.answer
            )
            suggestion = tutor.get_suggestion(
                questions[st.session_state.ques_num], st.session_state.answer
            )
        if "cumulative_score" not in st.session_state:
            st.session_state.cumulative_score = (
                int(list(rating.values())[0])
                + int(list(rating.values())[1])
                + int(list(rating.values())[2])
            )
        else:
            st.session_state.cumulative_score += (
                int(list(rating.values())[0])
                + int(list(rating.values())[1])
                + int(list(rating.values())[2])
            )
        print(st.session_state.cumulative_score)
        col2, col3 = st.columns(2)
        
        stylesheet = """
                <style>
                    .rating-container {
                        font-family: Poppins, Seouge-UI, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 1rem;
                        border-radius: 1rem;
                        text-align: center;
                        margin: 0.5rem;
                    }
                    .rating-container h1 {
                        font-weight: 700;
                        font-size: 2rem;
                        opacity: 0.6;
                    }
                    .rating-container h3 {
                        font-weight: 400;
                        font-size: 1rem;
                    }
                </style>
                """

        with col2:
            components.html(
                f"""{stylesheet}
                    <div class='rating-container' style='background-color:#B7A4FF;'>
                        <h3>{list(rating.keys())[1]}</h3>
                        <h1>{list(rating.values())[1]}</h1>
                    </div>
                """
            )

        with col3:
            components.html(
                f"""{stylesheet}
                    <div class='rating-container' style='background-color:#F1AA1E;'>
                        <h3>{list(rating.keys())[2]}</h3>
                        <h1>{list(rating.values())[2]}</h1>
                    </div>
                """
            )

        with st.chat_message("assistant"):
            st.markdown("**Suggestion**")
            st.info(suggestion)
        st.button(
            label="Next",
            type="primary",
            on_click=update_ques_num,
            key=st.session_state.ques_num,
        )
