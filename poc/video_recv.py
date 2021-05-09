import cv2
import imagezmq
image_hub = imagezmq.ImageHub(open_port='tcp://*:5555')

while True:  # show streamed images until ctrl-c
    rpi_name, image = image_hub.recv_image()
    cv2.imshow(rpi_name, image) # 1 window for each rpi
    cv2.waitKey(1)
    image_hub.send_reply(b'OK')