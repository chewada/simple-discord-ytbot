
import os
import yt_dlp


def downloadAudioFile(query: str, folder: str): # Does not handle searching rn

    ydl_opts = {
        'format': 'worstaudio',
        'outtmpl': '%(id)s.%(ext)s',
        #'default_search': 'ytsearch',
        'paths': {'home': f'./audio_files/{folder}'},
        'noplaylist': True,
        'allow_playlist_files': False
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    try: 
         info_dict = ydl.extract_info(query, download=True)
    except: 
         return None

    return info_dict

def isPlaylist(link):
    return "&list=" in link


# def fastSearch(query: str):
#         if "/watch?" in query:
#              return None
#         else:
#             try: 
#                 s = Search(query)
#             except: 
#                 return None
            
#             return getYouTubetoAudioFile(s.results[0])

# def getYouTubetoAudioFile(yt: YouTube):
#     audio_stream = yt.streams.filter(only_audio=True).first()
#     audio_file = audio_stream.download(filename='audio.mp4')
#     return audio_file
    

# def downloadPlaylist(link):
#     #p = Playlist(link)
#     return f"Downloaded playlist, {p.title}"