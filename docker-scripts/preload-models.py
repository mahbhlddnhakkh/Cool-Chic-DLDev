import sys
import os

# Fixes: `Downloading: "https://download.pytorch.org/models/vgg16-397923af.pth" to /root/.cache/torch/hub/checkpoints/vgg16-397923af.pth`

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "coolchic", "enc", "training", "metrics"))
    import wasserstein
    preload_1 = wasserstein.Vgg16()
