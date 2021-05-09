<script>
	import { device_info } from "./store/socket.js";
	import Container from "./components/Container.svelte";
	import DeviceList from "./components/DeviceList.svelte";
	import Room from "./components/Room.svelte";

	let loading = true;
	let connectedToDevice = false;

	let unsubscribe = device_info.subscribe((val) => {
		loading = false;
		connectedToDevice = val !== null;
	});
</script>

<Container>
	{#if loading}
		Loading...
	{:else if connectedToDevice}
		<Room />
	{:else}
		<DeviceList />
	{/if}
</Container>
