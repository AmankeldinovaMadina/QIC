import { ArrowLeft, Search, Navigation, MapPin, Star } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';

interface MapPageProps {
  onBack: () => void;
}

interface Place {
  id: number;
  name: string;
  category: string;
  distance: string;
  rating: number;
  address: string;
}

export function MapPage({ onBack }: MapPageProps) {
  const nearbyPlaces: Place[] = [
    {
      id: 1,
      name: 'Grand Mosque',
      category: 'Religious',
      distance: '0.5 km',
      rating: 4.8,
      address: 'Al Corniche Street'
    },
    {
      id: 2,
      name: 'City Mall',
      category: 'Shopping',
      distance: '1.2 km',
      rating: 4.5,
      address: 'Downtown District'
    },
    {
      id: 3,
      name: 'Heritage Museum',
      category: 'Culture',
      distance: '2.3 km',
      rating: 4.7,
      address: 'Museum Square'
    },
    {
      id: 4,
      name: 'Seaside Restaurant',
      category: 'Dining',
      distance: '0.8 km',
      rating: 4.6,
      address: 'Marina Walk'
    }
  ];

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-semibold">Map</h1>
            <p className="text-sm text-gray-500">Find places nearby</p>
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <Input 
            placeholder="Search locations..."
            className="pl-10"
          />
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="relative h-64 bg-gradient-to-br from-blue-100 to-green-100 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-12 h-12 text-green-600 mx-auto mb-2" />
            <p className="text-gray-600">Interactive map view</p>
          </div>
        </div>
        <button className="absolute bottom-4 right-4 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors">
          <Navigation className="w-5 h-5 text-blue-600" />
        </button>
      </div>

      {/* Category Filters */}
      <div className="px-6 py-4 flex gap-2 overflow-x-auto no-scrollbar border-b">
        <Badge variant="default" className="px-4 py-2 bg-green-600 hover:bg-green-700 whitespace-nowrap cursor-pointer">
          All
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Religious
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Shopping
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Dining
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Culture
        </Badge>
      </div>

      {/* Nearby Places */}
      <div className="px-6 py-4">
        <h2 className="font-semibold mb-4">Nearby Places</h2>
        <div className="space-y-3">
          {nearbyPlaces.map((place) => (
            <Card key={place.id} className="p-4 border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">{place.name}</h3>
                    <Badge variant="outline" className="text-xs">
                      {place.category}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">{place.address}</p>
                  <div className="flex items-center gap-3 text-sm">
                    <div className="flex items-center gap-1 text-yellow-600">
                      <Star className="w-4 h-4 fill-current" />
                      <span className="font-medium">{place.rating}</span>
                    </div>
                    <span className="text-gray-500">{place.distance}</span>
                  </div>
                </div>
                <button className="ml-3 px-3 py-1 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors text-sm">
                  Directions
                </button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
