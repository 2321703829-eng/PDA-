$ErrorActionPreference = 'Stop'

$scriptPath = 'd:\Desktop\Odoo\ai-code\.runtime\tenant_reverse_proxy.py'
$logDir = 'd:\Desktop\Odoo\ai-code\.runtime\logs'
$outLog = Join-Path $logDir 'tenant_reverse_proxy.out.log'
$errLog = Join-Path $logDir 'tenant_reverse_proxy.err.log'

if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$existingByPort = netstat -ano | Select-String ':8090 '
if ($existingByPort) {
    throw 'Port 8090 is already in use. Stop the existing listener before starting the tenant reverse proxy.'
}

$args = @(
    $scriptPath,
    '--listen-host', '127.0.0.1',
    '--listen-port', '8090',
    '--map', 'kebi.tianshu.test=127.0.0.1:8070',
    '--map', 'dev.tianshu.test=127.0.0.1:8071'
)

$proc = Start-Process -FilePath 'python' -ArgumentList $args -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog

Start-Sleep -Seconds 2

[PSCustomObject]@{
    ProxyPid = $proc.Id
    Listen = '127.0.0.1:8090'
    Hosts = 'kebi.tianshu.test, dev.tianshu.test'
    KebiBackend = '127.0.0.1:8070'
    DevBackend = '127.0.0.1:8071'
}
