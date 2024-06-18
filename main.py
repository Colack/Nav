import os
import sys
import datetime
import webbrowser
import wikipedia
import pyjokes
import pywhatkit
from pytube import YouTube
from googlesearch import search
import re
from newsapi import NewsApiClient
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load settings from JSON
with open('settings.json') as json_file:
    JSON_SETTINGS = json.load(json_file)

USERNAME = JSON_SETTINGS['Name']
BOTNAME = JSON_SETTINGS['BotName']
NEWS_API_KEY = JSON_SETTINGS['NewsAPIKey']  # Add your News API key in the settings.json file

WAKE_WORDS = [f"{BOTNAME}", f"{BOTNAME.lower()}", f"{BOTNAME.upper()}"]

LANGUAGE = 'en'  # Default language for news API

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def speak(text):
    print(f"{BOTNAME}: {text}")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_current_date():
    return datetime.datetime.now().strftime("%d/%m/%Y")

def search_google(query):
    try:
        search_results = search(query, num_results=1)
        for j in search_results:
            speak(f"Here is what I found: {j}")
            break  # Only print the first result
    except Exception as e:
        speak(f"Error searching Google: {str(e)}")


def open_website(query):
    webbrowser.open(query)

def search_wikipedia(query):
    try:
        results = wikipedia.search(query)
        if results:
            page_title = results[0]
            summary = wikipedia.summary(page_title, sentences=2)
            speak(f"{page_title}: {summary}")
        else:
            speak(f"No results found for '{query}' on Wikipedia.")
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]  # Show the first 5 options for brevity
        speak(f"Your query is too ambiguous. Did you mean: {', '.join(options)}?")
    except wikipedia.exceptions.PageError:
        speak(f"No page found for '{query}'. Please try another query.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def play_on_youtube(query):
    pywhatkit.playonyt(query)

def download_youtube_video(query):
    try:
        video = YouTube(query)
        video.streams.first().download()
        speak(f"Downloaded video: {video.title}")
    except Exception as e:
        speak(f"Failed to download video. Error: {str(e)}")

def get_news(topic):
    try:
        top_headlines = newsapi.get_top_headlines(q=topic, language=LANGUAGE)
        articles = top_headlines['articles']
        if articles:
            for article in articles[:5]:  # Displaying up to 5 articles
                speak(f"Title: {article['title']}")
                speak(f"Description: {article['description']}")
                speak("...")
        else:
            speak(f"No news articles found for '{topic}'.")
    except Exception as e:
        speak(f"An error occurred while fetching news: {str(e)}")

reminders = []

def set_reminder(reminder, time):
    reminders.append((reminder, time))
    speak(f"Reminder set for {time}: {reminder}")

def handle_query(query):
    if 'time' in query:
        speak(f"The current time is {get_current_time()}")
    elif 'date' in query:
        speak(f"The current date is {get_current_date()}")
    elif 'search' in query:
        handle_google_search(query)
    elif 'open' in query:
        handle_website_open(query)
    elif 'news' in query:
        handle_news_query(query)
    elif any(word in query for word in ['wikipedia', 'about', 'tell me about']):
        handle_wikipedia_query(query)
    elif 'joke' in query:
        tell_joke()
    elif 'play' in query and 'spotify' in query:
        handle_spotify_play(query)
    elif 'pause' in query and 'spotify' in query:
        handle_spotify_pause()
    elif 'next' in query and 'spotify' in query:
        handle_spotify_next()
    elif 'previous' in query and 'spotify' in query:
        handle_spotify_previous()
    elif 'download' in query:
        handle_youtube_download(query)
    elif any(word in query for word in ['reminder', 'remind me']):
        handle_reminder_query(query)
    elif 'clear' in query:
        clear_console()
    elif 'help' in query:
        display_help()
    elif 'exit' in query:
        speak(f"Goodbye {USERNAME}, have a great day!")
        sys.exit()
    else:
        speak("I'm sorry, I didn't understand that.")

def handle_google_search(query):
    query = query.replace('search', '').strip()
    search_google(query)

def handle_website_open(query):
    query = query.replace('open', '').strip()
    open_website(query)

def handle_wikipedia_query(query):
    query = re.sub(r'\b(wikipedia|about|tell me about)\b', '', query).strip()
    search_wikipedia(query)

def handle_spotify_play(query):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=JSON_SETTINGS['SpotifyClientID'],
                                                      client_secret=JSON_SETTINGS['SpotifyClientSecret'],
                                                      redirect_uri=JSON_SETTINGS['SpotifyRedirectURI'],
                                                      scope='user-read-playback-state,user-modify-playback-state'))
        query = query.replace('play', '').replace('spotify', '').strip()
        results = sp.search(q=query, limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            speak(f"Playing {results['tracks']['items'][0]['name']} by {results['tracks']['items'][0]['artists'][0]['name']}")
        else:
            speak(f"Could not find '{query}' on Spotify.")
    except Exception as e:
        speak(f"Error playing track: {str(e)}")

def display_help():
    help_text = """
    Here are the commands I can understand:
    - time: Get the current time.
    - date: Get the current date.
    - search [query]: Perform a Google search.
    - open [website URL]: Open a website.
    - news about [topic]: Get news headlines about a topic.
    - wikipedia [query]: Search and provide information from Wikipedia.
    - joke: Tell a joke.
    - play spotify [song/artist]: Play a song or artist on Spotify.
    - pause spotify: Pause the current song on Spotify.
    - next spotify: Play the next song on Spotify.
    - previous spotify: Play the previous song on Spotify.
    - download [YouTube URL or query]: Download a YouTube video.
    - remind me to [task] at [time]: Set a reminder.
    - clear: Clear the console screen.
    - help: Display this help message.
    - exit: Exit the assistant.
    """
    speak(help_text)

def handle_spotify_pause():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=JSON_SETTINGS['SpotifyClientID'],
                                                      client_secret=JSON_SETTINGS['SpotifyClientSecret'],
                                                      redirect_uri=JSON_SETTINGS['SpotifyRedirectURI'],
                                                      scope='user-read-playback-state,user-modify-playback-state'))
        sp.pause_playback()
        speak("Paused Spotify playback.")
    except Exception as e:
        speak(f"Error pausing playback: {str(e)}")

def handle_spotify_next():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=JSON_SETTINGS['SpotifyClientID'],
                                                      client_secret=JSON_SETTINGS['SpotifyClientSecret'],
                                                      redirect_uri=JSON_SETTINGS['SpotifyRedirectURI'],
                                                      scope='user-read-playback-state,user-modify-playback-state'))
        sp.next_track()
        speak("Playing next track on Spotify.")
    except Exception as e:
        speak(f"Error playing next track: {str(e)}")

def handle_spotify_previous():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=JSON_SETTINGS['SpotifyClientID'],
                                                      client_secret=JSON_SETTINGS['SpotifyClientSecret'],
                                                      redirect_uri=JSON_SETTINGS['SpotifyRedirectURI'],
                                                      scope='user-read-playback-state,user-modify-playback-state'))
        sp.previous_track()
        speak("Playing previous track on Spotify.")
    except Exception as e:
        speak(f"Error playing previous track: {str(e)}")

def handle_youtube_download(query):
    query = query.replace('download', '').strip()
    download_youtube_video(query)

def handle_news_query(query):
    topic_match = re.search(r'news about (.+)', query, re.IGNORECASE)
    if topic_match:
        topic = topic_match.group(1).strip()
        get_news(topic)
    else:
        speak("Please specify a topic for the news.")

def handle_reminder_query(query):
    match = re.search(r'remind me to (.+) at (.+)', query)
    if match:
        reminder, time = match.groups()
        set_reminder(reminder.strip(), time.strip())
    else:
        speak("I'm sorry, I didn't understand the reminder. Please use the format 'remind me to [task] at [time]'.")

def main():
    speak(f"Hello {USERNAME}, I am {BOTNAME}, your personal assistant. How can I help you today?")

    while True:
        query = input(f"{USERNAME}: ").lower()

        if any(wake_word in query for wake_word in WAKE_WORDS):
            speak(f"Yes {USERNAME}?")

            while True:
                query = input(f"{USERNAME}: ").lower()
                handle_query(query)

                if 'exit' in query:
                    break

if __name__ == '__main__':
    main()
