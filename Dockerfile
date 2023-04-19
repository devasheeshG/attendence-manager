FROM python:latest
RUN pip install --upgrade pip

# Install dependencies
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y tesseract-ocr

# RUN wget https://intoli.com/install-google-chrome.sh
# RUN bash install-google-chrome.sh
# RUN cp /usr/bin/google-chrome-stable /usr/bin/google-chrome
# RUN google-chrome --version && which google-chrome

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN apt-get install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libu2f-udev libvulkan1 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils

RUN apt-get install -f && dpkg -i google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb --force-depends
RUN google-chrome --version && which google-chrome

# RUN apt-get install -y chromium-browser

RUN wget https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip
RUN apt-get install unzip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chromedriver --version

RUN apt-get update && apt-get upgrade -y

# Expose port
EXPOSE 8501

# Copy files
COPY main.py /app
COPY stop_script.py /app
COPY databases/* /app/databases/

# Icon
COPY icon.png /usr/share/icons/hicolor/256x256/apps/attendence-manager.png
COPY icon.png /usr/share/icons/hicolor/512x512/apps/attendence-manager.png

CMD ["bash", "-c", "trap 'python3 stop_script.py' EXIT; python3 main.py"]
# CMD ["bash", "-c", "trap 'echo Stop Signal Received; sleep 2; python3 stop_script.py' EXIT; python3 main.py"]