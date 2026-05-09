param(
    [string]$ServerIp = '192.168.0.17',
    [string[]]$Domains = @(
        'hq.odoo.test',
        'kebi.odoo.test',
        'template.odoo.test'
    ),
    [string]$WrongHost = 'wrong.odoo.test',
    [string]$OutputDir = "$env:USERPROFILE\\Desktop\\odoo-team-access-diagnostics"
)

$ErrorActionPreference = 'Continue'

function Invoke-Step {
    param(
        [string]$Title,
        [scriptblock]$Script
    )

    "`r`n==== $Title ====" | Tee-Object -FilePath $script:TextReport -Append | Out-Null
    try {
        $result = & $Script 2>&1 | Out-String
    } catch {
        $result = $_ | Out-String
    }
    $result.TrimEnd() | Tee-Object -FilePath $script:TextReport -Append | Out-Null
    return $result.TrimEnd()
}

function Invoke-CurlHead {
    param([string]$Url)
    try {
        return (& curl.exe -I --max-time 15 $Url 2>&1 | Out-String).TrimEnd()
    } catch {
        return ($_ | Out-String).TrimEnd()
    }
}

function Get-HostEntries {
    $hostsPath = 'C:\Windows\System32\drivers\etc\hosts'
    if (-not (Test-Path -LiteralPath $hostsPath)) {
        return 'hosts file not found'
    }
    $patterns = @('hq.odoo.test', 'kebi.odoo.test', 'template.odoo.test', 'wrong.odoo.test')
    $lines = Get-Content -LiteralPath $hostsPath -ErrorAction SilentlyContinue
    $matched = foreach ($line in $lines) {
        foreach ($pattern in $patterns) {
            if ($line -match [regex]::Escape($pattern)) {
                $line
                break
            }
        }
    }
    if (-not $matched) {
        return 'No matching hosts entries found.'
    }
    return ($matched | Out-String).TrimEnd()
}

function Get-BrowserProxyHints {
    $hints = @()
    try {
        $internetSettings = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction Stop
        $hints += "ProxyEnable=$($internetSettings.ProxyEnable)"
        $hints += "ProxyServer=$($internetSettings.ProxyServer)"
        $hints += "ProxyOverride=$($internetSettings.ProxyOverride)"
        $hints += "AutoConfigURL=$($internetSettings.AutoConfigURL)"
    } catch {
        $hints += "Internet Settings read failed: $($_.Exception.Message)"
    }
    return ($hints -join "`r`n")
}

function Get-HttpStatusSummary {
    param([string]$HeadersText)
    $match = [regex]::Match($HeadersText, 'HTTP/\d+\.\d+\s+(\d{3})')
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return 'NO_STATUS'
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$computer = $env:COMPUTERNAME
$script:TextReport = Join-Path $OutputDir "odoo_team_access_diag_${computer}_$timestamp.txt"
$jsonReport = Join-Path $OutputDir "odoo_team_access_diag_${computer}_$timestamp.json"

$summary = [ordered]@{
    computer_name = $computer
    user_name = $env:USERNAME
    timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    server_ip = $ServerIp
    domains = $Domains
}

"Odoo team access diagnostics" | Set-Content -LiteralPath $script:TextReport
"Computer: $computer" | Add-Content -LiteralPath $script:TextReport
"Time: $($summary.timestamp)" | Add-Content -LiteralPath $script:TextReport
"Server IP: $ServerIp" | Add-Content -LiteralPath $script:TextReport
"Domains: $($Domains -join ', ')" | Add-Content -LiteralPath $script:TextReport

$summary.system = [ordered]@{}
$summary.system.hostname = Invoke-Step 'System / hostname' { hostname }
$summary.system.ipconfig = Invoke-Step 'System / ipconfig' { ipconfig }
$summary.system.winhttp_proxy = Invoke-Step 'System / WinHTTP proxy' { netsh winhttp show proxy }
$summary.system.browser_proxy = Invoke-Step 'System / Internet Settings proxy hints' { Get-BrowserProxyHints }
$summary.system.hosts_entries = Invoke-Step 'System / matching hosts entries' { Get-HostEntries }

$summary.network = [ordered]@{}
$summary.network.server_port_80 = Invoke-Step "Network / Test-NetConnection $ServerIp:80" {
    Test-NetConnection $ServerIp -Port 80 | Format-List * | Out-String
}

$summary.domains_detail = @()
foreach ($domain in $Domains) {
    $nslookup = Invoke-Step "DNS / nslookup $domain" { nslookup $domain }
    $ping = Invoke-Step "DNS / ping $domain" { ping $domain }
    $tnc = Invoke-Step "Network / Test-NetConnection $domain:80" {
        Test-NetConnection $domain -Port 80 | Format-List * | Out-String
    }
    $curlWeb = Invoke-Step "HTTP / curl -I http://$domain/web" {
        Invoke-CurlHead -Url "http://$domain/web"
    }
    $curlLogin = Invoke-Step "HTTP / curl -I http://$domain/web/login" {
        Invoke-CurlHead -Url "http://$domain/web/login"
    }

    $summary.domains_detail += [ordered]@{
        domain = $domain
        nslookup = $nslookup
        ping = $ping
        test_net_connection = $tnc
        curl_web = $curlWeb
        curl_web_status = Get-HttpStatusSummary -HeadersText $curlWeb
        curl_login = $curlLogin
        curl_login_status = Get-HttpStatusSummary -HeadersText $curlLogin
    }
}

$summary.wrong_host = [ordered]@{}
$summary.wrong_host.curl = Invoke-Step "HTTP / curl -I http://$WrongHost/web" {
    Invoke-CurlHead -Url "http://$WrongHost/web"
}
$summary.wrong_host.status = Get-HttpStatusSummary -HeadersText $summary.wrong_host.curl

$summary.quick_judgement = [ordered]@{
    expected_server_ip = $ServerIp
    expected_domain_count = $Domains.Count
    notes = @(
        'Expected: each nslookup resolves to 192.168.0.17',
        'Expected: Test-NetConnection to domain:80 succeeds',
        'Expected: curl http://<domain>/web returns 200 or 303',
        'Expected: curl http://wrong.odoo.test/web does not open the real site'
    )
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonReport -Encoding UTF8

Invoke-Step 'Output / report files' {
    @(
        "Text report: $script:TextReport"
        "JSON report: $jsonReport"
    ) -join "`r`n"
} | Out-Null

Write-Host ''
Write-Host 'Diagnostics finished.'
Write-Host "Text report: $script:TextReport"
Write-Host "JSON report: $jsonReport"
