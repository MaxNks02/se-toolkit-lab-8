import re

def run():
    # 1. Update docker-compose.yml
    with open('docker-compose.yml', 'r') as f:
        lines = f.readlines()
    
    out_lines = []
    in_nanobot = False
    
    for line in lines:
        # Detect the nanobot block
        if re.match(r'^\s*#\s*nanobot:', line):
            in_nanobot = True
            
        if in_nanobot:
            # Remove the first '#' and up to one trailing space, preserving leading spaces
            line = re.sub(r'^(\s*)# ?', r'\1', line)
            # Stop uncommenting when we hit an empty line
            if line.strip() == '':
                in_nanobot = False
        else:
            # Uncomment specific caddy dependency and env var
            if re.match(r'^\s*#\s*-\s*nanobot', line) or re.match(r'^\s*#\s*NANOBOT_WEBCHAT_CONTAINER_PORT', line):
                line = re.sub(r'^(\s*)# ?', r'\1', line)
                
        out_lines.append(line)
        
    with open('docker-compose.yml', 'w') as f:
        f.writelines(out_lines)

    # 2. Update caddy/Caddyfile
    with open('caddy/Caddyfile', 'r') as f:
        lines = f.readlines()
        
    out_lines = []
    in_ws = False
    
    for line in lines:
        if re.match(r'^\s*#\s*handle /ws/chat', line):
            in_ws = True
            
        if in_ws:
            line = re.sub(r'^(\s*)# ?', r'\1', line)
            if '}' in line:
                in_ws = False
                
        out_lines.append(line)
        
    with open('caddy/Caddyfile', 'w') as f:
        f.writelines(out_lines)

run()
print("✅ Successfully uncommented configurations with perfect YAML indentation!")
