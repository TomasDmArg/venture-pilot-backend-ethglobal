import requests
import os

def test_team_upload():
    """
    Test the upload endpoint with a file containing team information
    """
    url = "http://localhost:8000/api/v1/analysis/project/upload"
    
    try:
        # Test file upload with team info
        with open("test_with_team.txt", "rb") as f:
            files = {"file": ("test_with_team.txt", f, "text/plain")}
            data = {"project_name": "ChatterPay"}
            
            response = requests.post(url, files=files, data=data)
            
            print("Status Code:", response.status_code)
            result = response.json()
            
            # Pretty print the response
            print("\n=== COMPLETE ANALYSIS ===")
            print(f"Project: {result.get('project_name', 'N/A')}")
            print(f"Summary: {result.get('summary', 'N/A')}")
            print(f"Viability Score: {result.get('viability_score', 'N/A')}/10")
            print(f"Recommendation: {result.get('recommendation', 'N/A')}")
            
            print(f"\n=== FOUNDERS ({len(result.get('founders', []))}) ===")
            for founder in result.get('founders', []):
                print(f"- {founder.get('name', 'N/A')}")
                print(f"  LinkedIn: {founder.get('linkedin', 'N/A')}")
                print(f"  GitHub: {founder.get('github', 'N/A')}")
                print(f"  Bio: {founder.get('bio', 'N/A')[:100]}...")
                print()
            
            print(f"\n=== RISK FACTORS ===")
            for risk in result.get('risk_factors', []):
                print(f"- {risk}")
            
            print(f"\n=== STRENGTHS ===")
            for strength in result.get('strengths', []):
                print(f"- {strength}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_team_upload() 