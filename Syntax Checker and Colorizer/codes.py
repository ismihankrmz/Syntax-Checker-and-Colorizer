import tkinter as tk
from tkinter import scrolledtext
import re

def tokenize(line):
    if line.strip().startswith('#'):
        return [], ""

    token_specification = [
        ('COMMENT', r'#.*'),
        ('NUMBER', r'\d+(\.\d*)?'),
        ('STRING', r'"[^"]*"'),
        ('IDENTIFIER', r'[a-zA-Z_ğüşöçıİĞÜŞÖÇ][a-zA-Z0-9_ğüşöçıİĞÜŞÖÇ]*'),
        ('OPERATOR', r'==|>=|<=|!=|>|<|='),
        ('SYMBOL', r'[{};]'),
        ('SKIP', r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    mo = get_token(line, pos)
    keywords = {
        'DATATYPE': ['sayı', 'metin'],
        'COMMAND': ['oluştur', 'yazdır', 'eğer', 'ise']
    }
    while mo:
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'NUMBER':
            tokens.append(('NUMBER', value))
        elif kind == 'STRING':
            tokens.append(('STRING', value))
        elif kind == 'IDENTIFIER':
            if value in keywords['DATATYPE']:
                tokens.append(('DATATYPE', value))
            elif value in keywords['COMMAND']:
                tokens.append(('COMMAND', value))
            else:
                tokens.append(('IDENTIFIER', value))
        elif kind == 'OPERATOR':
            tokens.append(('OPERATOR', value))
        elif kind == 'SYMBOL':
            tokens.append(('SYMBOL', value))
        elif kind == 'SKIP':
            pass
        elif kind == 'COMMENT':
            break
        elif kind == 'MISMATCH':
            return None, f"Hatalı karakter: {value}"
        pos = mo.end()
        mo = get_token(line, pos)
    if pos != len(line):
        return None, f"Satırda işlenemeyen kısım var: {line[pos:]}"
    return tokens, ""

def is_valid_identifier(name):
    return re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name) is not None

def parse_line(tokens):
    if not tokens:
        return True, ""

    if tokens[0][0] == "COMMENT":
        return True, ""

    if tokens[0][1] in ["sayı", "metin"]:
        if len(tokens) == 6 and tokens[1][1] == "oluştur" and tokens[2][0] == "IDENTIFIER" and is_valid_identifier(tokens[2][1]) and \
                tokens[3][1] == "=" and tokens[5][1] == ";":
            tip = tokens[0][1]
            deger_token = tokens[4]

            if tip == "sayı" and deger_token[0] == "NUMBER":
                return True, ""
            elif tip == "metin" and deger_token[0] == "STRING":
                return True, ""
            else:
                return False, f"Tip uyuşmazlığı: {tip} için uygun olmayan değer"
        else:
            return False, "Hatalı değişken tanımlama veya geçersiz isim"

    if tokens[0][1] == "yazdır":
        if len(tokens) == 3 and (tokens[1][0] in ["IDENTIFIER", "STRING"]) and tokens[2][1] == ";":
            if tokens[1][0] == "IDENTIFIER" and not is_valid_identifier(tokens[1][1]):
                return False, "Geçersiz değişken adı"
            return True, ""
        else:
            return False, "Hatalı yazdırma komutu, satır sonu ';' eksik olabilir,yazdırılacak ifade eksik olabilir"

    if tokens[0][1] == "eğer":
        if len(tokens) == 6 and tokens[1][0] == "IDENTIFIER" and is_valid_identifier(tokens[1][1]) and tokens[2][0] == "OPERATOR" and \
                tokens[3][0] == "NUMBER" and tokens[4][1] == "ise" and tokens[5][1] == "{":
            if tokens[2][1] in ["==", ">", "<"]:
                return True, ""
            else:
                return False, "Koşulda karşılaştırma operatörü hatalı (==, >, < olmalı)"
        else:
            return False, "Hatalı koşul ifadesi"

    if len(tokens) == 1 and tokens[0][1] == "}":
        return True, ""

    return False, "Anlaşılamayan ifade veya sözdizimi hatası"

token_colors = {
    'DATATYPE': 'blue',
    'COMMAND': 'dark violet',
    'STRING': 'green',
    'NUMBER': 'orange',
    'OPERATOR': 'purple',
    'IDENTIFIER': 'black'
}

def highlight_and_analyze(event=None):
    code = input_text.get("1.0", tk.END)
    lines = code.strip().split('\n')
    output_text.delete("1.0", tk.END)
    input_text.tag_remove("all", "1.0", tk.END)

    for i, line in enumerate(lines):
        line_start = f"{i + 1}.0"
        tokens, err = tokenize(line)

        if err:
            output_text.insert(tk.END, f"Satır: {line}\nHata: {err}\n\n", "error")
            continue

        # Renklendirme
        offset = 0
        for token_type, value in tokens:
            color = token_colors.get(token_type, None)
            if color:
                idx_start = f"{i + 1}.{offset}"
                idx_end = f"{i + 1}.{offset + len(value)}"
                input_text.tag_add(token_type, idx_start, idx_end)
                input_text.tag_config(token_type, foreground=color)
            offset += len(value)

        # Geçerlilik kontrolü
        valid, err_msg = parse_line(tokens)
        output_text.insert(tk.END, f"SATIR: {line}\nTOKENS: {tokens}\n")
        if not valid:
            output_text.insert(tk.END, f"Hata: {err_msg}\n", "error")
        output_text.insert(tk.END, "\n")

### --- Geliştirilmiş Arayüz ---

root = tk.Tk()
root.title("SÖZ DİZİMİ DENETLEYİCİ VE RENKLENDİRİCİ")
root.geometry("800x700")
root.configure(bg="#f0f0f0")

font_set = ("Consolas", 14)

tk.Label(root, text="KODUNUZU GİRİN:", font=("Arial", 12, "bold"), bg="#e98484").pack(pady=(10, 0))
input_text = scrolledtext.ScrolledText(root, height=12, width=90, font=font_set, bg="#e6f0ff")
input_text.pack(pady=5)
input_text.bind("<KeyRelease>", highlight_and_analyze)

tk.Label(root, text="SONUÇ:", font=("Arial", 12, "bold"), bg="#e98484").pack(pady=(10, 0))
output_text = scrolledtext.ScrolledText(root, height=16, width=90, font=font_set, bg="#e6f0ff")
output_text.pack(pady=5)
output_text.tag_config("error", foreground="red")

highlight_and_analyze()
root.mainloop()
