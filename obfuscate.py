#!/usr/bin/env python3
"""
Lua Obfuscator - Minifies and obfuscates Lua code
Similar to Delta Script Executor protection
"""

import re
import sys
import os
from pathlib import Path

class LuaObfuscator:
    def __init__(self):
        self.var_map = {}
        self.var_counter = 0
        self.obfuscated_vars = set()
        
    def obfuscate(self, code):
        """Main obfuscation pipeline"""
        code = self.remove_comments(code)
        code = self.minify(code)
        code = self.rename_variables(code)
        code = self.add_junk_code(code)
        return code
    
    def remove_comments(self, code):
        """Remove Lua comments"""
        # Remove single-line comments
        code = re.sub(r'--\[=*\[(.|\n)*?\]=*\]', '', code)  # Block comments
        code = re.sub(r'--[^\n]*', '', code)  # Line comments
        return code
    
    def minify(self, code):
        """Remove unnecessary whitespace and newlines"""
        # Remove leading/trailing whitespace
        lines = code.split('\n')
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]  # Remove empty lines
        code = '\n'.join(lines)
        
        # Remove spaces around operators
        code = re.sub(r'\s*([=+\-*/%<>~&|^(){}[\],;:])\s*', r'\1', code)
        code = re.sub(r'\s+', ' ', code)  # Collapse multiple spaces
        
        return code
    
    def rename_variables(self, code):
        """Rename variables to single letters/numbers"""
        # Find all variable assignments and usages
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        # Keywords that shouldn't be renamed
        keywords = {
            'local', 'function', 'end', 'if', 'then', 'else', 'elseif',
            'for', 'do', 'while', 'repeat', 'until', 'return', 'break',
            'and', 'or', 'not', 'nil', 'true', 'false', 'in',
            'require', 'print', 'table', 'string', 'math', 'os', 'io',
            'game', 'script', 'workspace', 'Instance', 'Vector3', 'Color3'
        }
        
        def generate_obfuscated_name():
            """Generate obfuscated variable names"""
            name = ''
            num = self.var_counter
            while True:
                name = chr(97 + (num % 26)) + name
                num //= 26
                if num == 0:
                    break
            self.var_counter += 1
            return name
        
        def replace_var(match):
            var = match.group(1)
            if var in keywords or var in self.obfuscated_vars:
                return var
            if var not in self.var_map:
                self.var_map[var] = generate_obfuscated_name()
            self.obfuscated_vars.add(var)
            return self.var_map[var]
        
        code = re.sub(var_pattern, replace_var, code)
        return code
    
    def add_junk_code(self, code):
        """Add junk/anti-decompile code"""
        junk = """
local _ = function() end;
local __ = {};
for i=1,1 do __ = nil end;
local ___ = (function()end)();
"""
        return code + junk
    
    def obfuscate_file(self, input_file, output_file):
        """Obfuscate a single file"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            obfuscated = self.obfuscate(code)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated)
            
            print(f"✓ Obfuscated: {input_file} → {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error processing {input_file}: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python obfuscate.py <input.lua> [output.lua]")
        print("       python obfuscate.py --dir <directory>")
        sys.exit(1)
    
    obfuscator = LuaObfuscator()
    
    if sys.argv[1] == '--dir':
        # Process all .lua files in directory
        directory = sys.argv[2] if len(sys.argv) > 2 else 'src'
        output_dir = 'dist'
        
        os.makedirs(output_dir, exist_ok=True)
        
        lua_files = Path(directory).glob('**/*.lua')
        for lua_file in lua_files:
            obfuscator = LuaObfuscator()  # Reset for each file
            rel_path = lua_file.relative_to(directory)
            output_file = Path(output_dir) / rel_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            obfuscator.obfuscate_file(str(lua_file), str(output_file))
    else:
        # Process single file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.lua', '_obfuscated.lua')
        obfuscator.obfuscate_file(input_file, output_file)

if __name__ == '__main__':
    main()
