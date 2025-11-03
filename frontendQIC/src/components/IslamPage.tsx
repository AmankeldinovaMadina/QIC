import { ArrowLeft, Clock, MapPin, Book, Calendar } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface IslamPageProps {
  onBack: () => void;
}

export function IslamPage({ onBack }: IslamPageProps) {
  const prayerTimes = [
    { name: 'Fajr', time: '5:12 AM' },
    { name: 'Dhuhr', time: '12:15 PM' },
    { name: 'Asr', time: '3:30 PM' },
    { name: 'Maghrib', time: '6:05 PM' },
    { name: 'Isha', time: '7:25 PM' }
  ];

  const islamicEvents = [
    {
      id: 1,
      title: 'Jumah Prayer',
      date: 'Friday, Nov 1',
      location: 'Grand Mosque',
      time: '1:00 PM'
    },
    {
      id: 2,
      title: 'Islamic Lecture Series',
      date: 'Saturday, Nov 2',
      location: 'Community Center',
      time: '7:00 PM'
    },
    {
      id: 3,
      title: 'Quran Study Circle',
      date: 'Sunday, Nov 3',
      location: 'Islamic Center',
      time: '5:00 PM'
    }
  ];

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-teal-50 to-white pb-6">
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
            <h1 className="text-xl font-semibold">Islamic Services</h1>
            <p className="text-sm text-gray-500">Prayer times & events</p>
          </div>
        </div>
      </div>

      {/* Islamic Date Card */}
      <div className="px-6 py-4">
        <Card className="p-5 bg-gradient-to-br from-teal-600 to-cyan-600 border-0 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-100 text-sm mb-1">Islamic Date</p>
              <p className="text-xl">15 Jumada al-Awwal 1447</p>
            </div>
            <Calendar className="w-8 h-8 text-teal-200" />
          </div>
        </Card>
      </div>

      {/* Prayer Times */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Prayer Times</h2>
          <Badge variant="outline" className="text-xs">
            Today
          </Badge>
        </div>
        <Card className="divide-y">
          {prayerTimes.map((prayer, index) => (
            <div key={index} className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-teal-600" />
                </div>
                <span className="font-medium">{prayer.name}</span>
              </div>
              <span className="text-teal-600 font-semibold">{prayer.time}</span>
            </div>
          ))}
        </Card>
      </div>

      {/* Nearby Mosques */}
      <div className="px-6 py-4">
        <h2 className="font-semibold mb-4">Nearby Mosques</h2>
        <div className="space-y-3">
          <Card className="p-4 border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Grand Mosque</h3>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>0.5 km away</span>
                </div>
              </div>
              <button className="px-3 py-1 bg-teal-50 text-teal-700 rounded-lg hover:bg-teal-100 transition-colors text-sm">
                Directions
              </button>
            </div>
          </Card>
          <Card className="p-4 border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Al-Noor Mosque</h3>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>1.2 km away</span>
                </div>
              </div>
              <button className="px-3 py-1 bg-teal-50 text-teal-700 rounded-lg hover:bg-teal-100 transition-colors text-sm">
                Directions
              </button>
            </div>
          </Card>
        </div>
      </div>

      {/* Islamic Events */}
      <div className="px-6 py-4">
        <h2 className="font-semibold mb-4">Upcoming Events</h2>
        <div className="space-y-3">
          {islamicEvents.map((event) => (
            <Card key={event.id} className="p-4 border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center flex-shrink-0">
                  <Book className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">{event.title}</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{event.date}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>{event.time}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>{event.location}</span>
                    </div>
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
