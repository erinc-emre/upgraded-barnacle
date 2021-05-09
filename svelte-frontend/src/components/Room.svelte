<script>
  import { video, debug_info } from "../store/socket";
</script>

<div class="row" width="100%">
  <div class="col-sm">
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Debug Info</h5>
        <div class="card-scroller">
          {#each $debug_info as info, i}<b>{info[0]}</b>: {info[1]}{/each}
        </div>
      </div>
    </div>
  </div>

  <div class="col"><img src={$video} alt="video" /></div>
</div>
