/**
 * API utility functions for communication with the backend
 */

const API_BASE_URL = 'http://localhost:8001/api/v1';

// Types
export interface ApiError {
  detail: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user_id: string;
  username: string;
}

export interface TripResponse {
  id: string;
  user_id: string;
  from_city: string;
  to_city: string;
  start_date: string;
  end_date: string;
  transport: string;
  adults: number;
  children: number;
  budget_min: number | null;
  budget_max: number | null;
  entertainment_tags: string[] | null;
  notes: string | null;
  status: string;
  timezone: string | null;
  ics_token: string;
  created_at: string;
  updated_at: string | null;
  selected_flight?: any;
  selected_hotel?: any;
  selected_entertainments?: any[];
}

export interface TripListResponse {
  trips: TripResponse[];
  total: number;
  page: number;
  per_page: number;
}

// Storage utilities
export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const setAccessToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

export const clearAccessToken = (): void => {
  localStorage.removeItem('access_token');
};

export const getTokenExpiry = (): string | null => {
  return localStorage.getItem('token_expires_at');
};

export const setTokenExpiry = (expiry: string): void => {
  localStorage.setItem('token_expires_at', expiry);
};

// Generic fetch wrapper with auth
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: 'Unknown error occurred',
    }));
    console.error('API Error:', response.status, errorData);
    if (response.status === 422 && Array.isArray(errorData.detail)) {
      console.error('Validation errors:', JSON.stringify(errorData.detail, null, 2));
    }
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  register: async (username: string): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
    setAccessToken(response.access_token);
    setTokenExpiry(response.expires_at);
    return response;
  },

  login: async (username: string): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
    setAccessToken(response.access_token);
    setTokenExpiry(response.expires_at);
    return response;
  },

  logout: async (): Promise<void> => {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAccessToken();
      localStorage.removeItem('token_expires_at');
    }
  },

  getCurrentUser: async () => {
    return apiRequest('/auth/me');
  },
};

// Trips API
export const tripsApi = {
  createTrip: async (tripData: any): Promise<TripResponse> => {
    return apiRequest<TripResponse>('/trips', {
      method: 'POST',
      body: JSON.stringify(tripData),
    });
  },

  getTrips: async (page = 1, perPage = 20): Promise<TripListResponse> => {
    return apiRequest<TripListResponse>(
      `/trips?page=${page}&per_page=${perPage}`
    );
  },

  getTrip: async (tripId: string): Promise<TripResponse> => {
    return apiRequest<TripResponse>(`/trips/${tripId}`);
  },

  updateTrip: async (
    tripId: string,
    tripData: any
  ): Promise<TripResponse> => {
    return apiRequest<TripResponse>(`/trips/${tripId}`, {
      method: 'PATCH',
      body: JSON.stringify(tripData),
    });
  },

  deleteTrip: async (tripId: string): Promise<void> => {
    await apiRequest(`/trips/${tripId}`, { method: 'DELETE' });
  },

  finalizeTrip: async (tripId: string): Promise<TripResponse> => {
    return apiRequest<TripResponse>(`/trips/${tripId}/finalize`, {
      method: 'POST',
    });
  },

  getTripPlan: async (tripId: string) => {
    return apiRequest(`/trips/${tripId}/plan`);
  },

  getTripChecklist: async (tripId: string) => {
    return apiRequest(`/trips/${tripId}/checklist`);
  },
};

// Flights API
export const flightsApi = {
  rankFlights: async (rankingData: any) => {
    return apiRequest('/flights/rank', {
      method: 'POST',
      body: JSON.stringify(rankingData),
    });
  },

  selectFlight: async (flightData: any) => {
    return apiRequest('/flights/select', {
      method: 'POST',
      body: JSON.stringify(flightData),
    });
  },
};

// Hotels API
export const hotelsApi = {
  searchHotels: async (query: any) => {
    const params = new URLSearchParams(query).toString();
    return apiRequest(`/hotels/search?${params}`);
  },

  rankHotels: async (rankingData: any) => {
    return apiRequest('/hotels/rank', {
      method: 'POST',
      body: JSON.stringify(rankingData),
    });
  },

  selectHotel: async (hotelData: any) => {
    return apiRequest('/hotels/select', {
      method: 'POST',
      body: JSON.stringify(hotelData),
    });
  },
};

// Entertainment API
export const entertainmentApi = {
  searchVenues: async (searchData: any) => {
    return apiRequest('/entertainment/search', {
      method: 'POST',
      body: JSON.stringify(searchData),
    });
  },

  rankVenues: async (rankingData: any) => {
    return apiRequest('/entertainment/rank', {
      method: 'POST',
      body: JSON.stringify(rankingData),
    });
  },

  selectVenues: async (selections: any) => {
    return apiRequest('/entertainment/select', {
      method: 'POST',
      body: JSON.stringify(selections),
    });
  },

  getSelections: async (tripId: string) => {
    return apiRequest(`/entertainment/${tripId}/selections`);
  },
};

// Culture API
export const cultureApi = {
  getGuide: async (destination: string) => {
    return apiRequest('/culture-guide', {
      method: 'POST',
      body: JSON.stringify({ destination, language: 'en' }),
    });
  },
};

