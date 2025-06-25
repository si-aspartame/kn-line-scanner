# Jetson AGX Orin 開発環境構築手順（Basler raL8192 + QRラインスキャン）

```bash
# ==========================
# ✅ xfce デスクトップ環境の導入
# ==========================
sudo apt update
sudo apt install -y xfce4 xfce4-goodies
sudo update-alternatives --config x-session-manager
# → xfce を選択

# ==========================
# ✅ Visual Studio Code 1.65 をインストール（Jetson動作安定版）
# ==========================
wget https://update.code.visualstudio.com/1.65.2/linux-deb-arm64/stable -O vscode_1.65.2_arm64.deb
sudo apt install -y ./vscode_1.65.2_arm64.deb

# ==========================
# ✅ mozc + fcitx（日本語入力）
# ==========================
sudo apt install -y fcitx fcitx-mozc
im-config -n fcitx
# sudo apt install fcitx-config-gtk
# fcitx-configtool
# reboot
# → 再起動後、fcitx設定から Mozc を有効化

# ==========================
# ✅ Python 3.10 のインストール（uv用に明示）
# ==========================
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# ==========================
# ✅ USB自動省電力の無効化
# ==========================
sudo gedit /boot/extlinux/extlinux.conf
# → 以下を APPEND 行の末尾に追加：
#    usbcore.autosuspend=-1
#sudo reboot

# ==========================
# ✅ Basler pylon SDK のインストール
# ==========================
# ※ arm64 向け .deb を公式からダウンロードしてインストール

# 動作確認
/opt/pylon/bin/PylonGigEConfigurator list
sudo /opt/pylon/bin/PylonGigEConfigurator auto-ip
# /opt/pylon/bin/PylonViewerApp
# ==========================
# ✅ Brave Browser インストール（公式install.sh）
# ==========================
curl -fsS https://dl.brave.com/install.sh | sh

# ==========================
# ✅ Python 仮想環境（pypylonテスト用）
# ==========================
# cd ~/Develop/kn-line-scanner
# uv venv --python=python3.10
# source .venv/bin/activate
# uv pip install pypylon pillow
