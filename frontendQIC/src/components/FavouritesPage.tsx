import { ArrowLeft, Heart, Star, MapPin, Bell, Trash2 } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Button } from './ui/button';

interface FavouritesPageProps {
  onBack: () => void;
  onViewPlan: (planId: number) => void;
  favouritePlans: number[];
  onRemoveFavourite: (planId: number) => void;
  onNotifications: () => void;
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

export function FavouritesPage({ onBack, onViewPlan, favouritePlans, onRemoveFavourite, onNotifications }: FavouritesPageProps) {
  // Mock data - should match the popular plans
  const allPlans: PublicTripPlan[] = [
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

  const favourites = allPlans.filter(plan => favouritePlans.includes(plan.id));

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-purple-50 to-white">
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
            <h1 className="text-xl font-semibold">Favourite Trips</h1>
            <p className="text-sm text-gray-500">{favourites.length} saved plans</p>
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

      {/* Content */}
      <div className="px-6 py-6">
        {favourites.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-24 h-24 bg-gradient-to-br from-red-100 to-pink-100 rounded-full flex items-center justify-center mb-6">
              <Heart className="w-12 h-12 text-red-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2 text-center">No favourites yet</h2>
            <p className="text-gray-600 text-center max-w-sm mb-6">
              Start adding trip plans to your favourites to see them here
            </p>
            <Button
              onClick={onBack}
              variant="outline"
              className="border-2"
            >
              Explore Plans
            </Button>
          </div>
        ) : (
          /* Favourites List */
          <div className="space-y-4">
            {favourites.map((plan) => (
              <Card 
                key={plan.id} 
                className="overflow-hidden border-0 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex gap-3 p-3">
                  <div 
                    className="relative w-28 h-28 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer"
                    onClick={() => onViewPlan(plan.id)}
                  >
                    <ImageWithFallback 
                      src={plan.image}
                      alt={plan.destination}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 
                        className="font-semibold text-sm truncate cursor-pointer hover:text-blue-600"
                        onClick={() => onViewPlan(plan.id)}
                      >
                        {plan.destination}
                      </h4>
                      <button
                        onClick={() => onRemoveFavourite(plan.id)}
                        className="flex-shrink-0"
                      >
                        <Heart className="w-5 h-5 fill-red-500 text-red-500 hover:scale-110 transition-transform" />
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
        )}
      </div>
    </div>
  );
}
