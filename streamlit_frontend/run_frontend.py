#!/usr/bin/env python3
"""
Streamlit Frontend Launcher
Automatically skips the email prompt and starts the app
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting Kaggle Competition Assistant Frontend...")
    
    # Set environment variables to skip Streamlit onboarding
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    env['STREAMLIT_THEME_BASE'] = 'light'
    
    try:
        # Start Streamlit with specific configuration
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.headless', 'true',
            '--global.developmentMode', 'false',
            '--browser.gatherUsageStats', 'false'
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print("🌐 Streamlit will be available at: http://localhost:8501")
        print("📧 Press Enter to skip email prompt if it appears...")
        
        # Run the command
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())