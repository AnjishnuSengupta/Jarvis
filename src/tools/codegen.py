import os
import subprocess
import time
import shutil
import re
import threading
import queue

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace"))
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

SECTION_KEYWORDS = {
    "contact form": "ContactForm",
    "pricing": "Pricing",
    "gallery": "Gallery",
    "testimonial": "Testimonials",
}

def classify_project_kind(project_type_text: str) -> str:
    text = project_type_text.lower()
    if any(k in text for k in ["python script", "cli tool", "script"]):
        return "python_script"
    if any(k in text for k in ["express server", "express api", "rest api", "node server", "backend api"]):
        return "express_api"
    if any(k in text for k in ["todo app", "todo list", "task app"]):
        return "vite_react_todo"
    return "vite_react_landing"

def select_sections(project_type_text: str) -> list:
    text = project_type_text.lower()
    sections = ["Hero"]
    for keyword, component in SECTION_KEYWORDS.items():
        if keyword in text:
            sections.append(component)
    return sections

def start_and_get_url(cmd, cwd, regex):
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    q = queue.Queue()
    def enqueue_output(out, queue):
        for line in iter(out.readline, ''):
            queue.put(line)
        out.close()
        
    t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
    t.daemon = True
    t.start()
    
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            line = q.get_nowait()
            match = re.search(regex, line)
            if match:
                return match.group(1)
        except queue.Empty:
            time.sleep(0.1)
            
    return None

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
        project_kind = classify_project_kind(project_type)
        
        print(f"  [Codegen] Scaffolding {project_kind} in {project_path}...")
        
        # We will implement the dev server background launch next.
        # For now, let's implement the generation logic
        
        if project_kind in ["vite_react_landing", "vite_react_todo"]:
            subprocess.run(
                ["npx", "-y", "create-vite@latest", project_name, "--template", "react", "--no-interactive"],
                cwd=WORKSPACE_DIR,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # For vite_react_landing, we use composition
            if project_kind == "vite_react_landing":
                sections = select_sections(project_type)
                
                # Copy components
                components_dir = os.path.join(project_path, "src", "components")
                os.makedirs(components_dir, exist_ok=True)
                
                imports = []
                renders = []
                
                for component in sections:
                    src_comp = os.path.join(TEMPLATES_DIR, "vite_react_landing", "components", f"{component}.jsx")
                    dest_comp = os.path.join(components_dir, f"{component}.jsx")
                    if os.path.exists(src_comp):
                        shutil.copy(src_comp, dest_comp)
                        imports.append(f"import {component} from './components/{component}';")
                        renders.append(f"      <{component} />")
                        
                # Fill App.jsx
                template_path = os.path.join(TEMPLATES_DIR, "vite_react_landing", "App.jsx.template")
                app_jsx_path = os.path.join(project_path, "src", "App.jsx")
                
                if os.path.exists(template_path):
                    with open(template_path, "r") as f:
                        app_code = f.read()
                    
                    app_code = app_code.replace("{{IMPORTS}}", "\n".join(imports))
                    app_code = app_code.replace("{{SECTIONS}}", "\n".join(renders))
                    
                    with open(app_jsx_path, "w") as f:
                        f.write(app_code)
            else:
                # vite_react_todo
                components_dir = os.path.join(project_path, "src", "components")
                os.makedirs(components_dir, exist_ok=True)
                
                src_comp = os.path.join(TEMPLATES_DIR, "vite_react_todo", "components", "TodoApp.jsx")
                dest_comp = os.path.join(components_dir, "TodoApp.jsx")
                shutil.copy(src_comp, dest_comp)
                
                template_path = os.path.join(TEMPLATES_DIR, "vite_react_todo", "App.jsx.template")
                app_jsx_path = os.path.join(project_path, "src", "App.jsx")
                shutil.copy(template_path, app_jsx_path)
                
            # Install dependencies and start server
            subprocess.run(["npm", "install"], cwd=project_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            url = start_and_get_url(["npm", "run", "dev"], project_path, r'Local:\s+(http://localhost:\d+)')
            
            if url:
                return {"status": "success", "message": f"Successfully scaffolded {project_type} in workspace/{project_name}.", "project_type": project_type, "url": url}
            else:
                return {"status": "error", "message": f"Scaffolded {project_type}, but failed to detect dev server URL.", "project_type": project_type}
                
        elif project_kind == "express_api":
            os.makedirs(project_path, exist_ok=True)
            
            src_pkg = os.path.join(TEMPLATES_DIR, "express_api", "package.json.template")
            dest_pkg = os.path.join(project_path, "package.json")
            shutil.copy(src_pkg, dest_pkg)
            
            src_svr = os.path.join(TEMPLATES_DIR, "express_api", "server.js.template")
            dest_svr = os.path.join(project_path, "server.js")
            shutil.copy(src_svr, dest_svr)
            
            subprocess.run(["npm", "install"], cwd=project_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            url = start_and_get_url(["npm", "start"], project_path, r'listening on port (\d+)')
            
            if url:
                return {"status": "success", "message": f"Successfully scaffolded {project_type}.", "project_type": project_type, "url": f"http://localhost:{url}"}
            else:
                return {"status": "error", "message": f"Scaffolded {project_type}, but failed to detect dev server running.", "project_type": project_type}
                
        elif project_kind == "python_script":
            os.makedirs(project_path, exist_ok=True)
            src_script = os.path.join(TEMPLATES_DIR, "python_script", "script.py.template")
            dest_script = os.path.join(project_path, "main.py")
            shutil.copy(src_script, dest_script)
            os.chmod(dest_script, 0o755)
            
            return {"status": "success", "message": f"Successfully scaffolded {project_type} in workspace/{project_name}.", "project_type": project_type}
        
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
