import streamlit as st
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

st.set_page_config(
    page_title="MediSnap AI",
    page_icon="💊",
    layout="centered"
)

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("💊 MediSnap AI")
st.write("Upload a medicine image and get easy-to-understand information.")

language = st.selectbox(
    "Select your language",
    ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam"]
)

uploaded_file = st.file_uploader(
    "Upload a medicine image",
    type=["jpg", "jpeg", "png"]
)

question = st.text_input(
    "Ask something about the medicine (optional)"
)

if uploaded_file:
    st.image(
        uploaded_file,
        caption="Uploaded Medicine",
        use_container_width=True
    )

    if st.button("🔍 Analyze Medicine"):
        image_bytes = uploaded_file.getvalue()

        prompt = f"""
{SYSTEM_PROMPT}

The user's selected language is: {language}

User's question:
{question if question else "Identify this medicine and explain its common uses and important safety information."}
"""

        try:
            with st.spinner("🔍 Analyzing medicine..."):
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=uploaded_file.type
                        ),
                        prompt
                    ]
                )

            if response.text:
                st.subheader("💊 Medicine Information")
                st.write(response.text)
            else:
                st.warning(
                    "⚠️ I couldn't identify the medicine from this image. "
                    "Please upload a clearer image showing the medicine name."
                )

        except Exception as e:
            st.error(
                "❌ Something went wrong while analyzing the image."
            )
            st.exception(e)

        st.warning(
            "⚠️ This information is for general educational purposes. "
            "Do not use it as a substitute for advice from a doctor or pharmacist."
        )