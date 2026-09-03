import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.codegen import classify_project_kind, select_sections

def test_classify_project_kind():
    assert classify_project_kind("build a simple python script") == "python_script"
    assert classify_project_kind("create an express api") == "express_api"
    assert classify_project_kind("scaffold a node server") == "express_api"
    assert classify_project_kind("make me a todo app") == "vite_react_todo"
    assert classify_project_kind("create a landing page with a contact form") == "vite_react_landing"
    assert classify_project_kind("build a generic website") == "vite_react_landing"
    print("test_classify_project_kind passed")

def test_select_sections():
    sections = select_sections("make me a landing page with a contact form and pricing")
    assert sections == ["Hero", "ContactForm", "Pricing"]
    
    sections = select_sections("make me a portfolio with a gallery")
    assert sections == ["Hero", "Gallery"]
    
    sections = select_sections("generic react app")
    assert sections == ["Hero"]
    print("test_select_sections passed")

if __name__ == "__main__":
    test_classify_project_kind()
    test_select_sections()
    print("All pure function tests passed!")
