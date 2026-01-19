#!/bin/bash

# Generate containers dynamically based on MAX_STATIONS
# Scalable and assigns each station a unique ID

export MAX_STATIONS=5

MIN_TEMP=-10
MAX_TEMP=40
MIN_HUMIDITY=0.0
MAX_HUMIDITY=1.0
MIN_WIND_SPEED=0
MAX_WIND_SPEED=50

export METRIC_RANGES="${MIN_TEMP},${MAX_TEMP}|${MIN_HUMIDITY},${MAX_HUMIDITY}|${MIN_WIND_SPEED},${MAX_WIND_SPEED}"

stations_template=$(cat ./weather-station/compose.yml.template)
stations="services:\n"
secrets="\n\nsecrets:\n"

declare -A station_secrets

for ((i=1; i<=MAX_STATIONS; i++)); do

    # Change or add more configurations here
    if [ $i -eq 2 ]; then
        metrics="temperature"
        ranges="${MIN_TEMP},${MAX_TEMP}"
        interval=60
    elif [ $i -eq 4 ]; then
        metrics="temperature,humidity"
        ranges="${MIN_TEMP},${MAX_TEMP}|${MIN_HUMIDITY},${MIN_HUMIDITY}"
        interval=30
    elif [ $i -eq 3 ]; then
        metrics="temperature,wind_speed"
        ranges="${MIN_TEMP},${MAX_TEMP}|${MIN_WIND_SPEED},${MAX_WIND_SPEED}"
        interval=45
    else
        metrics="temperature,humidity,wind_speed"
        ranges="$METRIC_RANGES"
        interval=15
    fi

    filled=$(echo "$stations_template" | sed \
        -e "s/{{ID}}/$i/g" \
        -e "s/{{METRICS}}/$metrics/g" \
        -e "s/{{RANGES}}/$ranges/g" \
        -e "s/{{INTERVAL}}/$interval/g")

    stations+="$filled"

    # Generate random 32-byte hex key (equivalent to HMACSHA256 key)
    hex_key=$(openssl rand -hex 32)
    
    station_secrets["station_$i"]=$hex_key
    export "STATION_${i}_SECRET"="$hex_key"
    
    secrets+="  station-${i}-secret:\n    environment: STATION_${i}_SECRET\n"
done

echo -e "$stations$secrets" | tee ./weather-station/compose.yml > /dev/null

# Generate server secret
server_secret=$(openssl rand -hex 32)
export SERVER_SECRET="$server_secret"

# Convert station secrets to JSON
STATION_SECRETS=$(printf '%s\n' "${!station_secrets[@]}" | \
    jq -n --argjson secrets "$(printf '%s=%s\n' "${!station_secrets[@]}" "${station_secrets[@]}")" '$secrets')

export STATION_SECRETS

docker compose -f 'compose.yml' -f "./server/compose.yml" -f "./weather-station/compose.yml" -f "./web/compose.yml" --env-file ./.env up --build -d
