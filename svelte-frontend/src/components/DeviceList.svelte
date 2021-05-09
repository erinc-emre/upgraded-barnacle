<script>
	import { device_list, connect_device } from "../store/socket";
</script>

<div class="container-sm py-4" style="max-width: 540px">
	<div class="card">
		<div class="card-body">
			<h3 class="card-title">Devices</h3>
			<div class="list-group">
				{#each $device_list as { occupier, deviceSid, device_name }, i}
					<button
						type="button"
						class="list-group-item list-group-item-action"
						on:click={() => connect_device(deviceSid)}>
						<i
							class={'fas fa-circle pr-2 ' + (occupier !== null ? 'text-danger' : 'text-success')} />
						{` ${device_name}`}
					</button>
				{/each}
			</div>
		</div>
	</div>
</div>
