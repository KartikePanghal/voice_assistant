import os
import openai
import speech_recognition as sr
import pyttsx3
import datetime
import smtplib
import wikipediaapi
import requests

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return None
        return command.lower()

def process_command_with_openai(command):
    openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": command}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def respond(command):
    if "hello" in command:
        speak("Hello! How can I help you today?")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {now}")
    elif "date" in command:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {today}")
    elif "search" in command:
        search_web(command)
    elif "wikipedia" in command:
        search_wikipedia(command)
    elif "email" in command:
        send_email(command)
    elif "weather" in command:
        get_weather(command)
    elif "your custom command" in command:
        speak("This is a custom response to your command.")
    else:
        response = process_command_with_openai(command)
        speak(response)

def search_web(command):
    speak("What would you like to search for?")
    query = listen()
    if query:
        url = f"https://www.google.com/search?q={query}"
        speak(f"Searching the web for {query}")
        response = requests.get(url)
        if response.status_code == 200:
            speak(f"I found some information on {query}. Please check your browser.")
        else:
            speak("Sorry, I couldn't fetch the information.")

def search_wikipedia(command):
    speak("What would you like to know about?")
    query = listen()
    if query:
        wiki = wikipediaapi.Wikipedia('en')
        page = wiki.page(query)
        if page.exists():
            speak(f"According to Wikipedia, {page.summary[:150]}...")
        else:
            speak("Sorry, I couldn't find anything on Wikipedia.")

def send_email(command):
    speak("What is the subject of the email?")
    subject = listen()
    speak("What should I say in the email?")
    body = listen()
    send_email_via_smtp(subject, body)

def send_email_via_smtp(subject, body):
    try:
        # You will need to update these details with your email server details
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_password")
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail("your_email@gmail.com", "recipient_email@gmail.com", message)
        server.quit()
        speak("Email has been sent successfully.")
    except Exception as e:
        speak(f"Failed to send email. Error: {e}")

def get_weather(command):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    speak("Please tell me the city name.")
    city = listen()
    if city:
        base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
            main = data['main']
            weather = data['weather'][0]['description']
            temperature = main['temp']
            speak(f"The temperature in {city} is {temperature} degrees Celsius with {weather}.")
        except requests.exceptions.RequestException as e:
            speak(f"Sorry, I couldn't get the weather information. Error: {e}")

def main():
    speak("Hello! How can I help you today?")
    while True:
        command = listen()
        if command:
            respond(command)

if __name__ == "__main__":
    main()
