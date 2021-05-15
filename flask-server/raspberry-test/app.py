import time
import socketio
from datetime import datetime
import bson
import threading
import cv2
import base64
from imutils.video import VideoStream
import argparse

"""
Use object detection to detect objects in the frame in realtime. The
types of objects detected can be changed by selecting different models.
To change the computer vision model, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_model.html
To change the engine and accelerator, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html
"""

sio = socketio.Client()

lock = threading.Lock()
lock.acquire(blocking=False)


@sio.event(namespace='/device')
def connect():
    print('[INFO] Successfully connected to server.')


@sio.event(namespace='/device')
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.event(namespace='/device')
def disconnect():
    print('[INFO] Disconnected from server.')


@sio.event(namespace='/device')
def web_client_connected(data):
    lock.release()
    print('web_client_connected', data)


@sio.event(namespace='/device')
def web_client_disconnected(data):
    lock.acquire(blocking=True)
    print('web_client_disconnected', data)


@sio.event(namespace='/device')
def video(data):
    print(data)


device_info = {'device_name': 'camera_device'}


class CVClient(object):

    def __init__(self, server_addr, stream_fps=60):
        self.server_addr = server_addr
        self.server_port = 5001
        self._stream_fps = stream_fps
        self._last_update_t = time.time()
        self._wait_t = (1/self._stream_fps)*3

    def create_room(self):
        sio.emit('join', device_info, '/device')

    def setup(self):
        print('[INFO] Connecting to server http://{}:{}...'.format(
            self.server_addr, self.server_port))
        sio.connect(
            'http://{}:{}'.format(self.server_addr, self.server_port),
            transports=['websocket'],
            namespaces=['/device'],
            wait=True, wait_timeout=1)
        self.create_room()
        return self

    def _convert_image_to_jpeg(self, image):
        # Encode frame as jpeg
        frame = cv2.imencode('.jpg', image)[1].tobytes()
        # frame = bson.encode_binary(frame)
        return frame

    def send_image(self, name, frame):
        cur_t = time.time()
        if cur_t - self._last_update_t > self._wait_t:
            self._last_update_t = cur_t
            b_frame_jpeg = self._convert_image_to_jpeg(frame)

            sio.emit(
                event='video',
                namespace='/device',
                data=bson.dumps({
                    # 'image': base64.b64encode(b_frame_jpeg).decode('utf-8'),
                    'time': name,
                    'image': b_frame_jpeg
                    # 'binaryJpeg': bson.encode_binary(b_frame_jpeg)
                })
            )

    def check_exit(self):
        pass

    def close(self):
        sio.disconnect()


def main(camera, server_addr):
    sender = CVClient(server_addr).setup()
    try:
        while 1:
            lock.acquire(blocking=True)
            image = camera.read()
            sender.send_image(datetime.now().timestamp()*1000, image)
            lock.release()
    finally:
        if sender is not None:
            sender.close()
        print("Program Ending")


parser = argparse.ArgumentParser(description='')
parser.add_argument(
    '--server-addr',  type=str, default='localhost',
    help='The IP address or hostname of the SocketIO server.')
args = parser.parse_args()

if __name__ == "__main__":
    camera = VideoStream().start()
    time.sleep(2.0)  # allow camera sensor to warm up
    main(camera, args.server_addr)
