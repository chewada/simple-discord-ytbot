import os
import pathlib

import unittest
from pytube_utils import *

class TestPytubeUtils(unittest.TestCase):
    def test_getAudioFile(self):
        self.assertEqual(getAudioFile('https://youtube.com/watch?v=2lAe1cqCOXo'), f'{pathlib.Path(__file__).parent.parent.resolve()}\\audio.mp4')
        self.assertEqual(getAudioFile('This will not work'), None)
    
    def test_isPlaylist(self):
        self.assertFalse(isPlaylist("Not a playlist"))

    def test_fastSearch(self):
        self.assertIsNone(fastSearch('https://youtube.com/watch?v=2lAe1cqCOXo'))
        self.assertEqual(fastSearch('Hello Adele'),  f'{pathlib.Path(__file__).parent.parent.resolve()}\\audio.mp4')
        

if __name__ == '__main__':
    unittest.main()
    os.remove("audio.mp4")