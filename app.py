from flask import Flask, request
from flask_cors import CORS
import tweepy
import re

app = Flask(__name__)
CORS(app)

tag_regex_texto = '(?:(?:(?:ftp|http)[s]*:\/\/|@|#|www\.)[^\.]+\.[^ \n]+)'


#RED SOCIAL TWITTER


CONSUMER_KEY = 'Sg9KPRUPVSS22ByxsD2Om3yh6'
CONSUMER_SECRET = 'pX8KCJfSBXm4sk6iMQU852agow2a7gdaYkaZeZNxekXBFoP49M'
ACCESS_TOKEN = '1262492224648077318-2QzMBDtjAt0p33W4C0EQSBCyoVW8yt'
ACCESS_TOKEN_SECRET = 'v2I4wGhQPVLjpdhEryZrqIrgvEMQMzzhOj9VBCcCGg5iQ'

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)

auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

api = tweepy.API(auth,wait_on_rate_limit= True,
                    wait_on_rate_limit_notify=True)
tag_regex = 'http[s]?://\S+/|#+|@|//\S+'
tag_regex_url = '(?:(?:(?:ftp|http)[s]*:\/\/|www\.)[^\.]+\.[^ \n]|://\S+/|#+|@|//\S|RT\.[^ \n]+)'
tag_regex_urls = '(?:(?:(?:ftp|http)[s]*:\/\/|www\.)[^\.]+\.[^ \n]+)'
tag_regex_fecha = '([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?|GMT'
tag_regex_texto = '(?:(?:(?:ftp|http)[s]*:\/\/|@|#|www\.)[^\.]+\.[^ \n]+)'


@app.route('/getUsers')
def users_keywords ():
    actor = request.args.get('user')
    search_language = "es"
    num = "15"
    country ="ECUADOR"
    result = api.geo_search(query= country, granularity="country") 
    place_id = result[0].id 
    tweets = api.search(q = actor+' -filter:retweets'+ 'place:%s', 
                            lang = search_language, 
                            count = num)
    for tweet in tweets:
        users_locs = [{'name':tweet.user.screen_name, 
        'descripcion': re.sub(tag_regex,'',remove_emoji(tweet.user.description)), 'avatar':tweet.user.profile_image_url_https, 'social': 'Twitter' 
                    } for tweet in tweets]
    lista = users_locs
    return {'users':lista}

@app.route('/getUser')
def users_description ():
    try:
        screen_name= request.args.get('user')
        results = api.user_timeline(screen_name)
        contenedor = len(results)
        if(contenedor > 0):
            for tweet in results[:1]:
                user_information = {'name':tweet.user.screen_name, 
                        'descripcion':tweet.user.description, 
                        'avatar':tweet.user.profile_image_url_https,
                        'social': 'Twitter' 
                        }
        return {'user':user_information}   
    except:
       return 'No existe el usuario ingresado'

@app.route('/getTuits')
def search():
    new_search = "covid,vacunas,quito, vacuna china"
    search_language = "es"
    num = "2000"
    result = api.geo_search(query="ECUADOR", granularity="country") 
    place_id = result[0].id 
    tweets = api.search(q = new_search+' -filter:retweets'+ 'place:%s' % place_id, 
                        tweet_mode = "extended", 
                        lang = search_language, 
                        count = num)
    for tweet in tweets:
        tuits = [{ 'usuario':tweet.user.screen_name, 
                    'descriptcion': tweet._json["full_text"], 
                    'creado':tweet.user.created_at } for tweet in tweets]
    return {'tuits':tuits} 

@app.route('/getTuit')
def users_Tuitters():
    try:
        actor = request.args.get('user')
        resultsUsers = api.user_timeline(actor, include_rts=False)
        contenedor = len(resultsUsers)
        results = tweepy.Cursor(api.user_timeline, screen_name=actor,
                                lang="en", tweet_mode='extended', count=100).items()
        num = "15"
        for tweet in results:
            fecha = re.sub(tag_regex_fecha, '', str(tweet.created_at))
            fechaG = re.sub('-', '/', fecha)
            user_information = [{
                'fecha': re.sub(r'(\d+)/(\d+)/(\d+)', r'\3/\2/\1', fechaG),
                'descripcion': re.sub(tag_regex_texto, '', tweet.full_text),
                'link': re.findall(r'(?:(?:(?:ftp|http)[s]*:\/\/|www\.)[^\.]+\.[^ \n]+)', tweet.full_text),
                'calificacion':'',
                'noticia':  re.sub(tag_regex_texto, '', tweet.full_text),
                'social':'Twitter',
            }for tweet in results]
            lista = user_information
        return {'tuits': lista}
    except:
        return 'No existe el usuario ingresado'


def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\u200d"
                           u"\u2640-\u2642" 
                           u"\ud83d\udc49"
                           u"\ud83d\ude37"
                           u"\ud83c\udf0e\u2705"
                           u"\ud83d\udc49"
                           u"\ud83d\udcf2\ud83d\uded2"
                           u"\u200d\ud83e\uddd1\u200d"
                           u"\\u200d\ud83e\uddd1\\u200d"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
  
@app.route('/') 
def inicio():
    return "Hello de nuevo!"

if __name__ == "__main__":
    app.run()