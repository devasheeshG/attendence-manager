pip install --upgrade pip
apt-get update && apt-get upgrade -y
apt-get install -y tesseract-ocr
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -f && dpkg -i google-chrome-stable_current_amd64.deb
wget https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
apt install -y libgl1-mesa-glx
apt --fix-broken install
apt install -y libgl1-mesa-glx
apt-get update && apt-get upgrade -y
# apt --fix-broken install
rm google-chrome-stable_current_amd64.deb
rm chromedriver_linux64.zip