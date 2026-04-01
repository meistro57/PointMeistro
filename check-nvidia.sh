#!/bin/bash

echo "🔍 NVIDIA Environment Verification for PointMeistro"
echo "===================================================="
echo ""

# Check 1: NVIDIA Driver on Windows/WSL
echo "1️⃣ Checking NVIDIA Driver..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo "✅ NVIDIA driver found"
else
    echo "❌ nvidia-smi not found"
    echo "   Install NVIDIA drivers on Windows first"
    exit 1
fi

echo ""

# Check 2: Docker installed
echo "2️⃣ Checking Docker..."
if command -v docker &> /dev/null; then
    docker --version
    echo "✅ Docker installed"
else
    echo "❌ Docker not installed"
    echo "   Install with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo ""

# Check 3: Docker running
echo "3️⃣ Checking Docker daemon..."
if docker ps &> /dev/null; then
    echo "✅ Docker daemon running"
else
    echo "❌ Docker daemon not running"
    echo "   Start with: sudo service docker start"
    exit 1
fi

echo ""

# Check 4: NVIDIA Container Toolkit
echo "4️⃣ Checking NVIDIA Container Toolkit..."
if dpkg -l | grep -q nvidia-container-toolkit; then
    echo "✅ NVIDIA Container Toolkit installed"
    
    # Check 5: GPU accessible in Docker
    echo ""
    echo "5️⃣ Testing GPU access in Docker..."
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo "✅ GPU accessible in Docker containers!"
        echo ""
        echo "🎉 ALL CHECKS PASSED!"
        echo ""
        echo "Your system is ready for PointMeistro."
        echo "Run: ./setup.sh to deploy"
    else
        echo "❌ GPU not accessible in Docker"
        echo ""
        echo "Fix with:"
        echo "  sudo nvidia-ctk runtime configure --runtime=docker"
        echo "  sudo systemctl restart docker"
        exit 1
    fi
else
    echo "❌ NVIDIA Container Toolkit not installed"
    echo ""
    echo "Install with:"
    echo "  distribution=\$(. /etc/os-release;echo \$ID\$VERSION_ID)"
    echo "  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \\"
    echo "    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
    echo "  curl -s -L https://nvidia.github.io/libnvidia-container/\$distribution/libnvidia-container.list | \\"
    echo "    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \\"
    echo "    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y nvidia-container-toolkit"
    echo "  sudo nvidia-ctk runtime configure --runtime=docker"
    echo "  sudo systemctl restart docker"
    exit 1
fi
