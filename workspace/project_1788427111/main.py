#!/usr/bin/env python3
import argparse

def main():
    parser = argparse.ArgumentParser(description="Auto-generated CLI script by Jarvis")
    parser.add_argument("--name", type=str, default="World", help="Who to greet")
    
    args = parser.parse_args()
    
    print(f"Hello, {args.name}! Your Python script is ready.")

if __name__ == "__main__":
    main()
