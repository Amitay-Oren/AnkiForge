import os
import sys
sys.path.append('/home/ubuntu')

# Create a test .env file with placeholder values for testing
def create_test_env():
    env_content = """
# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
REPLICATE_API_KEY=your_replicate_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
FORVO_API_KEY=your_forvo_api_key_here

# Anki MCP Server settings
ANKI_MCP_SERVER_URL=http://localhost:8765
"""
    with open('/home/ubuntu/AnkiForge/.env', 'w') as f:
        f.write(env_content)
    print("Created test .env file with placeholder values")

# Test the Streamlit app can start without errors
def test_streamlit_startup():
    print("=== Testing Streamlit App Startup ===")
    # Create a simple test script that imports the app
    test_script = """
import sys
sys.path.append('/home/ubuntu')
from AnkiForge.app import main

# Just test that the app can be imported without errors
print("Streamlit app imported successfully")
"""
    with open('/home/ubuntu/AnkiForge/streamlit_test.py', 'w') as f:
        f.write(test_script)
    
    # Run the test script
    os.system('python3 /home/ubuntu/AnkiForge/streamlit_test.py')
    print("=== Streamlit App Startup Test Complete ===")

if __name__ == "__main__":
    create_test_env()
    test_streamlit_startup()
