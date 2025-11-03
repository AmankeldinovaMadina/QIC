import { ArrowLeft, Calendar, Plane, Hotel, MapPin, DollarSign, Check, Bell } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface TripPlannerPageProps {
  onBack: () => void;
  tripData: any;
  onConfirm: (selectedOptions: any) => void;
  onNotifications: () => void;
}

export function TripPlannerPage({ onBack, tripData, onConfirm, onNotifications }: TripPlannerPageProps) {
  const [selectedFlight, setSelectedFlight] = useState<number | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<number | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<number[]>([]);

  const flightOptions = [
    { id: 1, airline: 'Emirates', price: '$450', time: '10:30 AM - 2:45 PM', duration: '4h 15m' },
    { id: 2, airline: 'Qatar Airways', price: '$520', time: '2:15 PM - 6:30 PM', duration: '4h 15m' },
    { id: 3, airline: 'FlyDubai', price: '$380', time: '6:00 AM - 10:15 AM', duration: '4h 15m' }
  ];

  const hotelOptions = [
    { id: 1, name: 'Luxury Resort & Spa', price: '$250/night', rating: 4.8, amenities: ['Pool', 'Spa', 'Restaurant'] },
    { id: 2, name: 'City Center Hotel', price: '$150/night', rating: 4.5, amenities: ['Gym', 'WiFi', 'Breakfast'] },
    { id: 3, name: 'Boutique Hotel', price: '$180/night', rating: 4.7, amenities: ['Rooftop', 'Bar', 'WiFi'] }
  ];

  const activityOptions = [
    { id: 1, name: 'Desert Safari', price: '$80', duration: '6 hours' },
    { id: 2, name: 'City Tour', price: '$50', duration: '4 hours' },
    { id: 3, name: 'Burj Khalifa Visit', price: '$60', duration: '2 hours' },
    { id: 4, name: 'Marina Dinner Cruise', price: '$100', duration: '3 hours' }
  ];

  const toggleActivity = (id: number) => {
    setSelectedActivities(prev =>
      prev.includes(id) ? prev.filter(actId => actId !== id) : [...prev, id]
    );
  };

  const handleConfirm = () => {
    onConfirm({
      flight: flightOptions.find(f => f.id === selectedFlight),
      hotel: hotelOptions.find(h => h.id === selectedHotel),
      activities: activityOptions.filter(a => selectedActivities.includes(a.id))
    });
  };

  const isComplete = selectedFlight !== null && selectedHotel !== null && selectedActivities.length > 0;

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white pb-20">
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
            <h1 className="text-xl font-semibold">Your Trip Plan</h1>
            <p className="text-sm text-gray-500">Select your preferences</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Trip Summary */}
      <div className="px-6 py-4 bg-gradient-to-br from-blue-50 to-purple-50">
        <Card className="p-4 border-0 shadow-md">
          <div className="flex items-center gap-3 mb-3">
            <MapPin className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Destination</p>
              <p className="font-semibold">{tripData.destination || 'Dubai'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Dates</p>
              <p className="font-semibold">{tripData.dates || 'Dec 1-8, 2025'}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Flight Options */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-2 mb-4">
          <Plane className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold">Select Flight</h2>
        </div>
        <div className="space-y-3">
          {flightOptions.map((flight) => (
            <Card
              key={flight.id}
              onClick={() => setSelectedFlight(flight.id)}
              className={`p-4 cursor-pointer transition-all ${
                selectedFlight === flight.id
                  ? 'border-2 border-blue-600 bg-blue-50'
                  : 'border hover:border-blue-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-semibold">{flight.airline}</p>
                    {selectedFlight === flight.id && (
                      <Check className="w-4 h-4 text-blue-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{flight.time}</p>
                  <p className="text-xs text-gray-500 mt-1">{flight.duration}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-blue-600">{flight.price}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Hotel Options */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-2 mb-4">
          <Hotel className="w-5 h-5 text-purple-600" />
          <h2 className="font-semibold">Select Hotel</h2>
        </div>
        <div className="space-y-3">
          {hotelOptions.map((hotel) => (
            <Card
              key={hotel.id}
              onClick={() => setSelectedHotel(hotel.id)}
              className={`p-4 cursor-pointer transition-all ${
                selectedHotel === hotel.id
                  ? 'border-2 border-purple-600 bg-purple-50'
                  : 'border hover:border-purple-200'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-semibold">{hotel.name}</p>
                    {selectedHotel === hotel.id && (
                      <Check className="w-4 h-4 text-purple-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600">⭐ {hotel.rating}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-purple-600">{hotel.price}</p>
                </div>
              </div>
              <div className="flex gap-2 mt-2">
                {hotel.amenities.map((amenity, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs">
                    {amenity}
                  </Badge>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Activity Options */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="w-5 h-5 text-green-600" />
          <h2 className="font-semibold">Select Activities</h2>
          <span className="text-sm text-gray-500">(Choose multiple)</span>
        </div>
        <div className="space-y-3">
          {activityOptions.map((activity) => (
            <Card
              key={activity.id}
              onClick={() => toggleActivity(activity.id)}
              className={`p-4 cursor-pointer transition-all ${
                selectedActivities.includes(activity.id)
                  ? 'border-2 border-green-600 bg-green-50'
                  : 'border hover:border-green-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-semibold">{activity.name}</p>
                    {selectedActivities.includes(activity.id) && (
                      <Check className="w-4 h-4 text-green-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{activity.duration}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-green-600">{activity.price}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Confirm Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
        <div className="max-w-md mx-auto">
          <Button
            onClick={handleConfirm}
            disabled={!isComplete}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 h-12"
          >
            {isComplete ? 'Create My Trip Plan' : 'Please select all options'}
          </Button>
        </div>
      </div>
    </div>
  );
}