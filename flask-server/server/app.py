from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms


app = Flask(__name__)

socketio = SocketIO(app, logger=True, engineio_logger=False, cors_allowed_origins="*")
# socketio = SocketIO(app,  cors_allowed_origins="*")


"""
room: {
    'occupier': None,
    'deviceSid': request.sid, 
    'device_name': str,
}
"""

rooms_list = {}
occupiers = {}

def broadcast_device_list():
    emit('list_devices', rooms_list, namespace='/web', broadcast=True)

@socketio.on('connect', namespace='/web')
def connect_web(): 
    emit('list_devices', rooms_list)
    print('[INFO] Web client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/web')
def disconnect_web(): 
    if request.sid in occupiers:
        device_sid = occupiers[request.sid]
        rooms_list[device_sid]['occupier'] = None
        del occupiers[request.sid]
        broadcast_device_list()
        emit('web_client_disconnected', { 'clientId': request.sid }, namespace='/device', to=device_sid)

    print('[INFO] Web client disconnected: {}'.format(request.sid))


"""
    Web client wants to connect to a device/room
    1. Send error if device/room is occupied or not found
    2. Set device/room occupied
    3. Add web client to the room
    4. Ask device for device state
"""
@socketio.on('join', namespace='/web')
def connect_to_device(data):
    device_sid = data['deviceSid']
    
    if device_sid not in rooms_list: return send({'error': 'device_not_found'})
    if rooms_list[device_sid]['occupier']: return send({'error': 'device_is_being_occupied'})

    rooms_list[device_sid]['occupier'] = {'sid': request.sid}
    occupiers[request.sid] = device_sid

    join_room(device_sid)
    broadcast_device_list()
    emit('web_client_connected', { 'clientId': request.sid }, namespace='/device', to=device_sid)
    emit('ack_device_state', namespace='/device', to=device_sid)
    emit('device_mount', rooms_list[device_sid], namespace='/web', to=device_sid)


"""
    Web client wants to disconnect from the device/room
    1. Send error if device/room is not found or client is not the owner
    2. Set device/room unoccupied
    3. Add web client to the room
"""
@socketio.on('leave', namespace='/web')
def disconnect_from_device(data):
    device_sid = data['deviceSid']
    
    if device_sid not in rooms_list: return send({'error': 'device_not_found'})
    if rooms_list[device_sid]['occupier']['sid'] != request.sid: return send({'error': 'occupier_is_not_the_client'})

    rooms_list[device_sid]['occupier'] = None
    leave_room(device_sid)
    emit('web_client_disconnected', { 'clientId': request.sid }, namespace='/device', to=device_sid)

"""
    Web client sends 
"""
@socketio.on('update_state', namespace='/web')
def update_state(data):
    client_id = request.sid
    new_state = data['newState']

    if client_id not in occupiers: return send({'error': 'not_subscribed_to_any_device'})
    room_id = occupiers[client_id]
    emit('device_state', new_state, namespace='/device', to=room_id)


@socketio.on('device_state', namespace='/device')
def update_device_state(data):
    room_id = request.sid
    emit('device_state', data, namespace='/web', to=room_id)


"""
    Device wants to connect to server.
"""
@socketio.on('connect', namespace='/device')
def connect_device(): print('[INFO] Device client connected: {}'.format(request.sid))


"""
    Device wants to create a room.
    1. if room already exists return error.
"""
@socketio.on('join', namespace='/device')
def device_join(data):
    device_id = request.sid
    if device_id in rooms_list:
        return send({'error': 'device_is_allready_in_a_room'})

    device_name = data['device_name']

    join_room(device_id)
    rooms_list[device_id] = {
        'occupier': None, 
        'deviceSid': device_id,
        'device_name': device_name,
    }

    broadcast_device_list()


"""
    Device wants to disconnect from the server.
    1. Remove the web client if connected to device/room and send message
    2. Remove device from room_list
    3. Remove device from room
"""
@socketio.on('disconnect', namespace='/device')
def disconnect_device():
    device_sid = request.sid

    if device_sid not in device_sid: return
    del rooms_list[device_sid]
    socketio.close_room(device_sid)


@socketio.on('video', namespace='/device')
def send_video_data(data):
    device_id = request.sid
    if device_id not in rooms_list: return send('error:room_not_created')

    emit('video', data, namespace='/web', to=device_id, broadcast=True, include_self=False,ignore_queue=True)

if __name__ == "__main__":
    print('[INFO] Starting server at http://localhost:5001')
    socketio.run(app=app, host='0.0.0.0', port=5001)
