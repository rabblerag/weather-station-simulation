# Generate containers dynamically based on MAX_STATIONS
# Scalable and assigns each station a unique ID

$env:MAX_STATIONS = 5 # env namespace so it gets passed to server container
$stations_template =  Get-Content -Path ./weather-station/compose.yml.template -Raw 
$stations = "services:`r`n"
$secrets = "`r`n`r`nsecrets:`r`n"

$station_secrets = @{}

for ($i = 1; $i -le $env:MAX_STATIONS; $i++) {
    $filled = $stations_template `
        -replace '{{ID}}', $i `
    
    $stations += $filled

    $temp_key = (New-Object System.Security.Cryptography.HMACSHA256).Key
    $hex_key = ($temp_key | ForEach-Object ToString X2) -join ''

    $station_secrets["STATION_$i"] = $hex_key

    [System.Environment]::SetEnvironmentVariable("STATION_$i`_SECRET", $hex_key)

    $secrets += "  station-$i-secret:`r`n    environment: STATION_$i`_SECRET`r`n"
}
$stations+$secrets | Out-File -FilePath ./weather-station/compose.yml -Encoding UTF8

$temp_key = (New-Object System.Security.Cryptography.HMACSHA256).Key
$env:SERVER_SECRET = ($temp_key | ForEach-Object ToString X2) -join ''
$env:STATION_SECRETS = $station_secrets | ConvertTo-Json -Compress

docker compose -f 'compose.yml' -f "./server/compose.yml" -f "./weather-station/compose.yml" --env-file ./.env up --build -d
