import { SERPAPI_KEY } from '$env/static/private';
import { json } from '@sveltejs/kit';
import axios from 'axios';

export async function GET({ url }) {
    console.log('Loaded SERPAPI_KEY:', SERPAPI_KEY?.slice(0, 6) + '...');
  const query = url.searchParams.get('q');
  const apiKey = SERPAPI_KEY; // ✅ use server env var

  try {
    const res = await axios.get('https://serpapi.com/search.json', {
      params: {
        engine: 'google_maps',
        type: 'search',
        q: query,
        api_key: apiKey
      }
    });

    return json(res.data);
  } catch (err) {
    console.error('SerpApi error:', err.response?.data || err.message);
    return json({ error: err.message }, { status: 500 });
  }
}
