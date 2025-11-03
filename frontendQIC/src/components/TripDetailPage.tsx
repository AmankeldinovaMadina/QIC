import { ArrowLeft, ChevronLeft, ChevronRight, MapPin, Clock, CheckSquare, MessageCircle, Calendar as CalendarIcon, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import qicoAvatar from 'figma:asset/df749756eb2f3e1f6a511fd7b1a552bd3aabda73.png';

interface TripDetailPageProps {
  onBack: () => void;
  onChecklistClick: () => void;
  onCalendarClick: () => void;
  tripDetails: any;
}

interface TimelineEvent {
  time: string;
  title: string;
  location?: string;
  status: 'completed' | 'upcoming' | 'optional';
}

export function TripDetailPage({ onBack, onChecklistClick, onCalendarClick, tripDetails }: TripDetailPageProps) {
  const [currentDate, setCurrentDate] = useState(0);
  const [showQico, setShowQico] = useState(false);

  const tripDays = [
    { date: 'Oct 25', day: 'Friday' },
    { date: 'Oct 26', day: 'Saturday' },
    { date: 'Oct 27', day: 'Sunday' },
    { date: 'Oct 28', day: 'Monday' },
    { date: 'Oct 29', day: 'Tuesday' },
    { date: 'Oct 30', day: 'Wednesday' },
    { date: 'Oct 31', day: 'Thursday' }
  ];

  const dailySchedules: { [key: number]: TimelineEvent[] } = {
    0: [
      { time: '9:00 AM', title: 'Departure from home', status: 'completed' },
      { time: '12:00 PM', title: 'Arrival at Dubai Airport', location: 'DXB', status: 'upcoming' },
      { time: '3:00 PM', title: 'Hotel Check-in', location: 'Luxury Resort & Spa', status: 'upcoming' },
      { time: '6:00 PM', title: 'Welcome Dinner', location: 'Hotel Restaurant', status: 'optional' }
    ],
    1: [
      { time: '8:00 AM', title: 'Breakfast at hotel', status: 'upcoming' },
      { time: '10:00 AM', title: 'Visit Burj Khalifa', location: 'Downtown Dubai', status: 'upcoming' },
      { time: '2:00 PM', title: 'Lunch at Dubai Mall', status: 'upcoming' },
      { time: '6:00 PM', title: 'Desert Safari', status: 'upcoming' }
    ],
    2: [
      { time: '9:00 AM', title: 'City Tour', status: 'upcoming' },
      { time: '1:00 PM', title: 'Gold Souk visit', status: 'optional' },
      { time: '7:00 PM', title: 'Marina Dinner Cruise', status: 'upcoming' }
    ]
  };

  const schedule = dailySchedules[currentDate] || dailySchedules[0];

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 border-b">
        <div className="px-6 py-4 flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="font-semibold">Trip to Dubai</h1>
            <p className="text-sm text-gray-500">Oct 25 - Oct 31, 2025</p>
          </div>

        </div>

        {/* Date Navigation */}
        <div className="px-6 pb-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentDate(Math.max(0, currentDate - 1))}
              disabled={currentDate === 0}
              className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button 
              onClick={onCalendarClick}
              className="flex-1 text-center bg-gray-50 rounded-lg py-3 px-4 hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <p className="font-semibold">{tripDays[currentDate].date}</p>
              <p className="text-sm text-gray-600">{tripDays[currentDate].day}</p>
            </button>
            <button
              onClick={() => setCurrentDate(Math.min(tripDays.length - 1, currentDate + 1))}
              disabled={currentDate === tripDays.length - 1}
              className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 disabled:opacity-30 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="space-y-4">
          {schedule.map((event, index) => (
            <div key={index} className="flex gap-4">
              {/* Time */}
              <div className="w-20 flex-shrink-0 pt-1">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-sm text-gray-600">{event.time}</span>
                </div>
              </div>

              {/* Event Card */}
              <div className="flex-1">
                <Card className={`p-4 border-l-4 ${
                  event.status === 'completed' 
                    ? 'border-l-green-500 bg-green-50' 
                    : event.status === 'optional'
                    ? 'border-l-gray-300 bg-gray-50'
                    : 'border-l-blue-500 bg-blue-50'
                }`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold">{event.title}</h3>
                      {event.location && (
                        <div className="flex items-center gap-1 mt-1">
                          <MapPin className="w-3 h-3 text-gray-500" />
                          <span className="text-sm text-gray-600">{event.location}</span>
                        </div>
                      )}
                    </div>
                    {event.status === 'completed' && (
                      <Badge className="bg-green-500">Done</Badge>
                    )}
                    {event.status === 'optional' && (
                      <Badge variant="outline">Optional</Badge>
                    )}
                  </div>
                  {event.location && event.status !== 'completed' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2 text-blue-600 border-blue-200 hover:bg-blue-50"
                    >
                      <MapPin className="w-4 h-4 mr-1" />
                      Open in Maps
                    </Button>
                  )}
                </Card>
              </div>
            </div>
          ))}
        </div>

        {/* Export to Calendar */}
        <div className="mt-6 mb-20">
          <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" onClick={onCalendarClick}>
            <CalendarIcon className="w-4 h-4 mr-2" />
            Export to Google Calendar
          </Button>
        </div>
      </div>

      {/* Qico AI Assistant */}
      <div className="sticky bottom-0 bg-white border-t p-4">
        <div className="max-w-md mx-auto">
          {!showQico ? (
            <button
              onClick={() => setShowQico(true)}
              className="w-full flex items-center justify-center gap-3 p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg"
            >
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                <Sparkles className="w-5 h-5" />
              </div>
              <div className="text-left">
                <p className="font-semibold">Need help with your plans?</p>
                <p className="text-sm text-blue-100">Chat with Qico AI</p>
              </div>
              <MessageCircle className="w-5 h-5 ml-auto" />
            </button>
          ) : (
            <Card className="p-4 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
              <div className="flex items-start gap-3 mb-3">
                <img src={qicoAvatar} alt="Qico AI" className="w-10 h-10 rounded-full flex-shrink-0" />
                <div className="flex-1">
                  <p className="font-semibold mb-1">Qico AI</p>
                  <p className="text-sm text-gray-600">
                    I can help you adjust your schedule, find nearby places, or answer any questions about your trip!
                  </p>
                </div>
                <button
                  onClick={() => setShowQico(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="flex gap-2">
                <input
                  placeholder="Ask me anything..."
                  className="flex-1 px-3 py-2 bg-white border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                  Send
                </Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}