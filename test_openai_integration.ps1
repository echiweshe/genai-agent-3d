# Test OpenAI Integration in SVG to Video Pipeline
# Save this as test_openai_integration.ps1

# Function for colorful output
function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Display header
Write-ColorMessage "=============================================" "Cyan"
Write-ColorMessage "          Testing OpenAI Integration         " "Cyan"
Write-ColorMessage "=============================================" "Cyan"

# Check if OpenAI API key is set
Write-ColorMessage "Checking for OpenAI API key..." "Yellow"
$envPath = Join-Path -Path $PSScriptRoot -ChildPath ".env"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    if ($envContent -match "OPENAI_API_KEY=([^\r\n]*)") {
        $apiKey = $Matches[1]
        if ($apiKey -and $apiKey -ne "your_openai_api_key") {
            Write-ColorMessage "✅ OpenAI API key found in .env file" "Green"
        } else {
            Write-ColorMessage "❌ OpenAI API key is not set properly in .env file" "Red"
            Write-ColorMessage "Please update your .env file with a valid OPENAI_API_KEY" "Yellow"
            exit 1
        }
    } else {
        Write-ColorMessage "❌ OpenAI API key not found in .env file" "Red"
        Write-ColorMessage "Please add OPENAI_API_KEY to your .env file" "Yellow"
        exit 1
    }
} else {
    Write-ColorMessage "❌ .env file not found" "Red"
    Write-ColorMessage "Please create a .env file with your OPENAI_API_KEY" "Yellow"
    exit 1
}

# Test OpenAI SVG generation
Write-ColorMessage "Testing OpenAI SVG generation..." "Yellow"

# Create a temporary directory for test outputs
$testDir = Join-Path -Path $PSScriptRoot -ChildPath "outputs\openai_test"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir | Out-Null
}

# Test concepts for SVG generation
$testConcepts = @(
    "A simple flowchart with three steps: Start, Process, End",
    "A network diagram showing a client, server, and database",
    "A decision tree with Yes/No branches"
)

# Generate SVGs using OpenAI
foreach ($concept in $testConcepts) {
    $conceptShort = $concept.Substring(0, [Math]::Min(20, $concept.Length)).Replace(" ", "_")
    $outputPath = Join-Path -Path $testDir -ChildPath "openai_$conceptShort.svg"
    
    Write-ColorMessage "Generating SVG for: $concept" "Yellow"
    
    # Use the CLI to generate an SVG with OpenAI
    $command = ".\run_svg_cli.bat svg `"$concept`" `"$outputPath`" --provider openai"
    
    try {
        Invoke-Expression $command
        
        if (Test-Path $outputPath) {
            # Check if the file has content
            $content = Get-Content $outputPath -Raw
            if ($content -and $content.Contains("<svg") -and $content.Contains("</svg>")) {
                Write-ColorMessage "✅ SVG generated successfully: $outputPath" "Green"
            } else {
                Write-ColorMessage "❌ Generated file does not contain valid SVG content" "Red"
            }
        } else {
            Write-ColorMessage "❌ Failed to generate SVG: $outputPath" "Red"
        }
    } catch {
        Write-ColorMessage "❌ Error generating SVG: $_" "Red"
    }
}

# Test API access directly
Write-ColorMessage "Testing direct API access..." "Yellow"

$apiUrl = "http://localhost:8001/api/svg-to-video/providers"
try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Get
    
    # Check if openai is in the providers list
    $hasOpenAI = $false
    foreach ($provider in $response) {
        if ($provider.id -eq "openai" -or $provider.name -eq "openai") {
            $hasOpenAI = $true
            break
        }
    }
    
    if ($hasOpenAI) {
        Write-ColorMessage "✅ OpenAI found in available providers" "Green"
    } else {
        Write-ColorMessage "❌ OpenAI not found in available providers" "Red"
        Write-ColorMessage "Available providers:" "Yellow"
        $response | Format-Table | Out-String | Write-ColorMessage -ForegroundColor Yellow
    }
} catch {
    Write-ColorMessage "❌ Error accessing API: $_" "Red"
    Write-ColorMessage "Make sure the server is running on port 8001" "Yellow"
}

# Test SVG generation through the API
Write-ColorMessage "Testing SVG generation through API..." "Yellow"

$concept = "A simple diagram created with OpenAI"
$apiUrl = "http://localhost:8001/api/svg-to-video/generate-svg?concept=$([System.Uri]::EscapeDataString($concept))&provider=openai"

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Get
    
    if ($response.svg_content -and $response.svg_content.Contains("<svg") -and $response.svg_content.Contains("</svg>")) {
        Write-ColorMessage "✅ Successfully generated SVG via API with OpenAI" "Green"
        
        # Save the SVG to a file
        $outputPath = Join-Path -Path $testDir -ChildPath "openai_api_test.svg"
        $response.svg_content | Out-File -FilePath $outputPath -Encoding utf8
        Write-ColorMessage "✅ Saved SVG to: $outputPath" "Green"
    } else {
        Write-ColorMessage "❌ Response does not contain valid SVG content" "Red"
        Write-ColorMessage "Response: $($response | ConvertTo-Json -Depth 3)" "Yellow"
    }
} catch {
    Write-ColorMessage "❌ Error generating SVG via API: $_" "Red"
    Write-ColorMessage "Make sure the server is running on port 8001" "Yellow"
}

# Summary
Write-ColorMessage "=============================================" "Cyan"
Write-ColorMessage "            OpenAI Integration Test          " "Cyan"
Write-ColorMessage "=============================================" "Cyan"
Write-ColorMessage "Test outputs saved to: $testDir" "Green"
Write-ColorMessage "Check the generated SVGs to verify quality and correctness" "Yellow"
Write-ColorMessage "=============================================" "Cyan"
