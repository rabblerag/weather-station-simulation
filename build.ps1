# Generate containers dynamically based on MAX_STATIONS
# Scalable and assigns each station a unique ID

$env:MAX_STATIONS = 5 # env namespace so it gets passed to server container
$stations_template =  Get-Content -Path ./weather-station/compose.yml.template -Raw 
$stations = "services:`r`n"

for ($i = 1; $i -le $env:MAX_STATIONS; $i++) {
    $filled = $stations_template `
        -replace '{{ID}}', $i `
    
    $stations += $filled
}

$stations | Out-File -FilePath ./weather-station/compose.yml -Encoding UTF8

docker compose -f 'compose.yml' -f "./server/compose.yml" -f "./weather-station/compose.yml" --env-file ./.env up --build -d
