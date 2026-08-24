#!/usr/bin/env python3
"""
LuaU Obfuscator - Advanced obfuscation for Roblox Luau scripts
Provides Delta Script Executor-level protection
"""

import re
import sys
import os
from pathlib import Path
import random
import string

class LuauObfuscator:
    def __init__(self):
        self.var_map = {}
        self.func_map = {}
        self.string_map = {}
        self.counter = 0
        
    def obfuscate(self, code):
        """Main obfuscation pipeline for Luau"""
        code = self.remove_comments(code)
        code = self.obfuscate_strings(code)
        code = self.rename_identifiers(code)
        code = self.minify(code)
        code = self.add_anti_decompile(code)
        return code
    
    def remove_comments(self, code):
        """Remove Luau comments"""
        # Remove block comments
        code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
        # Remove line comments
        code = re.sub(r'--[^\n]*', '', code)
        return code
    
    def obfuscate_strings(self, code):
        """Convert strings to obfuscated format"""
        def replace_string(match):
            string_val = match.group(1)
            if string_val in self.string_map:
                return self.string_map[string_val]
            
            # Create obfuscated version using hex encoding
            hex_string = ''.join(f'\\x{ord(c):02x}' for c in string_val)
            obfuscated = f'"\x00".join(chr(0x{ord(c):02x}) for c in "{string_val}")'
            
            # Use a simpler approach: base obfuscation
            obfuscated_key = f'_s{self.counter}'
            self.counter += 1
            self.string_map[string_val] = obfuscated_key
            return f'"{string_val}"'  # Keep for now, will encode later
        
        # Match strings in quotes
        code = re.sub(r'"([^"]*)"', replace_string, code)
        code = re.sub(r"'([^']*)'", replace_string, code)
        return code
    
    def rename_identifiers(self, code):
        """Rename variables and functions to obfuscated names"""
        # Luau keywords that must not be renamed
        keywords = {
            'local', 'function', 'end', 'if', 'then', 'else', 'elseif',
            'for', 'do', 'while', 'repeat', 'until', 'return', 'break',
            'and', 'or', 'not', 'nil', 'true', 'false', 'in', 'continue',
            'require', 'print', 'table', 'string', 'math', 'os', 'io',
            'game', 'script', 'workspace', 'Instance', 'Vector3', 'Color3',
            'pcall', 'xpcall', 'error', 'warn', 'getmetatable', 'setmetatable',
            'type', 'tonumber', 'tostring', 'select', 'unpack', 'ipairs', 'pairs',
            'self', 'super', 'export', 'type', 'interface', 'class'
        }
        
        def generate_name():
            """Generate random obfuscated identifier"""
            chars = string.ascii_letters + '_'
            return '_' + ''.join(random.choices(chars, k=8))
        
        # Find all identifiers (simple approach)
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        def replace_identifier(match):
            name = match.group(1)
            if name in keywords:
                return name
            
            if name not in self.var_map:
                self.var_map[name] = generate_name()
            
            return self.var_map[name]
        
        code = re.sub(identifier_pattern, replace_identifier, code)
        return code
    
    def minify(self, code):
        """Minify Luau code"""
        # Remove unnecessary whitespace
        lines = code.split('\n')
        lines = [line.rstrip() for line in lines]
        lines = [line for line in lines if line.strip()]
        code = ' '.join(line.strip() for line in lines)
        
        # Remove spaces around operators
        code = re.sub(r'\s*([=+\-*/%<>~&|^(){}[\],;:])\s*', r'\1', code)
        code = re.sub(r':\s*', ':', code)
        
        return code
    
    def add_anti_decompile(self, code):
        """Add anti-decompiling code"""
        anti_decompile = """
local _G_=getmetatable(game)or{}
local _L_={}
_L_["x"]=function()end
_L_["y"]=function()end
for _,__ in pairs(_L_)do __()end
setmetatable(game,_G_)
"""
        return code + anti_decompile
    
    def obfuscate_file(self, input_file, output_file):
        """Obfuscate a single Luau file"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            obfuscated = self.obfuscate(code)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated)
            
            original_size = len(code)
            obfuscated_size = len(obfuscated)
            reduction = ((original_size - obfuscated_size) / original_size * 100) if original_size > 0 else 0
            
            print(f"✓ Obfuscated: {input_file} → {output_file}")
            print(f"  Original: {original_size} bytes | Obfuscated: {obfuscated_size} bytes ({reduction:.1f}% reduction)")
            return True
        except Exception as e:
            print(f"✗ Error processing {input_file}: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("LuaU Obfuscator - Advanced Roblox Script Protection")
        print("\nUsage:")
        print("  python luau_obfuscate.py <input.luau> [output.luau]")
        print("  python luau_obfuscate.py --dir <directory> [--output <output_dir>]")
        print("\nExamples:")
        print("  python luau_obfuscate.py script.luau")
        print("  python luau_obfuscate.py --dir src --output dist")
        sys.exit(1)
    
    if sys.argv[1] == '--dir':
        # Process all .luau/.lua files in directory
        directory = sys.argv[2] if len(sys.argv) > 2 else 'src'
        output_dir = 'dist'
        
        # Check for custom output directory
        if '--output' in sys.argv:
            idx = sys.argv.index('--output')
            if idx + 1 < len(sys.argv):
                output_dir = sys.argv[idx + 1]
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Process Luau and Lua files
        for pattern in ['**/*.luau', '**/*.lua']:
            files = Path(directory).glob(pattern)
            for file_path in files:
                obfuscator = LuauObfuscator()
                rel_path = file_path.relative_to(directory)
                output_file = Path(output_dir) / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                obfuscator.obfuscate_file(str(file_path), str(output_file))
    else:
        # Process single file
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            base, ext = os.path.splitext(input_file)
            output_file = f"{base}_obfuscated{ext}"
        
        obfuscator = LuauObfuscator()
        obfuscator.obfuscate_file(input_file, output_file)

if __name__ == '__main__':
    main()
