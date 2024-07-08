#!/bin/bash

# https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac
brew install pulseaudio

pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon

docker build -f Dockerfile_pyttsx3_test -t pyttsx3_test .

docker run -it -e PULSE_SERVER=docker.for.mac.localhost -v ~/.config/pulse:/home/pulseaudio/.config/pulse --rm pyttsx3_test