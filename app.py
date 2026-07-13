if st.button("Run Comprehensive AI Analysis"):
    if not symptoms and not uploaded_image:
        st.warning("Please provide symptoms or an image.")
    else:
        try:
            with st.spinner('AI is analyzing the clinical data...'):
                # Force a timeout check and clear error handling
                response = client.models.generate_content(
                    model="gemini-2.0-flash", # Use the latest stable model
                    contents=f"Analyze these symptoms: {symptoms}"
                )
                st.write("### Diagnostic Result:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.write("Check your logs in 'Manage app' for specific connectivity errors.")
