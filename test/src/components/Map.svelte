<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from "svelte";

  // Props
  export let apiKey: string;
  export let center: { lat: number; lng: number };
  export let zoom: number = 12;
  export let disableDefaultUI: boolean = false;
  export let height: string = "400px"; // quick control from parent

  let mapEl: HTMLDivElement;
  let map: google.maps.Map | null = null;
  const dispatch = createEventDispatcher();

  // --- Tiny loader for Google Maps JS API (no external deps) ---
  const SCRIPT_ID = "google-maps-js";

  function loadGoogleMaps(apiKey: string): Promise<void> {
    // already loaded?
    if (typeof window !== "undefined" && (window as any).google?.maps) {
      return Promise.resolve();
    }

    // already injecting?
    if (document.getElementById(SCRIPT_ID)) {
      return new Promise((resolve, reject) => {
        const check = () => {
          if ((window as any).google?.maps) resolve();
          else setTimeout(check, 50);
        };
        check();
      });
    }

    return new Promise((resolve, reject) => {
      const cbName = "__initGoogleMaps__" + Math.random().toString(36).slice(2);
      (window as any)[cbName] = () => {
        resolve();
        // cleanup callback reference
        try {
          delete (window as any)[cbName];
        } catch {}
      };

      const script = document.createElement("script");
      script.id = SCRIPT_ID;
      script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=${cbName}`;
      script.async = true;
      script.defer = true;
      script.onerror = () =>
        reject(new Error("Failed to load Google Maps JS API"));
      document.head.appendChild(script);
    });
  }

  // --- Mount / reactive updates ---
  onMount(async () => {
    await loadGoogleMaps(apiKey);

    map = new google.maps.Map(mapEl, {
      center,
      zoom,
      disableDefaultUI,
    });

    dispatch("ready", { map });
  });

  // Keep map in sync if center/zoom change
  $: if (map && center) map.setCenter(center);
  $: if (map && typeof zoom === "number") map.setZoom(zoom);

  onDestroy(() => {
    // Nothing mandatory to dispose; GC will collect when element is removed.
    map = null;
  });
</script>

<!-- Map container -->
<div bind:this={mapEl} class="map" style={`height:${height}`}></div>

<style>
  .map {
    width: 100%;
    border-radius: 12px;
  }
</style>
