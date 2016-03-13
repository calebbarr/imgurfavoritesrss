from __future__ import print_function
from flask import Flask
from twisted.internet import reactor
from twisted.internet import task
from threading import Thread
from imgurpython import ImgurClient
import os,sys
from datetime import datetime
import pytz
from itertools import dropwhile
from utils import drop,dropright,tail


print = lambda x: sys.stdout.write("%s\n" % x)

POLL_FREQUENCY = 60 # seconds

favorites = {
    # username : [imgs]
}

server = Flask(__name__,static_url_path='')

client_id = os.environ.get('IMGUR_CLIENT_ID')
client_secret = os.environ.get('IMGUR_CLIENT_SECRET')
client = ImgurClient(client_id, client_secret)

def poll_imgur(users=None):
    print("polling imgur")
    users = favorites.keys() if users is None else users
    for username in users:
        new_favorites = fetch_new_favorites(username)
        for favorite in new_favorites:
            print("found new favorite for {username}: {link}".format(username=username,link=favorite.link))
            favorites[username].append(favorite)
    
def rss_item(img):
    return  """
        <item>
          <title>{title}</title>
          <link>{link}</link>
          <pubDate>{date}</pubDate>
        </item>
    """.format(title=img.title,link=img.link,description=img.description,date=img.datetime)

    
def fetch_favorites(username):
    return [normalize_img(img) for img in client.get_gallery_favorites(username)]
    
def normalize_img(img):
    img.datetime = datetime.now(pytz.timezone('UTC')).strftime("%a, %d %b %Y %H:%M:%S %z")
    img.link = img.link[:img.link.rfind(".")].replace("i.imgur.com","imgur.com")
    return img
    
def fetch_new_favorites(username):
    last_favorite = (favorites[username])[-1]
    return tail([ fave for fave in dropwhile(lambda img: img.link != last_favorite.link, fetch_favorites(username))])
    
def initialize_rss_file(username):
    return """
    <rss version="2.0">
      <channel>
        <title>{username}'s Imgur Favorites</title>
        <link>http://imgur.com/user/{username}/favorites</link>
        <description>{username}'s Imgur Favorites ....</description>
      </channel>
    </rss>
    """.format(username=username).split("\n")
    
@server.route('/<username>', methods=['GET', 'POST'])
def favorites_rss(username):
    if not username in favorites:
        subscribe(username)
    else:
        poll_imgur([username])
    rss = initialize_rss_file(username)
    return "\n".join(rss[:-3] + [rss_item(fave) for fave in favorites[username]] + rss[-3:] )

def subscribe(username):
    favorite = fetchLastFavorite(username)
    favorites[username] = [favorite]
    
def run():
    task.LoopingCall(poll_imgur).start(POLL_FREQUENCY)
    t = Thread(target=reactor.run, args=(False,))
    t.daemon = True
    t.start()
    server.run(host="0.0.0.0",port=os.getenv("PORT",5000), debug=os.getenv("PORT") == None)

if __name__ == '__main__':
    run()
    