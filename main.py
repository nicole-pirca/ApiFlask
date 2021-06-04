from flask import Flask, request
from flask_cors import CORS
from facebook_scraper import get_posts
import tweepy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re as re
import time
import datetime
from webdriver_manager.chrome import ChromeDriverManager
import time, requests, os
import re

app = Flask(__name__)
CORS(app)

today = datetime.date.today().strftime('%d-%m-%Y')
tag_regex_texto = '(?:(?:(?:ftp|http)[s]*:\/\/|@|#|www\.)[^\.]+\.[^ \n]+)'

# RED SOCIAL DE FACEBOOK 

@app.route('/postFacebook') 
def users_Post():
    try:
#caracolradio, SaludEcuador, bbcnews, SaludEcuador, MinisterioDeGobiernoEcuador,lahoraecuador, elcomerciocom 
        group = request.args.get('group')
        posts = get_posts(group, pages=10)
        for post in posts:
            fecha = re.sub(tag_regex_fecha, '', str(post['time']))
            fechaG = re.sub('-', '/', fecha)
            users_locs = [{
                'descripcion': post['text'],
                'fecha': re.sub(r'(\d+)/(\d+)/(\d+)', r'\3/\2/\1', fechaG),
                'calificacion': '',
                'link':post['post_url'],
                'social':'Facebook',
                'noticia': post['text']
            } for post in  posts ]
            lista = users_locs
        return {'post': lista} 
    except:
        return 'No es un grupo publico'


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
    tweets = api.search(q = actor+' -filter:retweets'+ 'place:%s' % place_id, 
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
                'enlace': re.findall(r'(?:(?:(?:ftp|http)[s]*:\/\/|www\.)[^\.]+\.[^ \n]+)', tweet.full_text),
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
  
#RED SOCIAL LINKEDIN 

@app.route('/postLinkedin')
def post_LinkedIn():
        
    USERNAME = 'systemvas001@gmail.com'
    PASSWORD = 'AdminVas'

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.linkedin.com/uas/login")
    time.sleep(3)

    email=driver.find_element_by_id("username")
    email.send_keys(USERNAME)
    password=driver.find_element_by_id("password")
    password.send_keys(PASSWORD)
    time.sleep(3)
    password.send_keys(Keys.RETURN)

    post_links = []
    post_texts = []
    post_names = []
    actor = request.args.get('user')
    page = actor
    time.sleep(10)
    driver.get(page + 'posts/?feedView=all')  
    start=time.time()
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
        end=time.time()
        if round(end-start)>10:
            break

    time.sleep(5)
    company_page = driver.page_source   

    linkedin_soup = bs(company_page.encode("utf-8"), "html")
    linkedin_soup.prettify()
    containers = linkedin_soup.findAll("div",{"class":"occludable-update ember-view"})
    iterations = 0
    nos = 20
    
    for container in containers:
       
        try:
            text_box = container.find("div",{"class":"feed-shared-update-v2__description-wrapper ember-view"})
            text = text_box.find("span",{"dir":"ltr"})
            texto = post_texts.append(text.text.strip())
            iterations += 1
            if(iterations==nos):
                break
        except:
            pass
    cadena_post = str(post_texts)
    lista = cadena_post.split(',')
    link = re.findall(r'(?:(?:(?:ftp|http)[s]*:\/\/|www\.)[^\.]+\.[^ \n]+)', str(post_texts))    
    descripcion = re.sub(tag_regex_texto, '',str(post_texts))
    posts_separados = descripcion.split('#')          
    users_locs = [{
        
                'descripcion': re.sub('#','',remove_emoji(descripcion)),
                'fecha': re.sub('-','/',today),
                'calificacion': '',
                'link':  link,
                'social':'LinkedIn',
                'noticia': re.sub('#','',remove_emoji(descripcion))
            }]
    lista = users_locs
    driver.quit()
    return {'lindelin': lista}

#RED SOCIAL INSTAGRAM

@app.route('/postInstagram')
def post_Instagram():
    actor = request.args.get('user')

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(actor)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(4)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
  
    posts = []
    links = driver.find_elements_by_tag_name('a')
        
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
            posts.append( post )
    try:
        for post in posts:
            headers = {'User-Agent': 'Mozilla'}
            r = requests.get('{}?__a=1'.format( post ), headers=headers)
            comentarios = r.json()['graphql']['shortcode_media']['edge_media_preview_comment']['edges']
            for i in comentarios:
                descripcion = i['node']['text']
                users_locs = [{
                    'descripcion': descripcion,
                    'fecha': re.sub('-','/',today),
                    'calificacion': '',
                    'link':  actor,
                    'social':'Instagram',
                    'noticia': descripcion,
                }]
                
            lista = users_locs
            driver.quit()
            return {'instagram': lista}
    except:
        users_locs = [{
                    'descripcion': 'no hay datos',
                    'fecha':'no hay registros',
                    'calificacion': '',
                    'link':  'actor',
                    'social':'Instagram',
                    'noticia': 'no hay datos',
                }]
        driver.quit()
        return {'Instagram': users_locs}
        
@app.route('/') 
def inicio():
    user_ip = request.remote_addr
    return "<h1>Hello de nuevo!</h1>"

if __name__ == "__main__":
    app.run()