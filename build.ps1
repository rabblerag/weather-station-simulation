# Generate containers dynamically based on MAX_STATIONS
# Scalable and assigns each station a unique ID

$env:MAX_STATIONS = 5 # env namespace so it gets passed to server container

$MIN_TEMP = [int] -10
$MAX_TEMP = [int] 40
$MIN_HUMIDITY = [float] 0.0
$MAX_HUMIDITY = [float] 1.0
$MIN_WIND_SPEED = [uint16] 0
$MAX_WIND_SPEED = [uint16] 50

$env:METRIC_RANGES = "$MIN_TEMP,$MAX_TEMP|$MIN_HUMIDITY,$MAX_HUMIDITY|$MIN_WIND_SPEED,$MAX_WIND_SPEED"

$stations_template =  Get-Content -Path ./weather-station/compose.yml.template -Raw 
$stations = "services:`r`n"
$secrets = "`r`n`r`nsecrets:`r`n"

$station_secrets = @{}

for ($i = 1; $i -le $env:MAX_STATIONS; $i++) {

    if ($i -eq 2){
        $metrics = "temperature"
        $ranges = "$MIN_TEMP,$MAX_TEMP"
        $interval = 60
    }
    elseif ($i -eq 4){
        $metrics = "temperature,humidity"
        $ranges = "$MIN_TEMP,$MAX_TEMP|$MIN_HUMIDITY,$MAX_HUMIDITY"
        $interval = 30
    }
    elseif ($i -eq 3){
        $metrics = "temperature,wind_speed"
        $ranges = "$MIN_TEMP,$MAX_TEMP|$MIN_WIND_SPEED,$MAX_WIND_SPEED"
        $interval = 45
    }
    else{
        $metrics = "temperature,humidity,wind_speed"
        $ranges = $env:METRIC_RANGES
        $interval = 15
    }

    $filled = $stations_template `
        -replace '{{ID}}', $i `
        -replace '{{METRICS}}', $metrics `
        -replace '{{RANGES}}', $ranges `
        -replace '{{INTERVAL}}', $interval

    $stations += $filled

    $temp_key = (New-Object System.Security.Cryptography.HMACSHA256).Key
    $hex_key = ($temp_key | ForEach-Object ToString X2) -join ''

    $station_secrets["station_$i"] = $hex_key

    [System.Environment]::SetEnvironmentVariable("STATION_$i`_SECRET", $hex_key)

    $secrets += "  station-$i-secret:`r`n    environment: STATION_$i`_SECRET`r`n"


}
$stations+$secrets | Out-File -FilePath ./weather-station/compose.yml -Encoding UTF8

$temp_key = (New-Object System.Security.Cryptography.HMACSHA256).Key
$env:SERVER_SECRET = ($temp_key | ForEach-Object ToString X2) -join ''
$env:STATION_SECRETS = $station_secrets | ConvertTo-Json -Compress

docker compose -f 'compose.yml' -f "./server/compose.yml" -f "./weather-station/compose.yml" -f "./web/compose.yml" --env-file ./.env up --build -d
