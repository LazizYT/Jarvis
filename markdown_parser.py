# markdown_parser.py
import re

def parse_markdown(text):
    code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)
    for code in code_blocks:
        text = text.replace(f'```{code}```', f"[CODE]{code}[/CODE]")
    text = re.sub(r'\*\*(.*?)\*\*', r"[B]\1[/B]", text)
    text = re.sub(r'\*(.*?)\*', r"[I]\1[/I]", text)
    return text
