import { ArrowLeft, Star, MapPin, Calendar, Users, Heart, Share2, Bell, Clock, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Avatar } from './ui/avatar';
import qicoAvatar from 'figma:asset/df749756eb2f3e1f6a511fd7b1a552bd3aabda73.png';

interface PopularPlanDetailPageProps {
  onBack: () => void;
  planId: number;
}

export function PopularPlanDetailPage({ onBack, planId }: PopularPlanDetailPageProps) {
  const [isLiked, setIsLiked] = useState(false);
  
  // Check if this is an AI-generated plan
  const isAIPlan = planId >= 101;

  // Mock data - in real app this would come from props or API
  const aiPlansData: { [key: number]: any } = {
    101: {
      id: 101,
      author: 'Qico AI',
      authorAvatar: qicoAvatar,
      destination: 'Morocco Desert Experience',
      country: 'Morocco',
      duration: '6 days',
      image: 'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=800&q=80',
      rating: 4.9,
      reviewCount: 0,
      tags: ['Adventure', 'Culture', 'Desert'],
      description: 'Immerse yourself in Morocco\'s vibrant culture and stunning landscapes. This AI-curated journey takes you through colorful markets, ancient medinas, and the breathtaking Sahara Desert. Based on your preference for diverse cultural experiences similar to your Dubai trip.',
      price: '$1,450',
      travelers: 2,
      dates: 'Best: Mar-May, Sep-Nov',
      basedOn: 'Similar to your Dubai trip',
      confidence: 95,
      itinerary: [
        {
          day: 1,
          title: 'Arrival in Marrakech',
          activities: [
            { time: '15:00', activity: 'Hotel check-in in Medina', icon: '🏨' },
            { time: '17:00', activity: 'Explore Jemaa el-Fnaa square', icon: '🎭' },
            { time: '19:30', activity: 'Traditional Moroccan dinner', icon: '🍲' },
            { time: '21:00', activity: 'Evening market walk', icon: '🌙' }
          ]
        },
        {
          day: 2,
          title: 'Marrakech Highlights',
          activities: [
            { time: '09:00', activity: 'Visit Bahia Palace', icon: '🏛️' },
            { time: '11:00', activity: 'Explore Majorelle Garden', icon: '🌿' },
            { time: '13:00', activity: 'Lunch in traditional riad', icon: '🍽️' },
            { time: '15:00', activity: 'Souk shopping experience', icon: '🛍️' },
            { time: '18:00', activity: 'Sunset at Koutoubia Mosque', icon: '🕌' }
          ]
        },
        {
          day: 3,
          title: 'Journey to Sahara',
          activities: [
            { time: '08:00', activity: 'Depart for desert via Atlas Mountains', icon: '🚗' },
            { time: '12:00', activity: 'Lunch in Ouarzazate', icon: '🍴' },
            { time: '16:00', activity: 'Arrive at desert camp', icon: '⛺' },
            { time: '18:00', activity: 'Camel trek at sunset', icon: '🐪' },
            { time: '20:00', activity: 'Berber dinner under stars', icon: '✨' }
          ]
        },
        {
          day: 4,
          title: 'Sahara Desert Experience',
          activities: [
            { time: '06:00', activity: 'Sunrise over the dunes', icon: '🌅' },
            { time: '09:00', activity: 'Desert activities & exploration', icon: '🏜️' },
            { time: '13:00', activity: 'Traditional desert lunch', icon: '🥘' },
            { time: '15:00', activity: 'Return journey begins', icon: '🚙' },
            { time: '19:00', activity: 'Overnight in Dades Valley', icon: '🏨' }
          ]
        },
        {
          day: 5,
          title: 'Back to Marrakech',
          activities: [
            { time: '09:00', activity: 'Visit Ait Benhaddou kasbah', icon: '🏰' },
            { time: '12:00', activity: 'Lunch en route', icon: '🍜' },
            { time: '18:00', activity: 'Arrive in Marrakech', icon: '🏙️' },
            { time: '20:00', activity: 'Farewell dinner at rooftop restaurant', icon: '🌃' }
          ]
        },
        {
          day: 6,
          title: 'Departure',
          activities: [
            { time: '09:00', activity: 'Last-minute souvenir shopping', icon: '🎁' },
            { time: '11:00', activity: 'Relax at hotel spa', icon: '💆' },
            { time: '14:00', activity: 'Check-out and transfer', icon: '✈️' }
          ]
        }
      ],
      reviews: []
    },
    102: {
      id: 102,
      author: 'Qico AI',
      authorAvatar: qicoAvatar,
      destination: 'Barcelona City & Beach',
      country: 'Spain',
      duration: '5 days',
      image: 'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=800&q=80',
      rating: 4.8,
      reviewCount: 0,
      tags: ['City', 'Beach', 'Culture'],
      description: 'Experience the perfect blend of urban culture and Mediterranean relaxation. This AI-designed itinerary combines Gaudí\'s masterpieces, vibrant neighborhoods, delicious tapas, and beach time. Curated based on your travel preferences.',
      price: '$1,250',
      travelers: 2,
      dates: 'Best: Apr-Jun, Sep-Oct',
      basedOn: 'Matches your travel style',
      confidence: 92,
      itinerary: [
        {
          day: 1,
          title: 'Gothic Quarter & Ramblas',
          activities: [
            { time: '14:00', activity: 'Check-in at hotel', icon: '🏨' },
            { time: '16:00', activity: 'Walk La Rambla', icon: '🚶' },
            { time: '18:00', activity: 'Explore Gothic Quarter', icon: '🏛️' },
            { time: '20:00', activity: 'Tapas dinner', icon: '🍤' }
          ]
        },
        {
          day: 2,
          title: 'Gaudí Masterpieces',
          activities: [
            { time: '09:00', activity: 'Visit Sagrada Familia', icon: '⛪' },
            { time: '12:00', activity: 'Lunch in Eixample', icon: '🍽️' },
            { time: '14:00', activity: 'Park Güell exploration', icon: '🎨' },
            { time: '17:00', activity: 'Casa Batlló visit', icon: '🏘️' },
            { time: '19:00', activity: 'Passeig de Gràcia stroll', icon: '🛍️' }
          ]
        },
        {
          day: 3,
          title: 'Beach Day',
          activities: [
            { time: '10:00', activity: 'Barceloneta Beach', icon: '🏖️' },
            { time: '13:00', activity: 'Seafood lunch by the beach', icon: '🦞' },
            { time: '15:00', activity: 'Beach activities & relaxation', icon: '☀️' },
            { time: '18:00', activity: 'Olympic Port sunset', icon: '🌅' },
            { time: '20:00', activity: 'Dinner in El Born', icon: '🍷' }
          ]
        },
        {
          day: 4,
          title: 'Montjuïc & Markets',
          activities: [
            { time: '09:00', activity: 'Cable car to Montjuïc', icon: '🚡' },
            { time: '11:00', activity: 'Visit Montjuïc Castle', icon: '🏰' },
            { time: '13:00', activity: 'Lunch at Boqueria Market', icon: '🥘' },
            { time: '15:00', activity: 'Shopping & exploring El Born', icon: '🛍️' },
            { time: '19:00', activity: 'Magic Fountain show', icon: '⛲' }
          ]
        },
        {
          day: 5,
          title: 'Last Day & Departure',
          activities: [
            { time: '09:00', activity: 'Morning at Ciutadella Park', icon: '🌳' },
            { time: '11:00', activity: 'Final shopping & souvenirs', icon: '🎁' },
            { time: '13:00', activity: 'Farewell paella lunch', icon: '🥘' },
            { time: '15:00', activity: 'Transfer to airport', icon: '✈️' }
          ]
        }
      ],
      reviews: []
    },
    103: {
      id: 103,
      author: 'Qico AI',
      authorAvatar: qicoAvatar,
      destination: 'Iceland Northern Lights',
      country: 'Iceland',
      duration: '7 days',
      image: 'https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=800&q=80',
      rating: 4.9,
      reviewCount: 0,
      tags: ['Nature', 'Adventure', 'Unique'],
      description: 'Chase the magical Northern Lights while exploring Iceland\'s dramatic landscapes. This AI-planned adventure includes glaciers, waterfalls, geothermal spas, and volcanic terrain. Perfect for those seeking unique natural wonders.',
      price: '$2,100',
      travelers: 2,
      dates: 'Best: Sep-Mar (for Northern Lights)',
      basedOn: 'New adventure for you',
      confidence: 88,
      itinerary: [
        {
          day: 1,
          title: 'Arrival & Reykjavik',
          activities: [
            { time: '12:00', activity: 'Arrive in Reykjavik', icon: '✈️' },
            { time: '14:00', activity: 'Check-in and city orientation', icon: '🏨' },
            { time: '16:00', activity: 'Explore downtown Reykjavik', icon: '🏙️' },
            { time: '19:00', activity: 'Icelandic dinner', icon: '🍽️' },
            { time: '22:00', activity: 'Northern Lights hunt', icon: '✨' }
          ]
        }
      ],
      reviews: []
    }
  };
  
  const plan = isAIPlan && aiPlansData[planId] ? aiPlansData[planId] : {
    id: planId,
    author: 'Sarah Chen',
    authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
    destination: 'Tokyo Adventure',
    country: 'Japan',
    duration: '7 days',
    image: 'https://images.unsplash.com/photo-1623566713971-1f7ad1dc7bfb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0b2t5byUyMHNreWxpbmUlMjB0cmF2ZWx8ZW58MXx8fHwxNzYxODA0NjY1fDA&ixlib=rb-4.1.0&q=80&w=1080',
    rating: 4.8,
    reviewCount: 124,
    tags: ['Urban', 'Culture', 'Food'],
    description: 'Experience the perfect blend of tradition and modernity in Tokyo. This 7-day itinerary covers all the must-see attractions while leaving room for spontaneous discoveries.',
    price: '$1,850',
    travelers: 2,
    dates: 'Best: Mar-May, Sep-Nov',
    itinerary: [
      {
        day: 1,
        title: 'Arrival & Shibuya Exploration',
        activities: [
          { time: '14:00', activity: 'Check-in at hotel in Shibuya', icon: '🏨' },
          { time: '16:00', activity: 'Shibuya Crossing & Hachiko Statue', icon: '📸' },
          { time: '18:30', activity: 'Dinner at local izakaya', icon: '🍜' },
          { time: '20:00', activity: 'Evening walk through Shibuya district', icon: '🚶' }
        ]
      },
      {
        day: 2,
        title: 'Traditional Tokyo',
        activities: [
          { time: '09:00', activity: 'Visit Senso-ji Temple in Asakusa', icon: '⛩️' },
          { time: '11:00', activity: 'Shopping at Nakamise Street', icon: '🛍️' },
          { time: '13:00', activity: 'Lunch at traditional restaurant', icon: '🍱' },
          { time: '15:00', activity: 'Tokyo Skytree observation deck', icon: '🗼' },
          { time: '18:00', activity: 'Sumida River cruise', icon: '🚢' }
        ]
      },
      {
        day: 3,
        title: 'Modern Tokyo & Shopping',
        activities: [
          { time: '10:00', activity: 'Explore Harajuku & Takeshita Street', icon: '👗' },
          { time: '12:00', activity: 'Meiji Shrine visit', icon: '⛩️' },
          { time: '14:00', activity: 'Lunch in Omotesando', icon: '🍽️' },
          { time: '16:00', activity: 'Shopping in Ginza district', icon: '💎' }
        ]
      },
      {
        day: 4,
        title: 'Day Trip to Mt. Fuji',
        activities: [
          { time: '07:00', activity: 'Depart for Mt. Fuji area', icon: '🚌' },
          { time: '10:00', activity: 'Lake Kawaguchi & Mt. Fuji views', icon: '🏔️' },
          { time: '13:00', activity: 'Lunch with Fuji view', icon: '🍜' },
          { time: '15:00', activity: 'Visit Chureito Pagoda', icon: '📸' },
          { time: '19:00', activity: 'Return to Tokyo', icon: '🚌' }
        ]
      },
      {
        day: 5,
        title: 'Akihabara & TeamLab',
        activities: [
          { time: '10:00', activity: 'Explore Akihabara electronics district', icon: '🎮' },
          { time: '12:30', activity: 'Themed cafe lunch', icon: '☕' },
          { time: '15:00', activity: 'teamLab Borderless digital art', icon: '🎨' },
          { time: '19:00', activity: 'Dinner in Odaiba', icon: '🍣' }
        ]
      },
      {
        day: 6,
        title: 'Tsukiji & Tokyo Tower',
        activities: [
          { time: '06:00', activity: 'Early morning Tsukiji fish market', icon: '🐟' },
          { time: '08:00', activity: 'Sushi breakfast', icon: '🍣' },
          { time: '11:00', activity: 'Imperial Palace gardens', icon: '🏯' },
          { time: '14:00', activity: 'Tokyo Tower visit', icon: '🗼' },
          { time: '18:00', activity: 'Roppongi dinner & nightlife', icon: '🌃' }
        ]
      },
      {
        day: 7,
        title: 'Last Day & Departure',
        activities: [
          { time: '09:00', activity: 'Final souvenir shopping', icon: '🎁' },
          { time: '11:00', activity: 'Visit local neighborhood cafe', icon: '☕' },
          { time: '13:00', activity: 'Hotel checkout', icon: '🏨' },
          { time: '15:00', activity: 'Depart to airport', icon: '✈️' }
        ]
      }
    ],
    reviews: [
      {
        id: 1,
        author: 'Mike Johnson',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike',
        rating: 5,
        date: 'Oct 2024',
        text: 'Absolutely amazing itinerary! Followed it exactly and had the best time. The day trip to Mt. Fuji was a highlight!'
      },
      {
        id: 2,
        author: 'Emma Wilson',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma',
        rating: 5,
        date: 'Sep 2024',
        text: 'Perfect balance of traditional and modern Tokyo. The teamLab experience was mind-blowing!'
      },
      {
        id: 3,
        author: 'David Lee',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David',
        rating: 4,
        date: 'Aug 2024',
        text: 'Great plan overall. I would suggest adding more time in Harajuku for shopping enthusiasts.'
      }
    ]
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white pb-24">
      {/* Hero Image */}
      <div className="relative h-64">
        <ImageWithFallback
          src={plan.image}
          alt={plan.destination}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        
        {/* Header Buttons */}
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex gap-2">
            <button className="w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center hover:bg-white transition-colors">
              <Share2 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsLiked(!isLiked)}
              className="w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center hover:bg-white transition-colors"
            >
              <Heart className={`w-5 h-5 ${isLiked ? 'fill-red-500 text-red-500' : ''}`} />
            </button>
          </div>
        </div>

        {/* Title Overlay */}
        <div className="absolute bottom-4 left-4 right-4 text-white">
          <h1 className="text-2xl font-semibold mb-1">{plan.destination}</h1>
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="w-4 h-4" />
            <span>{plan.country}</span>
          </div>
        </div>
      </div>

      {/* Author & Rating */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {isAIPlan ? (
              <img
                src={plan.authorAvatar}
                alt={plan.author}
                className="w-12 h-12 rounded-full"
              />
            ) : (
              <ImageWithFallback
                src={plan.authorAvatar}
                alt={plan.author}
                className="w-12 h-12 rounded-full"
              />
            )}
            <div>
              <div className="flex items-center gap-2">
                <p className="font-semibold">{plan.author}</p>
                {isAIPlan && <Sparkles className="w-4 h-4 text-purple-600" />}
              </div>
              <p className="text-sm text-gray-500">{isAIPlan ? 'AI Generated Plan' : 'Travel Expert'}</p>
            </div>
          </div>
          {isAIPlan ? (
            <div className="text-right">
              <Badge className="bg-gradient-to-r from-blue-500 to-purple-600 mb-1">
                {plan.confidence}% match
              </Badge>
              <p className="text-xs text-gray-500">{plan.basedOn}</p>
            </div>
          ) : (
            <div className="text-right">
              <div className="flex items-center gap-1">
                <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                <span className="font-semibold">{plan.rating}</span>
              </div>
              <p className="text-xs text-gray-500">{plan.reviewCount} reviews</p>
            </div>
          )}
        </div>

        {/* Tags */}
        <div className="flex gap-2 flex-wrap">
          {plan.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              {tag}
            </Badge>
          ))}
        </div>
      </div>

      {/* Quick Info */}
      <div className="px-6 py-4 border-b">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <Calendar className="w-5 h-5 text-blue-600 mx-auto mb-1" />
            <p className="text-xs text-gray-500">Duration</p>
            <p className="font-semibold text-sm">{plan.duration}</p>
          </div>
          <div className="text-center">
            <Users className="w-5 h-5 text-purple-600 mx-auto mb-1" />
            <p className="text-xs text-gray-500">Group Size</p>
            <p className="font-semibold text-sm">{plan.travelers} people</p>
          </div>
          <div className="text-center">
            <span className="text-2xl block mb-1">💰</span>
            <p className="text-xs text-gray-500">Est. Cost</p>
            <p className="font-semibold text-sm">{plan.price}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="px-6 py-4">
        <TabsList className={`grid w-full ${isAIPlan ? 'grid-cols-2' : 'grid-cols-3'}`}>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
          {!isAIPlan && <TabsTrigger value="reviews">Reviews</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview" className="space-y-4 mt-4">
          {isAIPlan && (
            <Card className="p-4 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold mb-1 text-sm">AI-Curated Experience</p>
                  <p className="text-xs text-gray-600">
                    This personalized itinerary was created by Qico AI based on your travel history and preferences. You can customize it further after booking.
                  </p>
                </div>
              </div>
            </Card>
          )}
          <div>
            <h3 className="font-semibold mb-2">About This Trip</h3>
            <p className="text-gray-700 text-sm leading-relaxed">{plan.description}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Best Time to Visit</h3>
            <p className="text-sm text-gray-600">{plan.dates}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">What's Included</h3>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>
                <span>Detailed daily itinerary</span>
              </li>
              <li className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>
                <span>Restaurant recommendations</span>
              </li>
              <li className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>
                <span>Transportation tips</span>
              </li>
              <li className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>
                <span>Money-saving advice</span>
              </li>
            </ul>
          </div>
        </TabsContent>

        <TabsContent value="itinerary" className="space-y-4 mt-4">
          {plan.itinerary.map((day) => (
            <Card key={day.day} className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="font-semibold text-blue-600">{day.day}</span>
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold">Day {day.day}</h4>
                  <p className="text-sm text-gray-600">{day.title}</p>
                </div>
              </div>
              <div className="space-y-3 ml-13">
                {day.activities.map((activity, idx) => (
                  <div key={idx} className="flex gap-3">
                    <div className="flex-shrink-0">
                      <span className="text-lg">{activity.icon}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Clock className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500">{activity.time}</span>
                      </div>
                      <p className="text-sm mt-1">{activity.activity}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="reviews" className="space-y-4 mt-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
                <span className="text-2xl font-semibold">{plan.rating}</span>
              </div>
              <p className="text-sm text-gray-500">{plan.reviewCount} reviews</p>
            </div>
            <Button variant="outline" size="sm">Write Review</Button>
          </div>

          <div className="space-y-4">
            {plan.reviews.map((review) => (
              <Card key={review.id} className="p-4">
                <div className="flex items-start gap-3">
                  <ImageWithFallback
                    src={review.avatar}
                    alt={review.author}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-semibold text-sm">{review.author}</p>
                      <span className="text-xs text-gray-500">{review.date}</span>
                    </div>
                    <div className="flex gap-1 mb-2">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${
                            i < review.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-sm text-gray-700">{review.text}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Use This Plan Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-3 sm:p-4 shadow-lg">
        <div className="max-w-md mx-auto px-1 sm:px-2">
          <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 h-11 sm:h-12 text-xs sm:text-sm px-4">
            Use This Plan for My Trip
          </Button>
        </div>
      </div>
    </div>
  );
}