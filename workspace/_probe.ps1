Set-Location C:\Jarvis\agent
"HASH: " + (Get-FileHash jarvis_core.py -Algorithm SHA256).Hash
"SIZE: " + (Get-Item jarvis_core.py).Length
"MTIME: " + (Get-Item jarvis_core.py).LastWriteTime
Select-String -Path .env -Pattern '^(GROQ_API_KEY|JARVIS_API_KEY|JARVIS_BASE_URL|JARVIS_MODEL|JARVIS_LOCAL_MODEL|JARVIS_MAX_[A-Z_]+|JARVIS_OLLAMA_URL)=(.*)$' | ForEach-Object {
  $n = $_.Matches[0].Groups[1].Value
  $v = $_.Matches[0].Groups[2].Value
  if ($n -match 'KEY') { "$n set=" + [bool]$v.Trim() } else { "$n=$v" }
}
try {
  $r = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 3
  "OLLAMA models: " + (($r.Content | ConvertFrom-Json).models.name -join ", ")
} catch { "OLLAMA unreachable: " + $_.Exception.Message }
"SKILL FILES: " + (Get-ChildItem C:\Jarvis\skills -Filter *.py).Count
