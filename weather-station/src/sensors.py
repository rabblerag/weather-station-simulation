import random as rand
from os import environ

from collections.abc import Iterator


def measure_temp() -> Iterator[float]:
    min_temp = int(environ["MIN_TEMP"])
    max_temp = int(environ["MAX_TEMP"])
    
    mu = (min_temp + max_temp)/2
    sigma = (max_temp - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

    while True:
        value = round(rand.gauss(mu, sigma), 1)

        if min_temp > value  or value > max_temp: continue
        
        yield value

def measure_humidity() -> Iterator[float]:
    min_humidity = 0.0
    max_humidity = float(environ["MAX_HUMIDITY"])
    
    mu = (min_humidity + max_humidity)/2
    sigma = (max_humidity - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

    while True:
        value = round(rand.gauss(mu, sigma), 2)

        if min_humidity > value  or value > max_humidity: continue
        
        yield value

def measure_wind_speed() -> Iterator[float]:
    min_wind_speed = 0
    max_wind_speed = int(environ["MAX_WIND_SPEED"])
    
    mu = (min_wind_speed + max_wind_speed)/2
    sigma = (max_wind_speed - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

    while True:
        value = round(rand.gauss(mu, sigma), 0)

        if min_wind_speed > value  or value > max_wind_speed: continue
        
        yield value

