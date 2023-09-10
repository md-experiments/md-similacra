from langchain.document_loaders import PyPDFLoader
import pandas as pd
import numpy as np

def is_numeric(txt):
    try:
        float(txt)
        return True
    except:
        return False

def is_title(t):
    spl_txt = t.split()
    if len(spl_txt):
        if is_numeric(spl_txt[0]):
            return True
        elif (len(spl_txt)<3) and (spl_txt[-1].lower() in ['abstract','references']):
            return True
        else:
            return False
    else:
        return False
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def get_ref_abs_range(ls_text):
    abs_lines = 0
    ref_lines = 0
    abstract_line = 0
    reference_line = len(ls_text)
    ref_lines_all = []
    for i, txt in enumerate(ls_text):
        spl_txt = txt.split()
        if len(spl_txt):
            if spl_txt[-1].lower() in ['abstract']:
                abstract_line = i
                abs_lines = abs_lines+1
                ref_lines_all.append(spl_txt[-1].lower())
            if spl_txt[-1].lower() in ['references']:
                reference_line = i
                ref_lines = ref_lines+1
                ref_lines_all.append(spl_txt[-1].lower())
    if (ref_lines>1) or (abs_lines>1) or (ref_lines==0) or (abs_lines==0):
        print(f'Missing/Multiple REFRN: found {ref_lines} or ABSTR: found {abs_lines}')
        print(ref_lines_all)
    return abstract_line, reference_line

def prep_docs(docs):
    pdf_lines = '\n'.join([d.page_content for d in docs]).split('\n')
    abstract_line, reference_line = get_ref_abs_range(pdf_lines)
    df_pdf = pd.DataFrame(pdf_lines[abstract_line:reference_line],columns=['body'])
    df_pdf['title'] = df_pdf['body'].apply(lambda x: x if is_title(x) else np.nan)
    df_pdf['title'] = df_pdf['title'].ffill()
    df_pdf = df_pdf[df_pdf['title']!=df_pdf['body']].copy()
    df_pdf['body'] = df_pdf['body'].apply(lambda x: x.strip()[:-1] if x.endswith('-') else 
                                        (x.strip() + "\n" if x.endswith(tuple('.?!')) else
                                        x.strip() + " "))
    
    paper_pdf = df_pdf.groupby('title', as_index=False).sum().to_dict(orient='records')
    df_pdf['body'] = df_pdf['body'].apply(lambda x: x.strip())
    return paper_pdf

"""
ls_files = files_in_dir('./data/arxiv/tar/',['.pdf'])
loader = PyPDFLoader(pdf_path)
pages = loader.load_and_split()
docs = loader.load()

paper_json = prep_docs(docs)
"""