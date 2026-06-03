param(
    [string[]]$TenantUrls = @(
        'http://hq.odoo.test',
        'http://kebi.odoo.test',
        'http://template.odoo.test'
    ),
    [string[]]$ExpectedDbs = @(
        'tenant_hq',
        'tenant_kebi',
        'tenant_template'
    ),
    [string]$UnknownHostProbeUrl = '',
    [string]$UnknownHostHeader = 'wrong.odoo.test'
)

$ErrorActionPreference = 'Stop'

if ($TenantUrls.Count -ne $ExpectedDbs.Count) {
    throw 'TenantUrls and ExpectedDbs must have the same number of entries.'
}

function Get-NormalizedBaseUrl {
    param([string]$Url)

    $trimmed = $Url.TrimEnd('/')
    if ($trimmed.EndsWith('/web')) {
        return $trimmed.Substring(0, $trimmed.Length - 4)
    }
    return $trimmed
}

function Invoke-CheckRequest {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = ''
    )

    try {
        $params = @{
            Method = $Method
            Uri = $Url
            Headers = $Headers
            MaximumRedirection = 5
        }
        if ($Method -eq 'POST') {
            $params['ContentType'] = 'application/json'
            $params['Body'] = $Body
        }
        $response = Invoke-WebRequest @params
        return [PSCustomObject]@{
            StatusCode = [int]$response.StatusCode
            Content = [string]$response.Content
            Headers = $response.Headers
            Ok = $true
            Error = $null
        }
    } catch {
        $statusCode = 0
        $content = ''
        $headers = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $content = $reader.ReadToEnd()
                    $reader.Dispose()
                }
            } catch {
            }
            $headers = $_.Exception.Response.Headers
        }
        return [PSCustomObject]@{
            StatusCode = $statusCode
            Content = [string]$content
            Headers = $headers
            Ok = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-ContainsExpectedDb {
    param(
        [string]$Content,
        [string]$ExpectedDb
    )

    if (-not $Content) {
        return $false
    }

    return (
        $Content.Contains("?dbname=$ExpectedDb") -or
        ($Content.Contains("name=`"db`"") -and $Content.Contains("value=`"$ExpectedDb`"")) -or
        $Content.Contains($ExpectedDb)
    )
}

$results = New-Object System.Collections.Generic.List[object]

for ($i = 0; $i -lt $TenantUrls.Count; $i++) {
    $baseUrl = Get-NormalizedBaseUrl -Url $TenantUrls[$i]
    $expectedDb = $ExpectedDbs[$i]
    $loginUrl = "$baseUrl/web/login"
    $wrongDbUrl = "$baseUrl/web/login?db=wrong_db_for_guard"

    $loginResponse = Invoke-CheckRequest -Method 'GET' -Url $loginUrl
    $wrongDbResponse = Invoke-CheckRequest -Method 'GET' -Url $wrongDbUrl
    $selectorResponse = Invoke-CheckRequest -Method 'GET' -Url "$baseUrl/web/database/selector"
    $managerResponse = Invoke-CheckRequest -Method 'GET' -Url "$baseUrl/web/database/manager"
    $listResponse = Invoke-CheckRequest -Method 'POST' -Url "$baseUrl/web/database/list" -Body '{}'

    $loginStatusOk = $loginResponse.StatusCode -in @(200, 303)
    $dbMarkerOk = Test-ContainsExpectedDb -Content $loginResponse.Content -ExpectedDb $expectedDb
    $wrongDbGuardOk = Test-ContainsExpectedDb -Content $wrongDbResponse.Content -ExpectedDb $expectedDb
    $selectorClosed = $selectorResponse.StatusCode -eq 404
    $managerClosed = $managerResponse.StatusCode -eq 404
    $listClosed = $listResponse.StatusCode -eq 404

    $results.Add([PSCustomObject]@{
        Target = $baseUrl
        ExpectedDb = $expectedDb
        LoginStatus = $loginResponse.StatusCode
        LoginStatusOk = $loginStatusOk
        ExpectedDbMarkerOk = $dbMarkerOk
        WrongDbParamGuardOk = $wrongDbGuardOk
        SelectorStatus = $selectorResponse.StatusCode
        SelectorClosed = $selectorClosed
        ManagerStatus = $managerResponse.StatusCode
        ManagerClosed = $managerClosed
        ListStatus = $listResponse.StatusCode
        ListClosed = $listClosed
    })
}

if ($UnknownHostProbeUrl) {
    $unknownResponse = Invoke-CheckRequest -Method 'GET' -Url $UnknownHostProbeUrl -Headers @{ Host = $UnknownHostHeader }
    $results.Add([PSCustomObject]@{
        Target = $UnknownHostProbeUrl
        ExpectedDb = '<unknown-host>'
        LoginStatus = $unknownResponse.StatusCode
        LoginStatusOk = $false
        ExpectedDbMarkerOk = $false
        WrongDbParamGuardOk = $false
        SelectorStatus = $null
        SelectorClosed = $null
        ManagerStatus = $null
        ManagerClosed = $null
        ListStatus = $null
        ListClosed = $null
        UnknownHostHeader = $UnknownHostHeader
        UnknownHostShouldNotSucceed = ($unknownResponse.StatusCode -notin @(200, 303))
    })
}

$results | Format-Table -AutoSize
