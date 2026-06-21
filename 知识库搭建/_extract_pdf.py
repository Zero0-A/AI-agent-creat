import pdfplumber, os
base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, '关于公布湖北工业大学2025年度学科竞赛指南的通知（20250509）.pdf')
out = os.path.join(base, '_pdf_text.txt')
with pdfplumber.open(path) as doc, open(out, 'w', encoding='utf-8') as f:
    for i,p in enumerate(doc.pages):
        f.write(f'--- Page {i+1} ---\n')
        f.write((p.extract_text() or '') + '\n\n')
print('OK pages:', len(doc.pages))
