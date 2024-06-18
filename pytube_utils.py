import os
from pytube import YouTube, Playlist, Search
import requests

def getAudioFile(query: str):
    try: 
        yt = YouTube(query)
    except: 
         return None

    return getYouTubetoAudioFile(yt)

def isPlaylist(link):
    return "&list=" in link


def fastSearch(query: str):
        if "/watch?" in query:
             return None
        else:
            try: 
                s = Search(query)
            except: 
                return None
            
            return getYouTubetoAudioFile(s.results[0])

def getYouTubetoAudioFile(yt: YouTube):
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(filename='audio.mp4')
    return audio_file
    

def downloadPlaylist(link):
    p = Playlist(link)
    return f"Downloaded playlist, {p.title}"