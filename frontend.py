import streamlit as st
import requests

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000/research"

st.title("Research Assistant")

# Input form
query = st.text_input("What can I help you with in your research?")

if st.button("Submit"):
    if query:
        with st.spinner("Researching..."):
            try:
                # Send request to FastAPI backend
                response = requests.post(BACKEND_URL, json={"query": query})
                response.raise_for_status()
                result = response.json()

                # Display results
                st.subheader("Research Results")
                st.write(f"**Topic:** {result['topic']}")
                st.write(f"**Summary:** {result['summary']}")
                st.write(f"**Tools Used:** {', '.join(result['tools_used'])}")
                st.write(f"**Sources:** {', '.join(result['sources'])}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a research query.")

# Optional: Add a button to clear the input
if st.button("Clear"):
    st.session_state.query = ""
    st.experimental_rerun()