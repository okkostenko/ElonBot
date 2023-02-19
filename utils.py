import datetime
from tqdm.notebook import tqdm_notebook
import snscrape.modules.twitter as sntwitter
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import re


global today
today=datetime.datetime.strftime(datetime.date.today(), '%Y-%m-%d')

def search(username='elonmusk', text='', since='', until='', retweet=''):
    global filename
    q=text

    if username!='':
        q+=f'from:{username}'
    if until=='':
        until=today
        q+=f' until:{until}'
    if since=='':
        since=datetime.datetime.strftime(datetime.date(2010, 1, 1), '%Y-%m-%d')
        q+=f' since:{since}'
    if retweet=='y':
        q+=f' exlude:retweets'
    
    if username!='' and text!='':
        filename=f' {since}_{until}_{username}_{text}.csv'
    elif username!='':
        filename=f' {since}_{until}_{username}.csv'
    else:
        filename=f' {since}_{until}_{text}.csv'

    print(filename)
    return q

def save(tweet_df, filename, day=today):
    day=datetime.date.today()
    data_dir=f'./data/{day}'
    os.makedirs(data_dir, exist_ok=True)
    tweet_df.to_csv(os.path.join(data_dir, filename))

def get_tweets(username='elonmusk'):
    q=search(username=username)
    elon_tweets=[]

    for i, tweet in enumerate(tqdm_notebook(sntwitter.TwitterSearchScraper(q).get_items())):
        elon_tweets.append([tweet.id, tweet.date, tweet.url, tweet.user.username, tweet.rawContent])

    tweet_df=pd.DataFrame(elon_tweets, columns=['ID', 'Date', 'Url', 'UserName', 'Text'])
    save(tweet_df)
    return tweet_df

def remove_mentioned(data):
    data=pd.read_csv(f'./data/{today}/clean_elon.csv')
    new_tweets=list(map(lambda x: re.sub(r'(\s)@\w+|(^)@\w+|(\s)http://\S+|(^)http://\S+|(\s)https://\S+|(^)https://\S+|', '', x), data['Text']))
    new_tweets=list(map(lambda x: x.replace(r'/\r?\n|\r/g', ""), new_tweets))
    new_tweets=pd.DataFrame(new_tweets, columns=['Text'])
    return new_tweets

def drop_na(new_file=True):
    clean_elon=pd.read_csv(f'./data/{today}/clean_elon.csv')
    clean_elon.dropna(inplace=True)
    if new_file:
        name='clean_elon_drop'
    else:
        name='clean_elon'
    save(clean_elon['Text'], f'{name}.csv')

def add_context():
    elon_tweets=pd.read_csv(f'/data/{today}/clean_elon.csv')

    contexted=[]
    n=7

    for i in range(n, len(elon_tweets['Text'])):
        row=[]
        prev=i-1-n
        for j in range(i, prev, -1):
            row.append(elon_tweets['Text'][j])
        contexted.append(row)
    columns=['response', 'context']
    columns=columns+['context/'+str(i) for i in range(n-1)]

    df=pd.DataFrame.from_records(contexted, columns=columns)

    trn_df, val_df=train_test_split(df, test_size=0.1)
    return trn_df, val_df