import os, arxiv

def download_from_arxiv(path_paper, paper_id, download_source, download_pdf):
    paper_id = d['entry_id'].split('/')[-1]
    paper_tar = f'{paper_id}.tax.gz'
    paper_pdf = f'{paper_id}.pdf'

    if not os.path.exists(os.path.join(path_paper, paper_tar)) and download_source:
        paper = next(arxiv.Search(id_list=[paper_id]).results())
        # Download the archive to the PWD with a custom filename.
        paper.download_source(dirpath = path_paper, filename=paper_tar)
        # Download the archive to a specified directory with a custom filename.
        #paper.download_source(dirpath="./", filename="downloaded-paper.tar.gz")
    if not os.path.exists(os.path.join(path_paper, paper_pdf)) and download_pdf:
        paper.download_pdf(dirpath = path_paper, filename=paper_pdf)