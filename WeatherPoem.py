import tkinter as tk
from tkinter import font as tkfont
import requests
from datetime import datetime
import openai

# Setup your API keys here
WEATHER_API_KEY = 'your api key'
OPENAI_API_KEY = 'your api key'

openai.api_key = OPENAI_API_KEY

# Mapping weather conditions to emojis
weather_emojis = {
    'sunny': '☀️',
    'clear': '☀',
    'partly cloudy': '⛅',
    'cloudy': '☁️',
    'overcast': '☁️',
    'mist': '🌫️',
    'patchy rain possible': '🌦️',
    'rain': '🌧️',
    'thunder': '⛈️',
    'snow': '❄️',
    'fog': '🌫️'
}

def get_weather():
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': WEATHER_API_KEY,
        'q': 'London',
        'aqi': 'no'
    }
    response = requests.get(url, params=params)
    weather_data = response.json()
    condition = weather_data['current']['condition']['text']
    temp_c = weather_data['current']['temp_c']
    return f"{condition.lower()}, {temp_c}°C", condition.lower()

def generate_poem(weather_description, condition):
    emoji = weather_emojis.get(condition, '🌍')  # Default to Earth globe if no match found
    now = datetime.now()
    current_hour = now.hour
    if 5 <= current_hour < 12:
        time_of_day = 'morning'
    elif 12 <= current_hour < 18:
        time_of_day = 'afternoon'
    elif 18 <= current_hour < 22:
        time_of_day = 'evening'
    else:
        time_of_day = 'night'
    prompt = f"Write a one verse rap poem about current weather in London, noting that it is {weather_description} this {time_of_day}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a poet who writes about the weather."},
                  {"role": "user", "content": prompt}]
    )
    poem = response['choices'][0]['message']['content']
    return poem, emoji  # Return both poem and emoji separately

def refresh_poem(canvas, poem_id, clock_id, emoji_id):
    weather_description, condition = get_weather()
    poem, emoji = generate_poem(weather_description, condition)
    full_text = f"Yo!\n{poem}"
    canvas.itemconfig(poem_id, text=full_text)
    canvas.itemconfig(emoji_id, text=emoji)  # Update emoji next to the clock
    root.after(3600000, refresh_poem, canvas, poem_id, clock_id, emoji_id)  # Refresh poem every hour

def update_clock(canvas, clock_id, emoji_id):
    if canvas.winfo_exists():  # Check if the widget still exists
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        canvas.itemconfig(clock_id, text=current_time)
        canvas.coords(emoji_id, canvas.bbox(clock_id)[2] + 10, 10)  # Position emoji right next to the clock
        root.after(1000, update_clock, canvas, clock_id, emoji_id)  # Update clock every second

root = tk.Tk()
root.title("Weather Poem Display")

# Full screen mode
root.attributes('-fullscreen', True)

canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Create font objects with tkinter.font
clock_font = tkfont.Font(family="Terminal", size=40)  # Double size for the clock
text_font = tkfont.Font(family="Terminal", size=20)

# Create text on the canvas using the custom fonts
clock_id = canvas.create_text(10, 10, anchor='nw', fill='antique white', font=clock_font, text="")
emoji_id = canvas.create_text(0, 0, anchor='nw', fill='antique white', font=clock_font, text="")  # Initialize emoji placement
poem_id = canvas.create_text(10, 100, anchor='nw', fill='antique white', font=text_font, text="Loading poem...")

refresh_poem(canvas, poem_id, clock_id, emoji_id)  # Initial call to display poem and start the refresh cycle
update_clock(canvas, clock_id, emoji_id)  # Start the clock update cycle
root.mainloop()

