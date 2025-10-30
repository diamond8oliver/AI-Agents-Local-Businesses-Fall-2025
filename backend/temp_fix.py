cat > temp_fix.py << 'EOF'
cat > temp_fix.py << 'EOF'

import sys
with open('src/api/main.py', 'r') as f:
    content = f.read()
content = content.replace('settings = get_settings()', 'print("APP STARTING - THIS SHOULD APPEAR IN LOGS", flush=True)\nsettings = get_settings()')
with open('src/api/main.py', 'w') as f:
    f.write(content)
