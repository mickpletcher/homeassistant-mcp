#Requires -Version 5.1
<#
.SYNOPSIS
    Finds claude_desktop_config.json and adds or updates an MCP server entry.

.DESCRIPTION
    Searches common Claude Desktop config locations, adds the mcpServers block
    with your Home Assistant MCP config, and backs up the original file first.

.PARAMETER HaUrl
    Home Assistant base URL. Default: http://homeassistant.local:8123

.PARAMETER HaToken
    Long-Lived Access Token from your HA profile page.

.PARAMETER ServerScriptPath
    Full path to server.py.
    Default behavior:
    1) .\server.py from the current working directory where the script is run
    2) server.py in the same folder as this script (fallback)

.PARAMETER McpServerName
    Key name for this MCP server in the config. Default: homeassistant

.EXAMPLE
    .\Set-ClaudeMcp.ps1 -HaToken "your_token_here"

.EXAMPLE
    .\Set-ClaudeMcp.ps1 -HaUrl "http://192.168.1.100:8123" -HaToken "abc123" -ServerScriptPath "C:\repos\homeassistant-mcp\server.py"
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$HaUrl          = 'http://homeassistant.local:8123',
    [string]$HaToken        = '',
    [string]$ServerScriptPath = '',
    [string]$McpServerName  = 'homeassistant'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── 1. Find config file ───────────────────────────────────────────────────────

function Find-ClaudeConfig {
    $candidates = @(
        # Packaged app (Microsoft Store / WinGet install)
        (Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter 'Claude_*' -ErrorAction SilentlyContinue |
            Select-Object -First 1 |
            ForEach-Object { Join-Path $_.FullName 'LocalCache\Roaming\Claude\claude_desktop_config.json' }),

        # Classic AppData paths
        "$env:APPDATA\Claude\claude_desktop_config.json",
        "$env:APPDATA\Anthropic\Claude\claude_desktop_config.json",
        "$env:LOCALAPPDATA\Claude\claude_desktop_config.json",
        "$env:LOCALAPPDATA\Anthropic\Claude\claude_desktop_config.json"
    )

    foreach ($path in $candidates) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }

    # Last resort: search the whole AppData tree (slower)
    Write-Host "Searching AppData for claude_desktop_config.json..." -ForegroundColor Yellow
    $found = Get-ChildItem "$env:APPDATA", "$env:LOCALAPPDATA" -Recurse -Filter 'claude_desktop_config.json' -ErrorAction SilentlyContinue |
             Select-Object -First 1
    return $found?.FullName
}

$configPath = Find-ClaudeConfig

if (-not $configPath) {
    Write-Error "Could not locate claude_desktop_config.json. Is Claude Desktop installed?"
    exit 1
}

Write-Host "Found config: $configPath" -ForegroundColor Green

if (-not $ServerScriptPath) {
    $cwdServerPath = Join-Path (Get-Location).Path 'server.py'
    $scriptDirServerPath = Join-Path $PSScriptRoot 'server.py'
    if (Test-Path $cwdServerPath) {
        $ServerScriptPath = $cwdServerPath
    } else {
        $ServerScriptPath = $scriptDirServerPath
    }
}

# ── 2. Validate inputs ────────────────────────────────────────────────────────

if (-not $HaToken) {
    $HaToken = Read-Host "Enter your Home Assistant Long-Lived Access Token"
}

if (-not (Test-Path $ServerScriptPath)) {
    Write-Warning "server.py not found at: $ServerScriptPath"
    $ServerScriptPath = Read-Host "Enter the full path to server.py"
    if (-not (Test-Path $ServerScriptPath)) {
        Write-Error "server.py still not found at: $ServerScriptPath"
        exit 1
    }
}

# ── 3. Read and parse existing config ────────────────────────────────────────

$raw = Get-Content $configPath -Raw -Encoding UTF8

if ([string]::IsNullOrWhiteSpace($raw)) {
    $config = [PSCustomObject]@{}
} else {
    try {
        $config = $raw | ConvertFrom-Json
    } catch {
        Write-Error "Failed to parse existing config as JSON: $_"
        exit 1
    }
}

# ── 4. Build MCP server entry ─────────────────────────────────────────────────

$newServer = [PSCustomObject]@{
    command = 'python'
    args    = @($ServerScriptPath)
    env     = [PSCustomObject]@{
        HA_URL   = $HaUrl
        HA_TOKEN = $HaToken
    }
}

# Ensure mcpServers key exists
if (-not (Get-Member -InputObject $config -Name 'mcpServers' -MemberType NoteProperty)) {
    $config | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value ([PSCustomObject]@{})
}

# Add or overwrite this server entry
if (Get-Member -InputObject $config.mcpServers -Name $McpServerName -MemberType NoteProperty) {
    Write-Host "Updating existing '$McpServerName' MCP entry..." -ForegroundColor Yellow
    $config.mcpServers.$McpServerName = $newServer
} else {
    Write-Host "Adding new '$McpServerName' MCP entry..." -ForegroundColor Yellow
    $config.mcpServers | Add-Member -MemberType NoteProperty -Name $McpServerName -Value $newServer
}

# ── 5. Write updated config ───────────────────────────────────────────────────

if ($PSCmdlet.ShouldProcess($configPath, 'Write updated MCP config')) {
    $backup = "$configPath.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $configPath $backup
    Write-Host "Backup saved: $backup" -ForegroundColor Cyan
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Host "Config updated successfully." -ForegroundColor Green
}

# ── 6. Summary ────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " MCP Server: $McpServerName"              -ForegroundColor Cyan
Write-Host " HA URL:     $HaUrl"                      -ForegroundColor Cyan
Write-Host " Script:     $ServerScriptPath"           -ForegroundColor Cyan
Write-Host " Config:     $configPath"                 -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart Claude Desktop to load the new MCP server." -ForegroundColor White
