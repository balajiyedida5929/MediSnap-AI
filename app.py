
import streamlit as st
import time
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

# Page configuration
st.set_page_config(
    page_title="MediSnap AI",
    page_icon="💊",
    layout="centered"
)

# Gemini API configuration
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# Application title
st.title("💊 MediSnap AI")
st.write(
    "Upload a medicine image and get easy-to-understand information."
)

# Language selection
language = st.selectbox(
    "Select your language",
    ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam"]
)

# Medicine image upload
uploaded_file = st.file_uploader(
    "Upload a medicine image",
    type=["jpg", "jpeg", "png"]
)

# Optional question
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

Instructions:
- Explain the medicine in simple language.
- Mention common uses and important precautions.
- Do not guess the medicine identity if the image is unclear.
- Respond in the selected language.
- Do not provide personalized prescriptions or dosages.
"""

        try:

            response = None

            # Retry mechanism for temporary server errors
            with st.spinner("🔍 Analyzing medicine..."):

                for attempt in range(3):

                    try:

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

                        break

                    except Exception as e:

                        error_code = getattr(e, "code", None)

                        if error_code == 503 and attempt < 2:

                            wait_time = 3 * (2 ** attempt)

                            st.warning(
                                f"Gemini server is busy. "
                                f"Retrying in {wait_time} seconds..."
                            )

                            time.sleep(wait_time)

                        else:
                            raise

            if response and response.text:

                st.success("✅ Analysis completed!")

                st.subheader("💊 Medicine Information")

                st.markdown(response.text)

            else:

                st.warning(
                    "⚠️ I couldn't identify the medicine from this image. "
                    "Please upload a clearer image."
                )

        except Exception as e:

            error_code = getattr(e, "code", None)

            if error_code == 503:

                st.error(
                    "❌ Google's Gemini service is currently overloaded. "
                    "Please try again later."
                )

            elif error_code == 429:

                st.error(
                    "❌ Gemini API request limit reached. "
                    "Please check your API quota and try again later."
                )

            else:

                st.error("❌ An error occurred during medicine analysis.")

                st.exception(e)

        finally:

            st.warning(
                "⚠️ This information is for general educational purposes. "
                "Do not use it as a substitute for advice from a doctor "
                "or pharmacist. Always verify medicine information "
                "with a qualified healthcare professional."
            )
