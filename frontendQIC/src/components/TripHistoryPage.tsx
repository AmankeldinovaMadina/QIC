import { ArrowLeft, Plus, Bell, Share2, Upload } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { tripsApi, TripResponse } from '../utils/api';

interface TripHistoryPageProps {
  onBack: () => void;
  onViewTrip: (tripId: string) => void;
  onCreateNewTrip: () => void;
  onNotifications: () => void;
  onTripSummary: (tripId: string) => void;
}

interface Trip {
  id: string;
  destination: string;
  dates: string;
  progress: number;
  isPublished: boolean;
}

export function TripHistoryPage({ onBack, onViewTrip, onCreateNewTrip, onNotifications, onTripSummary }: TripHistoryPageProps) {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      const response = await tripsApi.getTrips();
      const formattedTrips: Trip[] = response.trips.map((trip: TripResponse) => {
        const startDate = new Date(trip.start_date);
        const endDate = new Date(trip.end_date);
        const dates = `${startDate.getDate()}.${startDate.getMonth() + 1}-${endDate.getDate()}.${endDate.getMonth() + 1}`;
        
        // Calculate progress based on selected items (mock for now)
        let progress = 0;
        if (trip.selected_flight) progress += 25;
        if (trip.selected_hotel) progress += 25;
        if (trip.selected_entertainments && trip.selected_entertainments.length > 0) progress += 25;
        if (trip.status === 'planned' || trip.status === 'active' || trip.status === 'completed') progress += 25;
        
        return {
          id: trip.id,
          destination: `Trip to ${trip.to_city}`,
          dates,
          progress,
          isPublished: false // Not implemented in backend yet
        };
      });
      setTrips(formattedTrips);
    } catch (error) {
      console.error('Failed to fetch trips:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-semibold">Planned Trips</h1>
          </div>
          <button 
            onClick={onCreateNewTrip}
            className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center hover:from-blue-700 hover:to-purple-700 transition-colors"
          >
            <Plus className="w-5 h-5 text-white" />
          </button>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Trip List */}
      <div className="px-6 py-6 space-y-4">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading trips...</p>
          </div>
        ) : trips.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">No trips yet. Create your first trip!</p>
            <Button onClick={onCreateNewTrip} className="bg-gradient-to-r from-blue-600 to-purple-600">
              Create New Trip
            </Button>
          </div>
        ) : (
          trips.map((trip) => (
          <Card 
            key={trip.id}
            className="p-4 cursor-pointer hover:shadow-md transition-shadow border-2"
            onClick={() => onViewTrip(trip.id)}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold">{trip.destination}</h3>
                <p className="text-sm text-gray-600">{trip.dates}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Share logic
                  }}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Share2 className="w-4 h-4 text-gray-600" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Publish logic
                  }}
                  className={`p-2 rounded-lg transition-colors ${
                    trip.isPublished
                      ? 'bg-green-50 hover:bg-green-100'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <Upload className={`w-4 h-4 ${trip.isPublished ? 'text-green-600' : 'text-gray-600'}`} />
                </button>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Checklist Progress</span>
                <span className="text-xs font-semibold text-gray-700">{trip.progress}%</span>
              </div>
              <div className="relative">
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-400 to-green-500 rounded-full transition-all duration-300"
                    style={{ width: `${trip.progress}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Trip Summary Button - Always Available */}
            <Button
              onClick={(e) => {
                e.stopPropagation();
                onTripSummary(trip.id);
              }}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Post Summary Collage
            </Button>
          </Card>
        ))
        )}
      </div>
    </div>
  );
}
