import { ArrowLeft, Calendar, MapPin, Clock, Ticket } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface EventPageProps {
  onBack: () => void;
}

interface Event {
  id: number;
  title: string;
  location: string;
  date: string;
  time: string;
  price: string;
  image: string;
  category: string;
  spotsLeft?: number;
}

export function EventPage({ onBack }: EventPageProps) {
  const events: Event[] = [
    {
      id: 1,
      title: 'Summer Music Festival',
      location: 'Central Park',
      date: 'Nov 25, 2025',
      time: '6:00 PM',
      price: '$45',
      image: 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800&q=80',
      category: 'Music',
      spotsLeft: 12
    },
    {
      id: 2,
      title: 'Tech Innovation Summit',
      location: 'Convention Center',
      date: 'Dec 5, 2025',
      time: '9:00 AM',
      price: '$99',
      image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80',
      category: 'Conference'
    },
    {
      id: 3,
      title: 'Food & Wine Tasting',
      location: 'Grand Hotel',
      date: 'Nov 30, 2025',
      time: '7:00 PM',
      price: '$75',
      image: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80',
      category: 'Food',
      spotsLeft: 8
    },
    {
      id: 4,
      title: 'Charity Marathon',
      location: 'City Stadium',
      date: 'Dec 10, 2025',
      time: '7:00 AM',
      price: 'Free',
      image: 'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800&q=80',
      category: 'Sports'
    }
  ];

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
          <div>
            <h1 className="text-xl font-semibold">Events</h1>
            <p className="text-sm text-gray-500">Upcoming events near you</p>
          </div>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="px-6 py-4 flex gap-2 overflow-x-auto no-scrollbar">
        <Badge variant="default" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 whitespace-nowrap cursor-pointer">
          All Events
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Music
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Food
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Sports
        </Badge>
        <Badge variant="outline" className="px-4 py-2 whitespace-nowrap cursor-pointer hover:bg-gray-50">
          Conference
        </Badge>
      </div>

      {/* Event Cards */}
      <div className="px-6 space-y-4">
        {events.map((event) => (
          <Card key={event.id} className="overflow-hidden border-0 shadow-md hover:shadow-xl transition-shadow cursor-pointer">
            <div className="relative h-40">
              <ImageWithFallback 
                src={event.image}
                alt={event.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3">
                <Badge className="bg-white/90 text-gray-800 hover:bg-white">
                  {event.category}
                </Badge>
              </div>
              {event.spotsLeft && (
                <div className="absolute top-3 right-3">
                  <Badge className="bg-red-500 hover:bg-red-600">
                    {event.spotsLeft} spots left
                  </Badge>
                </div>
              )}
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-3">{event.title}</h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span>{event.location}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>{event.date}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span>{event.time}</span>
                </div>
              </div>
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <div className="flex items-center gap-2">
                  <Ticket className="w-4 h-4 text-purple-600" />
                  <span className="font-semibold text-purple-600">{event.price}</span>
                </div>
                <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                  Book Now
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
