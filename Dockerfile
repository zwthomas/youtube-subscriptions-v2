FROM python:3

WORKDIR /usr/src/app
COPY ./* /usr/src/app/

# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
# RUN tar -xzf geckodriver-v0.27.0-linux64.tar.gz
# RUN mv geckodriver /usr/bin


# # Install latest stable chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get -y update
# RUN apt-get install -y google-chrome-stable

# # Download and install latest chrome driver
# RUN \
#  CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#  wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
#  unzip chromedriver_linux64.zip && \
#  rm chromedriver_linux64.zip && \
#  mv chromedriver /usr/bin

RUN git clone https://github.com/zwthomas/youtube-subscriptions-v2.git ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "./youtube.py"]