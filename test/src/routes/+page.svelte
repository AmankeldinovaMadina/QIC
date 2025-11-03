<script lang="ts">
  import axios from "axios";
  import "leaflet/dist/leaflet.css";
  import { onMount } from "svelte";

  let query = "restaurants in Astana";
  let results = [];
  let map;
  let mapElement;
  let isLoading = false;

  const defaultLocation = {
    lat: 51.1694,
    lng: 71.4491,
    zoom: 13,
  };

  async function search() {
    isLoading = true;
    try {
      const res = await axios.get(`/api/serp?q=${encodeURIComponent(query)}`);
      results = res.data.local_results || [];

      // Lazy-import Leaflet only in browser
      const L = await import("leaflet");

      if (map) {
        map.remove();
      }

      // Get coordinates from first result or use default
      const firstResult = results[0]?.gps_coordinates;
      const center = firstResult
        ? [firstResult.latitude, firstResult.longitude]
        : [defaultLocation.lat, defaultLocation.lng];

      map = L.map(mapElement, {
        center,
        zoom: defaultLocation.zoom,
        zoomControl: true,
        scrollWheelZoom: true,
        layers: [
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "© OpenStreetMap contributors",
          }),
        ],
      });

      // Add markers for each result
      const bounds = L.latLngBounds([]);

      results.forEach((r) => {
        if (r.gps_coordinates) {
          const pos = [r.gps_coordinates.latitude, r.gps_coordinates.longitude];
          bounds.extend(pos);

          const popupContent = `
              <div class="popup-content">
                <h3>${r.title}</h3>
                ${
                  r.rating
                    ? `
                  <div class="rating">
                    ${"★".repeat(Math.floor(r.rating))}${"☆".repeat(5 - Math.floor(r.rating))}
                    ${r.reviews ? `<span>(${r.reviews})</span>` : ""}
                  </div>
                `
                    : ""
                }
                <p>${r.address}</p>
                ${r.phone_number ? `<p>📞 ${r.phone_number}</p>` : ""}
                ${r.hours ? `<p>⏰ ${r.hours}</p>` : ""}
                ${r.type ? `<p class="type">${r.type}</p>` : ""}
                ${r.website ? `<a href="${r.website}" target="_blank" class="website">Visit Website</a>` : ""}
              </div>
            `;

          L.marker(pos).addTo(map).bindPopup(popupContent, {
            maxWidth: 350,
            className: "custom-popup",
          });
        }
      });

      // Fit bounds if we have results
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }

      // Ensure map renders correctly
      setTimeout(() => map.invalidateSize(), 100);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      isLoading = false;
    }
  }

  onMount(search);
</script>

<div class="container">
  <header>
    <h1>Places Search</h1>
    <div class="search-box">
      <input
        bind:value={query}
        placeholder="Search places..."
        on:keypress={(e) => e.key === "Enter" && search()}
      />
      <button class="search-btn" on:click={search} disabled={isLoading}>
        {#if isLoading}
          <span class="loading"></span>
        {:else}
          Search
        {/if}
      </button>
    </div>
  </header>

  <main>
    <div bind:this={mapElement} class="map"></div>

    <div class="results">
      {#each results as r}
        <div
          class="card"
          on:click={() => {
            if (map && r.gps_coordinates) {
              map.setView(
                [r.gps_coordinates.latitude, r.gps_coordinates.longitude],
                16
              );
            }
          }}
        >
          <div class="card-header">
            <strong>{r.title}</strong>
            {#if r.rating}
              <div class="rating">
                {"★".repeat(Math.floor(r.rating))}{"☆".repeat(
                  5 - Math.floor(r.rating)
                )}
                {#if r.reviews}
                  <span class="reviews">({r.reviews})</span>
                {/if}
              </div>
            {/if}
          </div>

          {#if r.type}
            <p class="type">{r.type}</p>
          {/if}

          <p class="address">{r.address}</p>

          {#if r.hours}
            <p class="hours">⏰ {r.hours}</p>
          {/if}

          {#if r.phone_number}
            <p class="phone">📞 {r.phone_number}</p>
          {/if}

          {#if r.description}
            <p class="description">{r.description}</p>
          {/if}

          {#if r.website}
            <a href={r.website} target="_blank" class="website-link"
              >Visit Website →</a
            >
          {/if}
        </div>
      {/each}
    </div>
  </main>
</div>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 2rem;
    color: #333;
    margin-bottom: 1rem;
  }

  .search-box {
    display: flex;
    gap: 10px;
  }

  input {
    flex: 1;
    padding: 10px 15px;
    border: 2px solid #e1e1e1;
    border-radius: 8px;
    font-size: 1rem;
  }

  .search-btn {
    padding: 10px 20px;
    background: #4a90e2;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 100px;
  }

  .search-btn:hover {
    background: #357abd;
  }

  .search-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .loading {
    width: 20px;
    height: 20px;
    border: 3px solid #ffffff;
    border-top: 3px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  main {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 20px;
    height: calc(100vh - 200px);
    min-height: 500px;
  }

  .map {
    width: 100%;
    height: 100%;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .results {
    overflow-y: auto;
    padding-right: 10px;
  }

  .card {
    background: white;
    border: 1px solid #e1e1e1;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .card strong {
    display: block;
    font-size: 1.1rem;
    color: #333;
    margin-bottom: 5px;
  }

  .address {
    color: #666;
    margin: 5px 0;
    font-size: 0.9rem;
  }

  .phone {
    color: #4a90e2;
    margin: 5px 0 0;
    font-size: 0.9rem;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  :global(.custom-popup) {
    min-width: 200px;
  }

  :global(.popup-content h3) {
    margin: 0 0 8px;
    color: #333;
  }

  .card-header {
    margin-bottom: 10px;
  }

  .rating {
    color: #ffd700;
    font-size: 1.1rem;
    margin: 5px 0;
  }

  .reviews {
    color: #666;
    font-size: 0.9rem;
    margin-left: 5px;
  }

  .type {
    background: #f0f0f0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #666;
    display: inline-block;
    margin: 5px 0;
  }

  .hours {
    color: #666;
    margin: 5px 0;
    font-size: 0.9rem;
  }

  .description {
    color: #666;
    margin: 10px 0;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .website-link {
    display: inline-block;
    margin-top: 10px;
    color: #4a90e2;
    text-decoration: none;
    font-size: 0.9rem;
  }

  .website-link:hover {
    text-decoration: underline;
  }

  :global(.popup-content p) {
    margin: 5px 0;
    color: #666;
  }

  :global(.popup-content .rating) {
    color: #ffd700;
    margin: 5px 0;
  }

  :global(.popup-content .rating span) {
    color: #666;
    font-size: 0.9rem;
    margin-left: 5px;
  }

  :global(.popup-content .type) {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #666;
    display: inline-block;
    margin: 5px 0;
  }

  :global(.popup-content .website) {
    display: inline-block;
    margin-top: 8px;
    color: #4a90e2;
    text-decoration: none;
    font-size: 0.9rem;
  }

  :global(.popup-content .website:hover) {
    text-decoration: underline;
  }
</style>
