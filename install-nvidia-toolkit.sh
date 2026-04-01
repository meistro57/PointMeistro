#!/bin/bash

echo "🔧 Installing NVIDIA Container Toolkit (Alternative Method)"
echo "============================================================"
echo ""

# Clean up broken repo file
echo "Cleaning up broken repository file..."
sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Method 1: Try direct package installation
echo ""
echo "Installing NVIDIA Container Toolkit from Ubuntu repos..."
sudo apt-get update

# Install from Ubuntu's own repositories
sudo apt-get install -y nvidia-container-toolkit || {
    echo ""
    echo "Method 1 failed. Trying manual installation..."
    echo ""
    
    # Method 2: Direct .deb download
    echo "Downloading packages directly..."
    cd /tmp
    
    # Get the latest stable release
    curl -sLO https://nvidia.github.io/libnvidia-container/stable/deb/amd64/libnvidia-container1_1.14.6-1_amd64.deb
    curl -sLO https://nvidia.github.io/libnvidia-container/stable/deb/amd64/libnvidia-container-tools_1.14.6-1_amd64.deb
    curl -sLO https://nvidia.github.io/libnvidia-container/stable/deb/amd64/nvidia-container-toolkit-base_1.14.6-1_amd64.deb
    curl -sLO https://nvidia.github.io/libnvidia-container/stable/deb/amd64/nvidia-container-toolkit_1.14.6-1_amd64.deb
    
    # Install the packages
    sudo dpkg -i libnvidia-container1_1.14.6-1_amd64.deb
    sudo dpkg -i libnvidia-container-tools_1.14.6-1_amd64.deb
    sudo dpkg -i nvidia-container-toolkit-base_1.14.6-1_amd64.deb
    sudo dpkg -i nvidia-container-toolkit_1.14.6-1_amd64.deb
    
    # Fix any dependency issues
    sudo apt-get install -f -y
}

echo ""
echo "Configuring Docker to use NVIDIA runtime..."
sudo nvidia-ctk runtime configure --runtime=docker

echo ""
echo "Restarting Docker..."
sudo systemctl restart docker || sudo service docker restart

echo ""
echo "✅ Installation complete!"
echo ""
echo "Testing GPU access in Docker..."
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! GPU is accessible in Docker containers!"
    echo ""
    echo "You're ready to run PointMeistro:"
    echo "  ./setup.sh"
else
    echo ""
    echo "❌ GPU test failed. Checking Docker config..."
    cat /etc/docker/daemon.json
fi
