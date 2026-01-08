# Generate containers dynamically based on MAX_STATIONS
# Scalable and assigns each station
$env:MAX_CLIENTS = 5
$stations_template =  Get-Content -Path ./weather-station/compose.yml.template -Raw 
$stations = "services:`r`n"

for ($i = 1; $i -le $env:MAX_CLIENTS; $i++) {
    $filled = $stations_template `
        -replace '{{ID}}', $i `
    
    $stations += $filled
}

$stations | Out-File -FilePath ./weather-station/compose.yml -Encoding UTF8

docker compose -f 'compose.yml' -f "./server/compose.yml" -f "./weather-station/compose.yml" up --build -d
# docker compose -f 'compose.yml' -f "./weather-station/compose.yml" up -d --build
