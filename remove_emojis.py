import re

file_path = r'c:\Misc\Dataengineering\Projects\agentic-ai-foundations\roadmap.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix spacing issues left by removing emojis
replacements = {
    '##  ': '## ',
    '### ** ': '### **',
    '** Resources:**': '**Resources:**',
    '** Practice:**': '**Practice:**',
    '** Deliverable:**': '**Deliverable:**',
    '** Deliverables:**': '**Deliverables:**',
    '** Project:': '**Project:',
    '** Hands-on:**': '**Hands-on:**',
    '** Exercise:**': '**Exercise:**',
    '** Mini Project:**': '**Mini Project:**'
}

for old, new in replacements.items():
    text = text.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
