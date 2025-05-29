import streamlit as st

# Set up page
st.set_page_config(page_title="Cartoon Cat Task Board", layout="centered")

# 💖 Background color with CSS
st.markdown(
    """
    <style>
    .main {
        background-color: #ffe6f0;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🐾 Cartoon Cat Task Board 🐱")

# 🎀 Cute sticker images
st.image("https://cdn.pixabay.com/photo/2021/10/18/21/35/cat-6721100_1280.png", width=120)
st.image("https://cdn.pixabay.com/photo/2023/06/29/21/30/cat-8096660_1280.png", width=120)

st.markdown("---")

# ✨ Initialize task state
if "tasks" not in st.session_state:
    st.session_state.tasks = [""] * 5
if "done" not in st.session_state:
    st.session_state.done = [False] * 5

# 🎯 Task input and done buttons
st.subheader("🎀 Your Kitty Tasks")
for i in range(5):
    cols = st.columns([0.75, 0.25])
    if st.session_state.done[i]:
        cols[0].markdown(f"✅ ~~{st.session_state.tasks[i]}~~")
    else:
        st.session_state.tasks[i] = cols[0].text_input(
            f"Task {i+1}", value=st.session_state.tasks[i], key=f"task_{i}"
        )
        if cols[1].button("Done", key=f"done_{i}"):
            st.session_state.done[i] = True
            st.success("Meow-gnificent! 🐾")
            st.image(
                "https://cdn.pixabay.com/photo/2021/03/11/14/46/cat-6085614_1280.png",
                width=200,
                caption="Purr-fect! ✅"
            )
            st.audio("https://www.fesliyanstudios.com/play-mp3/6965", autoplay=True)

# 🧼 Reset button
if st.button("Reset All"):
    st.session_state.tasks = [""] * 5
    st.session_state.done = [False] * 5
    st.info("All tasks cleared. Time for fresh meows!")