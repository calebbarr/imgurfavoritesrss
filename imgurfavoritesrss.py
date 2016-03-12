from __future__ import print_function
from flask import Flask
from twisted.internet import reactor
from twisted.internet import task
from threading import Thread
from imgurpython import ImgurClient
import os,sys
from datetime import datetime


print = lambda x: sys.stdout.write("%s\n" % x)

POLL_FREQUENCY = 60 # seconds

favorites = {
    # username : [imgs]
}

server = Flask(__name__,static_url_path='')

client_id = os.environ.get('IMGUR_CLIENT_ID')
client_secret = os.environ.get('IMGUR_CLIENT_SECRET')
client = ImgurClient(client_id, client_secret)


def poll_imgur():
    print("polling imgur")
    for username in favorites:
        favorite = getLastFavorite(username)
        print("last favorite for {username}: {link}".format(username=username,link=favorite.link))
        if(favorite.link != favorites[username][-1].link):
            print ("found new favorite for {username}: {link}").format(username=username,link=favorite.link)
            latest_favorite[username].append(favorite)
    
def rss_item(img):
    return  """
        <item>
          <title>{title}</title>
          <link>{link}</link>
          <description>{description}</description>
          <pubDate>{date}<pubDate>
        </item>
    """.format(title=img.title,link=img.link,description=img.description,date=img.datetime)

def getLastFavorite(username):
    favorite = client.get_gallery_favorites(username)[0]
    favorite.datetime = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    return favorite
    
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
    rss = initialize_rss_file(username)
    return "\n".join(rss[:-3] + [rss_item(fave) for fave in favorites[username]] + rss[-3:] )

def subscribe(username):
    favorite = getLastFavorite(username)
    favorites[username] = [favorite]
    
def run():
    task.LoopingCall(poll_imgur).start(POLL_FREQUENCY)
    t = Thread(target=reactor.run, args=(False,))
    t.daemon = True
    t.start()
    server.run(host="0.0.0.0",port=os.getenv("PORT",5000), debug=os.getenv("PORT") == None)

if __name__ == '__main__':
    run()
    