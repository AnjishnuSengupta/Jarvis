import os
import time
import hashlib
import sqlite3
import threading
import ast
import re
import urllib.request
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.data.logger import DB_PATH, init_db

MAX_FILE_SIZE = 250 * 1024

class CodeIndexer(FileSystemEventHandler):
    def __init__(self, watch_dirs):
        self.watch_dirs = watch_dirs
        self.file_hashes = {}
        self.debounce_timers = {}
        self.conn = None
        self.enrichment_cache = {}
        
        # Connect to DB
        init_db()
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        
        # Excludes
        self.exclude_dirs = {'.git', 'node_modules', 'venv', 'dist', 'build', '__pycache__', 'target', '.dart_tool'}
        self.exclude_exts = {'.env', '.pem', '.key', '.sqlite', '.db', '.pyc'}
        self.include_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.dart'}
        
    def should_index(self, file_path):
        if not os.path.isfile(file_path):
            return False
            
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return False
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.include_exts:
            return False
            
        parts = file_path.split(os.sep)
        if any(ex in parts for ex in self.exclude_dirs):
            return False
            
        name = os.path.basename(file_path).lower()
        if any(name.endswith(ex) for ex in self.exclude_exts):
            return False
        if "secret" in name or "credential" in name:
            return False
            
        return True
        
    def fetch_pypi_desc(self, pkg_name):
        if pkg_name in self.enrichment_cache:
            return self.enrichment_cache[pkg_name]
        try:
            req = urllib.request.Request(f"https://pypi.org/pypi/{pkg_name}/json", headers={'User-Agent': 'Jarvis-Indexer'})
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                desc = data.get('info', {}).get('summary', '')
                self.enrichment_cache[pkg_name] = desc
                return desc
        except Exception:
            self.enrichment_cache[pkg_name] = ""
            return ""

    def fetch_npm_desc(self, pkg_name):
        if pkg_name in self.enrichment_cache:
            return self.enrichment_cache[pkg_name]
        try:
            req = urllib.request.Request(f"https://registry.npmjs.org/{pkg_name}", headers={'User-Agent': 'Jarvis-Indexer'})
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                desc = data.get('description', '')
                self.enrichment_cache[pkg_name] = desc
                return desc
        except Exception:
            self.enrichment_cache[pkg_name] = ""
            return ""

    def process_python_file(self, content, file_path):
        chunks = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return chunks

        lines = content.split('\n')
        
        # Imports for enrichment
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
                    
        enrichment_text = ""
        for imp in set(imports):
            # Skip likely stdlib
            if imp not in ['os', 'sys', 'time', 'json', 're', 'math', 'datetime']:
                desc = self.fetch_pypi_desc(imp)
                if desc:
                    enrichment_text += f" Uses {imp}: {desc}."

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', len(lines))
                chunk_code = '\n'.join(lines[start:end])
                
                docstring = ast.get_docstring(node)
                desc = f"{os.path.basename(file_path)} - {node.name}"
                if docstring:
                    desc += f": {docstring.split(chr(10))[0]}"
                desc += enrichment_text
                
                chunks.append((desc, chunk_code))
                
        # Fallback if no functions/classes
        if not chunks:
            desc = f"{os.path.basename(file_path)} script" + enrichment_text
            chunks.append((desc, content))
            
        return chunks

    def process_js_file(self, content, file_path):
        chunks = []
        pattern = re.compile(
            r'((?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(.*?\)\s*\{.*?^\})'
            r'|((?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(.*?\)\s*=>\s*\{.*?^\})'
            r'|((?:export\s+)?class\s+(\w+)\s*\{.*?^\})',
            re.MULTILINE | re.DOTALL
        )
        
        # Regex for imports
        import_pattern = re.compile(r'from\s+[\'"]([^\.\/][^\'"]+)[\'"]')
        imports = import_pattern.findall(content)
        
        enrichment_text = ""
        for imp in set(imports):
            pkg = imp.split('/')[0] # handle @scope/pkg separately if needed, but this is fine for basic
            desc = self.fetch_npm_desc(pkg)
            if desc:
                enrichment_text += f" Uses {pkg}: {desc}."

        matches = pattern.finditer(content)
        for match in matches:
            chunk_code = match.group(0)
            name = match.group(2) or match.group(4) or match.group(6)
            desc = f"{os.path.basename(file_path)} - {name}" + enrichment_text
            chunks.append((desc, chunk_code))
            
        if not chunks:
            desc = f"{os.path.basename(file_path)} script" + enrichment_text
            chunks.append((desc, content))
            
        return chunks

    def process_dart_file(self, content, file_path):
        chunks = []
        pattern = re.compile(
            r'(class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+\w+(?:,\s*\w+)*)?\s*\{.*?^\})'
            r'|((?:[\w<>]+\s+)?(\w+)\s*\([^)]*\)(?:\s+async\*?)?\s*\{.*?^\})',
            re.MULTILINE | re.DOTALL
        )
        
        matches = pattern.finditer(content)
        for match in matches:
            chunk_code = match.group(0)
            name = match.group(2) or match.group(4)
            desc = f"{os.path.basename(file_path)} - {name}"
            chunks.append((desc, chunk_code))
            
        if not chunks:
            desc = f"{os.path.basename(file_path)} script"
            chunks.append((desc, content))
            
        return chunks

    def index_file(self, file_path):
        if not self.should_index(file_path):
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return
            
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if self.file_hashes.get(file_path) == file_hash:
            return
        self.file_hashes[file_path] = file_hash
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            chunks = self.process_python_file(content, file_path)
            lang = 'python'
        elif ext == '.dart':
            chunks = self.process_dart_file(content, file_path)
            lang = 'dart'
        else:
            chunks = self.process_js_file(content, file_path)
            lang_map = {'.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript'}
            lang = lang_map.get(ext, 'javascript')
            
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM code_snippets WHERE source_path = ?", (file_path,))
        
        for desc, chunk_code in chunks:
            cursor.execute("INSERT INTO code_snippets (description, code, source_path, language) VALUES (?, ?, ?, ?)",
                           (desc, chunk_code, file_path, lang))
                           
        self.conn.commit()

    def on_modified(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path in self.debounce_timers:
            self.debounce_timers[file_path].cancel()
            
        timer = threading.Timer(5.0, self.index_file, args=[file_path])
        self.debounce_timers[file_path] = timer
        timer.start()
        
    def on_created(self, event):
        self.on_modified(event)
        
    def initial_sweep(self):
        print("[Indexer] Running initial sweep...")
        for watch_dir in self.watch_dirs:
            for root, dirs, files in os.walk(watch_dir):
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                for file in files:
                    self.index_file(os.path.join(root, file))
        print("[Indexer] Initial sweep complete.")

def start_background_indexer():
    watch_dirs = [os.path.expanduser("~/Documents")]
    indexer = CodeIndexer(watch_dirs)
    
    sweep_thread = threading.Thread(target=indexer.initial_sweep, daemon=True)
    sweep_thread.start()
    
    observer = Observer()
    for d in watch_dirs:
        if os.path.exists(d):
            observer.schedule(indexer, d, recursive=True)
            
    observer.start()
    return observer
