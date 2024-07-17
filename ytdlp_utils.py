
import os
import yt_dlp

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
        info_dict = info_dict['entries'][0]
    
    return info_dict

def getTitle(query: str):
     
    info_dict = extractDict(query, "temp", False)

    if(info_dict is None):
        return "None"
    
    if 'entries' in info_dict:
        info_dict = info_dict['entries'][0]

    return info_dict["title"]