
import pandas as pd
import twitterscraper
import datetime as dt


def tw_scraper(hashtag, start_date, end_date):
    '''
    The maximum search for Twitter API is 72,000 tweets per hour
    Using twitterscraper module can scrape without this limitation
    But the maximum tweets per search on my machine is around 13,000
    
    This function recursively scrape tweets with twitterscraper
    of certain hashtag in smaller time period to avoid those constraints
    
    Inputs:
        hashtag: (string) a hashtag starts with #
        startdate: (datetime obj) start date (year, month, date)
        enddate: (datetime obj) end date (year, month, date)
        path: (string) archive path
    
    Ouput:
        df: (pandas dataframe) tweets in the time period
    '''

    if end_date > start_date+dt.timedelta(days=5):
        med_date = start_date + dt.timedelta(days=5)
        tweets = twitterscraper.query_tweets(hashtag, begindate=start_date, enddate=med_date)
        df = pd.DataFrame(t.__dict__ for t in tweets)
        return pd.concat([df,tw_scraper(hashtag, med_date+dt.timedelta(days=1), end_date)])
    
    else:
        tweets = twitterscraper.query_tweets(hashtag, begindate=start_date, enddate=end_date)
        df = pd.DataFrame(t.__dict__ for t in tweets)
        return df


def save_clean_tweets(df, filename, path="/Users/chengyahan/Desktop/"):
    df = df[~df["tweet_url"].apply(tuple).duplicated()]
    path = path + filename + ".csv"
    df.to_csv(path, index=False)


# ## Case example

metoo = tw_scraper("#metoo", dt.date(2017, 9, 21), dt.date(2017, 11, 21))
save_clean_tweets(metoo, "metoo")


coronavirus = tw_scraper("#coronavirus", dt.date(2017, 9, 21), dt.date(2017, 11, 21))
save_clean_tweets(coronavirus, "coronavirus")


ivoted = tw_scraper("#IVoted", dt.date(2017, 9, 21), dt.date(2017, 11, 21))
save_clean_tweets(ivoted, "ivoted")



# ### Delete corrupted rows


def clean_up_file(filename, path="/Users/chengyahan/Desktop/"):
    path = path + filename + ".csv"
    df = pd.read_csv(path)
    for i in range(len(df)):
        try:
            float1 = float(df.loc[i, 'likes'])
            float2 = float(df.loc[i, 'replies'])
            float3 = float(df.loc[i, 'retweets'])
        except ValueError:
            print('Line {i} is corrupt!'.format(i = i))
            corrupt_list.append(i)
    
    df = df.drop(corrupt_list)
    # overwrite old file
    df.to_csv(path, index=False)

