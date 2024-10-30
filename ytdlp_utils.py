import yt_dlp
import re

def extractDict(query: str, download: bool):
    ydl_opts = {
        'format': 'worstaudio',
        'source_address': '0.0.0.0',
        'outtmpl': '%(id)s.%(ext)s',
        'default_search': 'ytsearch',
        'paths': {'home': f'./audio_files'},
        'noplaylist': True,
        'ignoreerrors': True,
        'allow_playlist_files': False
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    try: 
         info_dict = ydl.extract_info(query, download=download)
    except: 
         return None
    
    return info_dict

def downloadAudioFile(query: str, download: bool): # Donwloads the audio from a query or link

    info_dict = extractDict(query, download)

    if(info_dict is None):
         return None
    
    if 'entries' in info_dict:
        i = 0
        while(info_dict['entries'][i].get('duration', 0) > 5400):
            i += 1
        info_dict = info_dict['entries'][i]
    
    return info_dict

def downloadPlaylist(query: str, folder: str, random: bool):
    playlist_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.*(\?|\&)list=([a-zA-Z0-9_-]+).*'
    )
    if(re.match(playlist_regex, query) is not None):
        ydl_opts = { # Options can be found here: https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/options.py
        'format': 'worstaudio',
        'source_address': '0.0.0.0',
        'outtmpl': '%(id)s.%(ext)s',
        'paths': {'home': f'./audio_files/{folder}'},
        'ignoreerrors': True,
        'playlist_random': random,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [finish_hook]
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
    
def finish_hook(dict):
    if dict['status'] == 'finished':
        print(f"Downloaded {dict['filename']}")
        pass