import random as rand
from os import environ

from collections.abc import Iterator

metrics = environ['AVAILABLE_METRICS'].split(",")
ranges = tuple(map(lambda x: tuple(map(float, x.split(','))), environ["METRIC_RANGES"].split('|')))

for metric, metric_range in zip(metrics, ranges):
    if metric == "temperature":
        min_temp, max_temp = metric_range

        def measure_temp() -> Iterator[float]:    
            mu = (min_temp + max_temp)/2
            sigma = (max_temp - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

            while True:
                value = round(rand.gauss(mu, sigma), 1)

                if min_temp > value  or value > max_temp: continue
                
                yield value
    if metric == "humidity":
        min_humidity, max_humidity = metric_range

        def measure_humidity() -> Iterator[float]:
            mu = (min_humidity + max_humidity)/2
            sigma = (max_humidity - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

            while True:
                value = round(rand.gauss(mu, sigma), 2)

                if min_humidity > value  or value > max_humidity: continue
                
                yield value
    if metric == "wind_speed":
        min_wind_speed, max_wind_speed = metric_range

        def measure_wind_speed() -> Iterator[float]:
            mu = (min_wind_speed + max_wind_speed)/2
            sigma = (max_wind_speed - mu) / 3     # 99% of values in a gaussian are in an interval +- 3σ from the mean

            while True:
                value = round(rand.gauss(mu, sigma), 0)

                if min_wind_speed > value  or value > max_wind_speed: continue
                
                yield value

