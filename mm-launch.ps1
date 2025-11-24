# Launch multiple development servers in Windows Terminal tabs
# Each tab gets a custom color and title

# Use the current directory where the script is launched from
$workingDir = Get-Location

Write-Host "Launching servers from: $workingDir" -ForegroundColor Cyan

# Launch multiple development servers in Windows Terminal tabs
# Each tab gets a custom color and title

# Use the current directory where the script is launched from
$workingDir = Get-Location

Write-Host "Launching servers from: $workingDir" -ForegroundColor Cyan

# Launch first tab with FastAPI
wt --title "FastAPI Webhook" --tabColor "#1E88E5" -d "$workingDir" pwsh -NoExit -Command "uv run fastapi dev webhook/main.py --port 8080"

Start-Sleep -Seconds 2

# Add GitHub Server tab
wt -w 0 new-tab --title "GitHub Server" --tabColor "#43A047" -d "$workingDir" pwsh -NoExit -Command "uv run module_05/custom_github_server.py"

Start-Sleep -Seconds 1

# Add Ngrok tab
wt -w 0 new-tab --title "Ngrok Tunnel" --tabColor "#FB8C00" -d "$workingDir" pwsh -NoExit -Command "ngrok http 8080"

Start-Sleep -Seconds 2

# Add LangGraph tab
wt -w 0 new-tab --title "LangGraph Dev" --tabColor "#8E24AA" -d "$workingDir" pwsh -NoExit -Command "uv run langgraph dev"

Write-Host "Launched all development servers in Windows Terminal" -ForegroundColor Green