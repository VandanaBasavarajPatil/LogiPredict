def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={c6fd1e5e95ddc734ca4bee692cce3542}"

    response = requests.get(url)

    data = response.json()

    weather = data['weather'][0]['main']

    temp = data['main']['temp']

    return {
        'weather': weather,
        'temperature': temp
    }