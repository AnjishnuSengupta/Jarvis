import os
import subprocess
import time
import shutil

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace"))

def execute_codegen(slots):
    project_type = slots.get("project_type", "react app").lower()
    
    # Generate a unique directory name
    timestamp = int(time.time())
    project_name = f"project_{timestamp}"
    
    if "landing page" in project_type:
        project_name = f"landing_page_{timestamp}"
    elif "react" in project_type:
        project_name = f"react_app_{timestamp}"
        
    project_path = os.path.join(WORKSPACE_DIR, project_name)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    try:
        # We will use Vite for almost all generic web requests for now
        print(f"  [Codegen] Scaffolding {project_type} in {project_path}...")
        
        # Execute npx create-vite
        subprocess.run(
            ["npx", "-y", "create-vite@latest", project_name, "--template", "react"],
            cwd=WORKSPACE_DIR,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # If it's a landing page, we can inject a basic App.jsx
        if "landing page" in project_type:
            app_jsx_path = os.path.join(project_path, "src", "App.jsx")
            landing_page_code = """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to Your New Landing Page</h1>
        <p>Built automatically by Jarvis.</p>
        <button onClick={() => alert('Contact form coming soon!')}>Contact Us</button>
      </header>
    </div>
  );
}

export default App;
"""
            with open(app_jsx_path, "w") as f:
                f.write(landing_page_code)
                
        return {
            "status": "success", 
            "message": f"Successfully scaffolded {project_type} in workspace/{project_name}.", 
            "project_type": project_type
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "status": "error", 
            "message": f"Failed to scaffold project. Error: {e.stderr.decode()}",
            "project_type": project_type
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An unexpected error occurred: {str(e)}",
            "project_type": project_type
        }
