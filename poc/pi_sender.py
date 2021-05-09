import socket
import time
from imutils.video import VideoStream
import imagezmq

sender = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5555')

rpi_name = "test camera"#socket.gethostname() # send RPi hostname with each image
cam = VideoStream().start()

time.sleep(2.0)  # allow camera sensor to warm up
while True:  # send images as stream until Ctrl-C
    image = cam.read()
    sender.send_image(rpi_name, image)