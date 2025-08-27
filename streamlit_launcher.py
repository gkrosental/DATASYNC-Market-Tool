"""
DATASYNC Market Tool - Streamlit Launcher
Simple launcher for the web interface
"""
import streamlit as st
import os
import sys

# Add paths
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import and run the main app
try:
    from ui.streamlit_app import main
    main()
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    st.error(f"Error: {e}")
    st.error("Please check the application logs for more details.")
