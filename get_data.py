from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from utils import save

n=7

def new_urls():
    search_url='https://elon-musk-interviews.com/category/english/'
    req=requests.get(search_url)
    soup=BeautifulSoup(req.text, 'html.parser')
    atags=soup.find_all('a', class_='more-link')
    hrefs=[link['href'] for link in atags]
    return hrefs

def scrape(urls):
    interviews=[]
    for url in urls:
        req=requests.get(url)
        soup=BeautifulSoup(req.text, 'html.parser')
        paragraphs=soup.find_all('p')
        text=[paragraph.text for paragraph in paragraphs]
        interviews.append(text)
    return interviews

def get_sentances(interview):
    sentances=[]
    for sentance in interview:
        sentance=re.sub(r'\([^)]*\)', '', sentance)
        sentance=sentance.split('. ')
        for s in sentance:
            if s=='' or s.startswith('Question from the audience: '):
                sentance.remove(s)
        if sentance!=[]:
            sentances.append(sentance) 
    sentances=sentances[2:-5]
    if [] in sentances:
        sentances.remove([])
    return sentances

def elon_lines(sentances):
    all = [(i, len(sentances[i])) for i in range(len(sentances))]
    result=[]
    for i in range(len(sentances)):
        print(sentances[i][0])
        if sentances[i][0].startswith('Elon:') or sentances[i][0].startswith('Elon Musk:'):
            result.append(i)
    idx=-1
    elon_sentances_idx=[]
    for par in all:
        for _ in range(par[1]):
            idx+=1
            if par[0] in result:
                elon_sentances_idx.append(idx)
    return elon_sentances_idx

def flatten(sentances, elon_sentances_idx):
    flat_list=[item for sublist in sentances for item in sublist]
    flat_list=flat_list[:elon_sentances_idx[-1]]
    return flat_list

def contexted(interview):
    sentances=get_sentances(interview)
    elon_sentances_idx=elon_lines(sentances)
    flat_list=flatten(sentances, elon_sentances_idx)
    rows=[]
    for i in range(len(flat_list), n-2, -1):
        if i not in elon_sentances_idx:
            continue
        row=[]
        for j in range(n):
            clean_line=re.sub(r'^[^:]*:', '', flat_list[i-j-1])
            row.append(clean_line)

        rows.append(row)
    return rows

def get_data():
    search_url='https://elon-musk-interviews.com/category/english/'
    req=requests.get(search_url)
    soup=BeautifulSoup(req.text, 'html.parser')
    atags=soup.find_all('a', class_='more-link')
    hrefs=[link['href'] for link in atags]

    urls=new_urls()
    interviews=scrape(urls)

    data=[]
    df=pd.DataFrame()
    data=contexted(interviews[1])
    df=df.append(data)

    save(df, 'elon_interview.csv')
    return df


if __name__=='__main__':
    get_data()