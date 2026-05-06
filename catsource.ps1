param(
    [string]$OutputFile = "a3chuyentin_source.txt"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Convert-GitignoreToRegex {
    param([string]$pattern)
    
    $negate = $false
    if ($pattern.StartsWith('!')) {
        $negate = $true
        $pattern = $pattern.Substring(1)
    }
    
    $isDirectory = $pattern.EndsWith('/')
    $isAnchored = $pattern.StartsWith('/')
    
    if ($isAnchored) {
        $pattern = $pattern.Substring(1)
    }
    
    $pattern = $pattern.Replace('\', '/')
    
    $parts = $pattern.Split('/')
    $regexParts = @()
    
    for ($i = 0; $i -lt $parts.Length; $i++) {
        $part = $parts[$i]
        if ($part -eq '**') {
            $regexParts += '.*'
        } else {
            $part = $part.Replace('.', '\.')
            $part = $part.Replace('*', '[^/]*')
            $part = $part.Replace('?', '.')
            $regexParts += $part
        }
    }
    
    $regex = $regexParts -join '/'
    
    if ($isAnchored) {
        $regex = '^' + $regex
    } else {
        if ($regex.StartsWith('.*/')) {
            $regex = '^(.*/)?' + $regex.Substring(3)
        } else {
            $regex = '^(.*/)?' + $regex
        }
    }
    
    if ($isDirectory) {
        if ($regex.EndsWith('/')) {
            $regex = $regex + '.*$'
        } else {
            $regex = $regex + '/.*$'
        }
    } else {
        $regex = $regex + '$'
    }
    
    return @{ Regex = $regex; Negate = $negate }
}

$gitignorePath = Join-Path $projectRoot ".gitignore"
$patterns = @()

if (Test-Path $gitignorePath) {
    $lines = Get-Content $gitignorePath | Where-Object { 
        $_ -and -not $_.StartsWith("#") 
    }
    
    foreach ($line in $lines) {
        $ptn = $line.Trim()
        $patterns += Convert-GitignoreToRegex -pattern $ptn
    }
}

$defaultIgnores = @(
    '.git/',
    'node_modules/',
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    'venv/',
    '.venv/',
    '.env',
    'db.sqlite3',
    'static/dist/',
    'a3chuyentin_source.txt',
    'cat_source.ps1'
)

foreach ($p in $defaultIgnores) {
    $patterns += Convert-GitignoreToRegex -pattern $p
}

function Should-Ignore {
    param([string]$relativePath)
    
    $result = $false
    
    foreach ($p in $patterns) {
        if ($relativePath -match $p.Regex) {
            $result = -not $p.Negate
        }
    }
    
    return $result
}

$outputPath = Join-Path $projectRoot $OutputFile

try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $writer = [System.IO.StreamWriter]::new($outputPath, $false, $utf8NoBom)
    
    $writer.WriteLine("=" * 80)
    $writer.WriteLine("PROJECT SOURCE: A3 Chuyên Tin (a3chuyentin)")
    $writer.WriteLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    $writer.WriteLine("=" * 80)
    $writer.WriteLine("")
    
    $allFiles = Get-ChildItem -Path $projectRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        -not $_.FullName.Contains("\.git\")
    }
    
    foreach ($file in $allFiles) {
        $relativePath = $file.FullName.Substring($projectRoot.Length + 1).Replace('\', '/')
        
        if (-not (Should-Ignore -relativePath $relativePath)) {
            $writer.WriteLine("=" * 80)
            $writer.WriteLine("FILE: $relativePath")
            $writer.WriteLine("=" * 80)
            $writer.WriteLine("")
            
            try {
                $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
                if ($content) {
                    $writer.WriteLine($content)
                } else {
                    $writer.WriteLine("[Empty file]")
                }
            } catch {
                $writer.WriteLine("[Binary file or unreadable]")
            }
            $writer.WriteLine("")
        }
    }
    
    $writer.Close()
}
catch {
    if ($writer) { $writer.Dispose() }
    exit 1
}