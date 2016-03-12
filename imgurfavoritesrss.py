from __future__ import print_function
from flask import Flask
from twisted.internet import reactor
from twisted.internet import task
from threading import Thread
from imgurpython import ImgurClient
import os,sys

print = lambda x: sys.stdout.write("%s\n" % x)



POLL_FREQUENCY = 60 # seconds
RSS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"static")

latest_favorite = {
    # username : link
}

server = Flask(__name__,static_url_path='',port=33507)

client_id = os.environ.get('IMGUR_CLIENT_ID')
client_secret = os.environ.get('IMGUR_CLIENT_SECRET')
client = ImgurClient(client_id, client_secret)


def poll_imgur():
    print("polling imgur")
    for username in latest_favorite:
        favorite = getLastFavorite(username)
        print("last favorite for {username}: {link}".format(username=username,link=favorite.link))
        if(favorite.link != latest_favorite[username]):
            print ("found new favorite for {username}: {link}").format(username=username,link=favorite.link)
            latest_favorite[username] = favorite.link
            add_rss_item(username,favorite)
            
def add_rss_item(username,img):
    rss_file = open(os.path.join(RSS_DIR,"{username}.xml".format(username=username)),'r')
    lines = rss_file.readlines()
    rss_file.close()
    rss_file = open(os.path.join(RSS_DIR,"{username}.xml".format(username=username)),'w')
    rss_file.write("\n".join(lines[:-3]))
    rss_file.write(rss_item(img))
    rss_file.write("\n".join(lines[-3:]))
    rss_file.close()
    
def rss_item(img):
    return  """
        <item>
          <title>{title}</title>
          <link>{link}</link>
          <description>{description}</description>
        </item>
    """.format(title=img.title,link=img.link,description=img.description )

def getLastFavorite(username):
    return client.get_gallery_favorites(username)[0]
    
def initialize_rss_file(username):
    rss="""
    <rss version="2.0">
      <channel>
        <title>{username}'s Imgur Favorites</title>
        <link>http://imgur.com/user/{username}/favorites</link>
        <description>{username}'s Imgur Favorites ....</description>
      </channel>
    </rss>
    """.format(username=username)
    open("{RSS_DIR}/{username}.xml".format(RSS_DIR=RSS_DIR,username=username),'w').write(rss)

@server.route('/subscribe/<username>', methods=['GET', 'POST']) #TODO finish
def subscribe(username):
    initialize_rss_file(username)
    favorite = getLastFavorite(username)
    latest_favorite[username] = favorite.link
    add_rss_item(username,favorite)
    return "subscribed to {username}".format(username=username) #TODO return link to rss file
    
def run():
    task.LoopingCall(poll_imgur).start(POLL_FREQUENCY)
    t = Thread(target=reactor.run, args=(False,))
    t.daemon = True
    t.start()
    server.run()

if __name__ == '__main__':
    run()
    