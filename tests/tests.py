from unittest import TestLoader, TextTestRunner, TestSuite, TestCase
from imgurfavoritesrss import fetchLastFavorite,client,favorites,poll_imgur
from datetime import datetime
import pytz


username="SnugglyWalrus"

def fetchSecondToLastFavorite(username):
    favorite = client.get_gallery_favorites(username)[1]
    favorite.datetime = datetime.now(pytz.timezone('UTC')).strftime("%a, %d %b %Y %H:%M:%S %z")
    return favorite
        
class Tests(TestCase):
    
    def test_favorites_fetching(self):
        global username
        second_to_last_favorite = fetchSecondToLastFavorite(username)
        last_favorite = fetchLastFavorite(username)
        self.assertNotEqual(second_to_last_favorite,last_favorite)
    
    def test_new_favorite(self):
        global favorites,username
        favorites[username] = [fetchSecondToLastFavorite(username)]
        poll_imgur()
        self.assertNotEqual(favorites[username][0].link,favorites[username][1].link)
        
def run():
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(Tests)
    ))
    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)
    
if __name__ == '__main__':
    run()