import streamlit as st
import json
import requests
import time

st.set_page_config(page_title="EPMS Load Test Portal", layout="centered")
st.title("🚀 EPMS Authentication Load Test Portal")
st.write("Generate real k6 performance reports independently without running terminal scripts.")

# Global Configuration Parameters - Update these to point to your repository
GITHUB_OWNER = "neelunadkat"     # Your exact username visible in the repo URL
GITHUB_REPO = "load-testing"     # From your screenshot path: /mount/src/load-testing/


# Web Form Fields
vus = st.number_input("Enter Number of Virtual Users (VUs)", min_value=1, max_value=50, value=10)
duration = st.text_input("Enter Test Duration (e.g., 30s, 1m)", value="30s")

st.subheader("📋 Target User Credentials")
default_json = '[\n  {"email": "test1@example.com", "password": "password123"},\n  {"email": "test2@example.com", "password": "password123"}\n]'
user_input = st.text_area("Paste User JSON Data here:", value=default_json, height=150)

# Securely extract the token from Streamlit environment variables
if "GITHUB_TOKEN" in st.secrets:
    token = st.secrets["GITHUB_TOKEN"]
else:
    st.warning("⚠️ GITHUB_TOKEN missing from Streamlit Secret dashboard panel.")
    token = None

if st.button("▶️ Run Load Test & Generate Report"):
    if not token:
        st.error("Cannot proceed. Setup connection token in Streamlit cloud secrets first.")
    else:
        try:
            # Validate JSON data input configuration
            parsed_users = json.loads(user_input)
            
            # API endpoint layout to trigger GitHub dispatch sequence
            url = f"https://github.com{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {
                "event_type": "streamlit_trigger",
                "client_payload": {
                    "vus": int(vus),
                    "duration": str(duration),
                    "users_json": user_input
                }
            }
            
            with st.spinner("⚡ Connecting to cloud test servers..."):
                response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 204:
                st.info("🔄 Load test triggered successfully on GitHub Actions! Running...")
                
                # Dynamic tracking loop interface loop
                status_container = st.empty()
                progress_bar = st.progress(0)
                
                # Polling GitHub API for test completion
                runs_url = f"https://github.com{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs?event=repository_dispatch&per_page=1"
                
                time.sleep(5)  # Wait for workflow initialization
                run_id = None
                
                for attempt in range(20):
                    run_resp = requests.get(runs_url, headers=headers).json()
                    if run_resp.get("workflow_runs"):
                        run_id = run_resp["workflow_runs"][0]["id"]
                        status = run_resp["workflow_runs"][0]["status"]
                        status_container.markdown(f"**Current Pipeline Status:** `{status.upper()}`")
                        
                        if status == "completed":
                            conclusion = run_resp["workflow_runs"][0]["conclusion"]
                            if conclusion == "success":
                                st.success("✅ Load Test Complete! Fetching your HTML report dashboard...")
                                break
                            else:
                                st.error("❌ The backend load test pipeline failed. Check your credentials.")
                                st.stop()
                    
                    progress_bar.progress(min((attempt + 1) * 5, 95))
                    time.sleep(8)
                
                # Download and serve the true generated artifact report 
                if run_id:
                    artifact_url = f"https://github.com{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}/artifacts"
                    art_resp = requests.get(artifact_url, headers=headers).json()
                    
                    if art_resp.get("artifacts"):
                        art_id = art_resp["artifacts"][0]["id"]
                        download_url = f"https://github.com{GITHUB_OWNER}/{GITHUB_REPO}/actions/artifacts/{art_id}/zip"
                        
                        # Download zip file and extract the inner index data stream
                        file_response = requests.get(download_url, headers=headers)
                        
                        import zipfile
                        import io
                        
                        with zipfile.ZipFile(io.BytesIO(file_response.content)) as z:
                            html_content = z.read("final_summary.html")
                        
                        progress_bar.progress(100)
                        
                        st.download_button(
                            label="📥 Download HTML Summary Report",
                            data=html_content,
                            file_name=f"summary_{vus}VUs.html",
                            mime="text/html"
                        )
                    else:
                        st.error("Could not fetch the generated report data file.")
            else:
                st.error(f"Failed to communicate with execution server: {response.text}")
                
        except json.JSONDecodeError:
            st.error("Invalid JSON structural syntax provided. Please check your data fields.")
