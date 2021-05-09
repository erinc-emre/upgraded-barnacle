import { io } from "socket.io-client";
import { writable } from 'svelte/store';
import BSON from 'bson';

console.log("BSON", BSON)

let domain = "localhost";
let port = "5001";

export const device_list = writable([])
export const video = writable('')
export const device_info = writable(null)
export const debug_info = writable([])

var socket = io("http://" + domain + ":" + port + "/web", {
	reconnection: false,
});

socket.on("connect", () => {
	console.log("Connected");
});

socket.on("disconnect", () => {
	console.log("Disconnected");
	socket.emit("leave");
});

socket.on("connect_error", (error) => {
	console.log("Connect error! " + error);
});

socket.on("connect_timeout", (error) => {
	console.log("Connect timeout! " + error);
});

socket.on("error", (error) => {
	console.log("Error! " + error);
});

socket.on("message", (data) => {
	console.log("message", data);
});

socket.on("list_devices", (data) => {
	device_list.set(Object.values(data));
	console.log("list_devices", data);
});

socket.on("device_state", (data) => {
	console.log("device_state", data);
});

socket.on('device_mount', (data) => {
	console.log('device_mount', data)
	device_info.set(data)
})

socket.on('video', (bson_data) => {
	let data = BSON.deserialize(bson_data)
	debug_info.set([
		['latency', performance.timing.navigationStart + performance.now() - data.time]
	])
	let imageB64 = btoa(String.fromCharCode.apply(null, data.image.buffer))
	video.set(`data:image/jpeg;base64,${imageB64}`)
})

export const connect_device = async (device_id) => {
	console.log(device_id)

	socket.emit("join", { deviceSid: device_id })
}


