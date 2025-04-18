#!/bin/bash

# AnkiForge Startup Script

echo "Starting AnkiForge..."

# Check if anki-mcp-server is running
if ! pgrep -f "anki-mcp-server" > /dev/null; then
    echo "Starting anki-mcp-server..."
    anki-mcp-server &
    echo "Please make sure Anki is running in the background."
    sleep 2
else
    echo "anki-mcp-server is already running."
fi

# Start the Streamlit app
echo "Starting AnkiForge Streamlit interface..."
cd "$(dirname "$0")"
streamlit run app.py
