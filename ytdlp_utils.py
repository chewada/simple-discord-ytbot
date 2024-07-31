import yt_dlp
import re

def extractDict(query: str, folder: str, download: bool):
    ydl_opts = {
        'format': 'worstaudio',
        'source_address': '0.0.0.0',
        'outtmpl': '%(id)s.%(ext)s',
        'default_search': 'ytsearch',
        'paths': {'home': f'./audio_files/{folder}'},
        'noplaylist': True,
        'allow_playlist_files': False
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    try: 
         info_dict = ydl.extract_info(query, download=download)
    except: 
         return None
    
    return info_dict

def downloadAudioFile(query: str, folder: str): # Donwloads the audio from a query or link

    info_dict = extractDict(query, folder, True)

    if(info_dict is None):
         return None
    
    if 'entries' in info_dict:
        i = 0
        while(info_dict['entries'][i].get('duration', 0) > 3600):
            i += 1
        info_dict = info_dict['entries'][i]
    
    return info_dict

def getTitle(query: str):
     
    info_dict = extractDict(query, "temp", False)

    if(info_dict is None):
        return None
    
    if 'entries' in info_dict:
        info_dict = info_dict['entries'][0]

    return info_dict["title"]

def getPlaylist(query: str, folder: str):
    playlist_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.*(\?|\&)list=([a-zA-Z0-9_-]+).*'
    )
    if(re.match(playlist_regex, query) is not None):
        ydl_opts = {
        'format': 'worstaudio',
        'source_address': '0.0.0.0',
        'outtmpl': '%(id)s.%(ext)s',
        'default_search': 'ytsearch',
        'paths': {'home': f'./audio_files/{folder}'},
        'allow_playlist_files': True
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        try: 
            info_dict = ydl.extract_info(query)
        except: 
            return None
        if 'entries' in info_dict:
            return info_dict
        return None
    else:
        return None