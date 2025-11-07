import { ArrowLeft, MapPin, Calendar, Users, Heart, Plus, Bell, Star, MessageSquare, Sparkles } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { useState } from 'react';
import qicoAvatar from 'figma:asset/df749756eb2f3e1f6a511fd7b1a552bd3aabda73.png';

interface TravelPageProps {
  onBack: () => void;
  onStartNewTrip: () => void;
  onViewTrip: (tripId: number) => void;
  onViewHistory: () => void;
  onViewPopularPlan: (planId: number) => void;
  onNotifications?: () => void;
}

interface TripCard {
  id: number;
  destination: string;
  country: string;
  duration: string;
  dates: string;
  price: string;
  image: string;
  travelers: number;
  category: string;
}

interface PublicTripPlan {
  id: number;
  author: string;
  authorAvatar: string;
  destination: string;
  duration: string;
  image: string;
  rating: number;
  reviewCount: number;
  tags: string[];
  description: string;
}

interface AISuggestedPlan {
  id: number;
  destination: string;
  duration: string;
  image: string;
  tags: string[];
  description: string;
  basedOn: string;
  confidence: number;
}

export function TravelPage({ onBack, onStartNewTrip, onViewTrip, onViewHistory, onViewPopularPlan, onNotifications }: TravelPageProps) {
  const [likedTrips, setLikedTrips] = useState<number[]>([]);
  const [hasTrips, setHasTrips] = useState(false); // Set to false to show Popular Plans and AI Suggested sections
  const [showAllAIPlans, setShowAllAIPlans] = useState(false);
  const [showAllPopularPlans, setShowAllPopularPlans] = useState(false);

  const trips: TripCard[] = [
    {
      id: 1,
      destination: 'Paris',
      country: 'France',
      duration: '5 days',
      dates: 'Nov 15 - Nov 20',
      price: '$1,299',
      image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
      travelers: 2,
      category: 'City Break'
    },
    {
      id: 2,
      destination: 'Maldives',
      country: 'Indian Ocean',
      duration: '7 days',
      dates: 'Dec 1 - Dec 8',
      price: '$2,499',
      image: 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80',
      travelers: 2,
      category: 'Beach Resort'
    },
    {
      id: 3,
      destination: 'Dubai',
      country: 'UAE',
      duration: '4 days',
      dates: 'Nov 22 - Nov 26',
      price: '$899',
      image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
      travelers: 4,
      category: 'City & Desert'
    },
    {
      id: 4,
      destination: 'Istanbul',
      country: 'Turkey',
      duration: '6 days',
      dates: 'Dec 10 - Dec 16',
      price: '$1,099',
      image: 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80',
      travelers: 2,
      category: 'Cultural'
    },
    {
      id: 5,
      destination: 'Bali',
      country: 'Indonesia',
      duration: '8 days',
      dates: 'Jan 5 - Jan 13',
      price: '$1,599',
      image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80',
      travelers: 2,
      category: 'Adventure'
    }
  ];

  const publicPlans: PublicTripPlan[] = [
    {
      id: 1,
      author: 'Sarah Chen',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
      destination: 'Tokyo Adventure',
      duration: '7 days',
      image: 'https://images.unsplash.com/photo-1623566713971-1f7ad1dc7bfb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0b2t5byUyMHNreWxpbmUlMjB0cmF2ZWx8ZW58MXx8fHwxNzYxODA0NjY1fDA&ixlib=rb-4.1.0&q=80&w=1080',
      rating: 4.8,
      reviewCount: 124,
      tags: ['Urban', 'Culture', 'Food'],
      description: 'Perfect blend of tradition and modernity'
    },
    {
      id: 2,
      author: 'Alex Turner',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
      destination: 'Santorini Escape',
      duration: '5 days',
      image: 'https://images.unsplash.com/photo-1612277288801-0d783ca59c42?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYW50b3JpbmklMjBncmVlY2UlMjB0cmF2ZWx8ZW58MXx8fHwxNzYxNzE0MDU5fDA&ixlib=rb-4.1.0&q=80&w=1080',
      rating: 4.9,
      reviewCount: 89,
      tags: ['Beach', 'Romantic', 'Luxury'],
      description: 'Stunning sunsets and white architecture'
    },
    {
      id: 3,
      author: 'Mike Johnson',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike',
      destination: 'Bali Getaway',
      duration: '10 days',
      image: 'https://images.unsplash.com/photo-1662950267280-0cdf5f7139b4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWxpJTIwYmVhY2glMjB0cmF2ZWx8ZW58MXx8fHwxNzYxODA0NjY1fDA&ixlib=rb-4.1.0&q=80&w=1080',
      rating: 4.7,
      reviewCount: 156,
      tags: ['Beach', 'Adventure', 'Wellness'],
      description: 'Temples, beaches, and spiritual vibes'
    },
    {
      id: 4,
      author: 'Emma Wilson',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma',
      destination: 'Swiss Alps Trek',
      duration: '6 days',
      image: 'https://images.unsplash.com/photo-1723925308619-efc04df8b081?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzd2lzcyUyMGFscHMlMjBtb3VudGFpbnN8ZW58MXx8fHwxNzYxNzY1NjQzfDA&ixlib=rb-4.1.0&q=80&w=1080',
      rating: 5.0,
      reviewCount: 73,
      tags: ['Mountain', 'Adventure', 'Nature'],
      description: 'Breathtaking mountain landscapes'
    }
  ];

  const aiSuggestedPlans: AISuggestedPlan[] = [
    {
      id: 101,
      destination: 'Morocco Desert Experience',
      duration: '6 days',
      image: 'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=800&q=80',
      tags: ['Adventure', 'Culture', 'Desert'],
      description: 'Explore vibrant markets and stunning Sahara landscapes',
      basedOn: 'Similar to your Dubai trip',
      confidence: 95
    },
    {
      id: 102,
      destination: 'Barcelona City & Beach',
      duration: '5 days',
      image: 'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=800&q=80',
      tags: ['City', 'Beach', 'Culture'],
      description: 'Perfect mix of urban exploration and beach relaxation',
      basedOn: 'Matches your travel style',
      confidence: 92
    },
    {
      id: 103,
      destination: 'Iceland Northern Lights',
      duration: '7 days',
      image: 'https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=800&q=80',
      tags: ['Nature', 'Adventure', 'Unique'],
      description: 'Chase auroras and explore dramatic landscapes',
      basedOn: 'New adventure for you',
      confidence: 88
    },
    {
      id: 104,
      destination: 'Seoul Modern Culture',
      duration: '6 days',
      image: 'https://images.unsplash.com/photo-1551740636-8de2e4f9b4e0?w=800&q=80',
      tags: ['Urban', 'Food', 'Shopping'],
      description: 'K-culture, street food, and futuristic cityscapes',
      basedOn: 'Popular with similar travelers',
      confidence: 90
    },
    {
      id: 105,
      destination: 'New Zealand Adventure',
      duration: '10 days',
      image: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&q=80',
      tags: ['Nature', 'Adventure', 'Scenic'],
      description: 'Epic landscapes and outdoor activities',
      basedOn: 'Trending destination',
      confidence: 87
    }
  ];

  const toggleLike = (tripId: number) => {
    setLikedTrips(prev => 
      prev.includes(tripId) 
        ? prev.filter(id => id !== tripId)
        : [...prev, tripId]
    );
  };

  // Empty state - no trips yet (shows Popular Plans and AI Suggested sections)
  if (!hasTrips) {
    return (
      <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
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
              <h1 className="text-xl font-semibold">Travel</h1>
              <p className="text-sm text-gray-500">Plan your next adventure</p>
            </div>
            <button 
              onClick={() => onNotifications?.()}
              className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
        </div>

        {/* Empty State - Only show "No trips planned yet" when there are no trips */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
          <div className="w-32 h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-16 h-16 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold mb-3 text-center">No trips planned yet</h2>
          <p className="text-gray-600 text-center mb-8 max-w-sm">
            Let our AI assistant help you plan the perfect trip tailored to your preferences
          </p>
          <div className="flex flex-col gap-3 w-full max-w-xs">
            <Button
              onClick={onStartNewTrip}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-6 h-auto w-full"
            >
              <Plus className="w-5 h-5 mr-2" />
              Plan New Trip with AI
            </Button>
            <Button
              onClick={onViewHistory}
              variant="outline"
              className="px-8 py-6 h-auto w-full border-2"
            >
              View My Trips
            </Button>
          </div>
        </div>

        {/* Popular Plans Section */}
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Popular Plans</h3>
            <button 
              onClick={() => setShowAllPopularPlans(!showAllPopularPlans)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAllPopularPlans ? 'Show less' : 'Show more'}
            </button>
          </div>
          <div className="space-y-3">
            {publicPlans.slice(0, showAllPopularPlans ? publicPlans.length : 3).map((plan) => (
              <Card 
                key={plan.id} 
                onClick={() => onViewPopularPlan(plan.id)}
                className="overflow-hidden border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex gap-3 p-3">
                  <div className="relative w-24 h-24 rounded-lg overflow-hidden flex-shrink-0">
                    <ImageWithFallback 
                      src={plan.image}
                      alt={plan.destination}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-semibold text-sm truncate">{plan.destination}</h4>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleLike(plan.id);
                        }}
                      >
                        <Heart 
                          className={`w-4 h-4 flex-shrink-0 ${likedTrips.includes(plan.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`}
                        />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <ImageWithFallback 
                        src={plan.authorAvatar}
                        alt={plan.author}
                        className="w-5 h-5 rounded-full"
                      />
                      <span className="text-xs text-gray-600">{plan.author}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <span className="text-xs font-semibold">{plan.rating}</span>
                        <span className="text-xs text-gray-500">({plan.reviewCount})</span>
                      </div>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-600">{plan.duration}</span>
                    </div>
                    <div className="flex gap-1 flex-wrap">
                      {plan.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs px-2 py-0 h-5">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* AI Suggested Plans Section */}
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <img src={qicoAvatar} alt="Qico AI" className="w-6 h-6 rounded-full" />
              <h3 className="font-semibold">AI Suggested for You</h3>
            </div>
            <button 
              onClick={() => setShowAllAIPlans(!showAllAIPlans)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAllAIPlans ? 'Show less' : 'Show more'}
            </button>
          </div>
          <div className="space-y-3">
            {aiSuggestedPlans.slice(0, showAllAIPlans ? 5 : 3).map((plan) => (
              <Card 
                key={plan.id} 
                onClick={() => onViewPopularPlan(plan.id)}
                className="overflow-hidden border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer bg-gradient-to-br from-blue-50/50 to-purple-50/50"
              >
                <div className="flex gap-3 p-3">
                  <div className="relative w-24 h-24 rounded-lg overflow-hidden flex-shrink-0">
                    <ImageWithFallback 
                      src={plan.image}
                      alt={plan.destination}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute top-1 right-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full p-1">
                      <Sparkles className="w-3 h-3 text-white" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-semibold text-sm truncate">{plan.destination}</h4>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleLike(plan.id);
                        }}
                      >
                        <Heart 
                          className={`w-4 h-4 flex-shrink-0 ${likedTrips.includes(plan.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`}
                        />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="text-xs px-2 py-0 h-5 bg-gradient-to-r from-blue-500 to-purple-600">
                        {plan.confidence}% match
                      </Badge>
                      <span className="text-xs text-gray-600">{plan.duration}</span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2 line-clamp-1">{plan.basedOn}</p>
                    <div className="flex gap-1 flex-wrap">
                      {plan.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs px-2 py-0 h-5">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Has trips - show list
  return (
    <div className="max-w-md mx-auto min-h-screen bg-white pb-6">
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
            <h1 className="text-xl font-semibold">My Trips</h1>
            <p className="text-sm text-gray-500">Your travel history</p>
          </div>
          <Button
            onClick={onStartNewTrip}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-1" />
            New Trip
          </Button>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="px-6 py-4 flex gap-2 overflow-x-auto no-scrollbar">
        <Badge variant="default" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 whitespace-nowrap cursor-pointer">
          All Trips
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Beach
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          City
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Adventure
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Cultural
        </Badge>
      </div>

      {/* Trip Cards */}
      <div className="px-6 space-y-4">
        {trips.map((trip) => (
          <Card 
            key={trip.id} 
            className="overflow-hidden border-0 shadow-md hover:shadow-xl transition-shadow cursor-pointer"
            onClick={() => onViewTrip(trip.id)}
          >
            <div className="relative h-48">
              <ImageWithFallback 
                src={trip.image}
                alt={trip.destination}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3">
                <Badge className="bg-white/90 text-gray-800 hover:bg-white">
                  {trip.category}
                </Badge>
              </div>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  toggleLike(trip.id);
                }}
                className="absolute top-3 right-3 w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center hover:bg-white transition-colors"
              >
                <Heart 
                  className={`w-5 h-5 ${likedTrips.includes(trip.id) ? 'fill-red-500 text-red-500' : 'text-gray-700'}`}
                />
              </button>
            </div>
            <div className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-lg">{trip.destination}</h3>
                  <div className="flex items-center gap-1 text-gray-500 text-sm">
                    <MapPin className="w-4 h-4" />
                    <span>{trip.country}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-indigo-600 font-semibold text-lg">{trip.price}</p>
                  <p className="text-gray-400 text-xs">per person</p>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600 mt-3">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>{trip.duration}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{trip.travelers} travelers</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t">
                <p className="text-sm text-gray-500">{trip.dates}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}