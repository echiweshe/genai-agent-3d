# Root wrapper script for SVG to Video Pipeline
# This script forwards all commands to the actual implementation

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetScript = Join-Path $scriptPath "scripts\run\run_svg_to_video.ps1"

# Forward all arguments to the target script
& $targetScript $args
