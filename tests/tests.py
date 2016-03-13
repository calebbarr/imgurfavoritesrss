from unittest import TestLoader, TextTestRunner, TestSuite, TestCase
from imgurfavoritesrss import fetch_favorites,fetch_new_favorites,client,favorites,poll_imgur,normalize_img
from utils import drop,dropright,tail
from datetime import datetime
import pytz


username="SnugglyWalrus"

def links(imgs):
    return [img.link for img in imgs]
        
class Tests(TestCase):
    
    def test_fetch_new_favorites(self):
        favorites[username] = fetch_favorites(username)[:-3]
        self.assertEqual(len(fetch_new_favorites(username)),3)
        
    def test_poll_imgur(self):
        favorites[username] = fetch_favorites(username)[:-3]
        num_favorites = len(favorites[username])
        poll_imgur([username])
        self.assertEqual(len(favorites[username]),num_favorites+3)
    
class UtilsTests(TestCase):
    
    def test_drop(self):
        self.assertEqual(drop([1,2,3,4,5],3) , [4,5])
        self.assertEqual(drop([1,2,3,4,5],6) , [])
    
    def test_dropright(self):
        self.assertEqual(dropright([1,2,3,4,5],3) , [1,2])
        self.assertEqual(dropright([1,2,3,4,5],6) , [])
        
    def test_tail(self):
        self.assertEqual(tail([1,2,3,4,5]) , [2,3,4,5])
        self.assertEqual(tail([1,]) , [])        
    
def run():
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(UtilsTests),
        loader.loadTestsFromTestCase(Tests)
    ))
    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)
    
if __name__ == '__main__':
    run()