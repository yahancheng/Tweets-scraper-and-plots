import pandas as pd
import datetime as dt
import re
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
pd.options.display.max_rows = 10



def read_tweets_file(filename, path="/Users/chengyahan/Desktop/"):
    '''
    Reads file contains tweets
    Inputs:
        filename: (str) file name
        path: (str) directory of the file
    Output:
        df: Pandas dataframe
    '''
    path = path + filename + ".csv"
    df = pd.read_csv(path, dtype={'retweets': "float64", 'likes': "float64", 'replies': "float64"})
    return df


def hash_list(series):
    '''
    Cleans up hashtags
    Input: 
        series: (pd.series) the column of hashtags
    Output:
        hash_list: (list) list of hashtags
    '''
    series = series.apply(lambda tags: str(tags).strip('[]').split(', '))
    hash_list = []
    for tag_list in series:
        tag_list = list(map(lambda x: x.strip("''"), tag_list))
        hash_list += tag_list
    return hash_list



def plot_wordcloud(output, color="Reds", size=(100, 80)):
    '''
    Plots word cloud
    Input:
        output: (list) list of words (hashtags)
        color: (str) the color of words in word cloud plot
        size: (tuple of integers) the width and length of the figure
    '''
    text = " ".join(output)
    wordcloud = WordCloud(max_font_size=50, max_words=1000, 
            colormap=color, background_color="white").generate(text)
    plt.figure(figsize=size)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def trans_date(timestp):
    '''
    Transforms string to datetime structure
    Input:
        timestp: (str) string of date
    Output:
        datetime object of year-month-day
    '''
    if type(timestp) == str:
        timestp = timestp.replace('/', "-")
        time = timestp.replace(' ', "-").replace(":", "-").split("-")
        date = tuple(map(int, time))[0:3]
        return dt.date(date[0], date[1], date[2])


def plot_day_freq(df, day_interval=10, n=2):
    '''
    Plots daily frequecy plot for a hashtag
    Inputs:
        df: (pd.dataframe) dataframe of tweets
        day_interval: (int) day interval of the ticker
        n: (int) number of peaks to tag, n < 50
    '''
    df.loc[:, "time"] = list(df.loc[:, "timestamp"].apply(trans_date))
    df_day = pd.DataFrame(df["time"].value_counts())
    df_day["date"] = df_day.index
    df_day.reset_index()
    day, freq = zip(*sorted(zip(df_day['date'], df_day['time'])))
    
    df_top = df_day.nlargest(50, 'time')
    
    date_ls = []
    num_ls = []
    for row in df_top.iterrows():
        date_in = False
        if date_ls:
            for date in date_ls:
                if date < row[0]+dt.timedelta(days=2) and date > row[0]-dt.timedelta(days=2):
                    date_in = True
                    break
        if not date_in:
            date_ls.append(row[1][1])
            num_ls.append((row[1][1], row[1][0]))
    
    plt.figure(figsize=(10, 8))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=day_interval))
    plt.plot(day, freq)

    for iters in num_ls[:n]:
        plt.text(iters[0], iters[1]+120, iters[0].strftime("%Y-%m-%d"))
    
    plt.gcf().autofmt_xdate()
    plt.show()



def find_KOL(df):
    '''
    Finds top 10 KOL of a hashtag by user's popular scores
    Popular score = # of likes + # of replies + 2 * # of retweets
    
    Input:
        df: (pd.dataframe) dataframe of tweets
    Output:
        df3.head(10): (pd.dataframe) dataframe of top 10 popular users
    '''
    df['pop_score'] = df['retweets'].apply(float)*2 + df['likes'].apply(float) + \
                      df['replies'].apply(float)
    
    df3 = pd.DataFrame({'user_id': df["user_id"].unique()})
    pop_score = []
    user_name = []
    for user in df3['user_id']:
        pop_score.append(sum(df.loc[df['user_id'] == user, 'pop_score']))
        if not df.loc[df['user_id'] == user, 'username'].empty:
            user_name.append(df.loc[df['user_id'] == user, 'username'].unique()[0])
        else:
            user_name.append(None)
    
    df3['username'] = user_name
    df3["pop_score"] = pop_score
    df3.sort_values(by=['pop_score'], inplace=True, ascending=False)
    
    return df3.head(10)


## Case Sample

### #IVoted
ivoted_df = read_tweets_file('ivoted_df')
plot_wordcloud(hash_list(ivoted_df['hashtags']), color="Blues")
plot_day_freq(ivoted_df)
find_KOL(ivoted_df)

### #coronavirus
coronavirus = read_tweets_file("corona_df")
plot_wordcloud(hash_list(coronavirus['hashtags']))
plot_day_freq(coronavirus, n = 1)
find_KOL(coronavirus)


### #metoo
metoo = read_tweets_file("metoo_df")
plot_wordcloud(hash_list(metoo['hashtags']))
plot_day_freq(metoo)
find_KOL(metoo)









