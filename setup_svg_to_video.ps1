# Wrapper script to set up SVG to Video pipeline
# This is a convenience script that redirects to the actual implementation

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $scriptPath "scripts\setup\setup_svg_to_video.ps1"

# Forward all arguments to the target script
& $targetScript @args
