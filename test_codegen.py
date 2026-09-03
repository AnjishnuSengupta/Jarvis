import sys
import os

from src.tools.codegen import execute_codegen

def test():
    print("Testing Landing Page...")
    res1 = execute_codegen({"project_type": "landing page with a contact form"})
    print(res1)
    
    print("\nTesting Node Express API...")
    res2 = execute_codegen({"project_type": "node express server"})
    print(res2)
    
    print("\nTesting Python Script...")
    res3 = execute_codegen({"project_type": "simple python script"})
    print(res3)

if __name__ == "__main__":
    test()
