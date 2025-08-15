import streamlit as st
import requests
import pandas as pd
import json

# Streamlit UI
st.title("Sales Prediction App")
st.write("Enter advertisement spend (in thousands of dollars):")

# Input fields
tv = st.number_input("TV", min_value=0.0, value=100.0)
radio = st.number_input("Radio", min_value=0.0, value=25.0)
newspaper = st.number_input("Newspaper", min_value=0.0, value=10.0)

if st.button("Predict"):
    # Prepare input as DataFrame, convert to JSON
    input_data = pd.DataFrame([{
        "TV": tv,
        "Radio": radio,
        "Newspaper": newspaper
    }])
    
    json_data = json.dumps({"inputs": input_data.to_dict(orient="records")})

    # Send request to model endpoint
    try:
        response = requests.post(
            url="http://localhost:8000/invocations",
            headers={"Content-Type": "application/json"},
            data=json_data
        )
        
        if response.status_code == 200:
            json_data = response.json()
            predicted_value = json_data["predictions"][0]

            # st.success(f"Predicted Sales: {prediction:.2f} (in thousands of units)")
            st.success(f"Predicted Sales: {predicted_value:.2f} (in thousands of units)")
        else:
            st.error(f"Prediction failed. Status code: {response.status_code}")
            st.text(response.text)
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to model server at http://localhost:8000/invocations")

#streamlit run app.py
