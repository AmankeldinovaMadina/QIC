import { ArrowLeft, Bell, CheckSquare, Calendar as CalendarIcon, AlertCircle, Shirt, FileText, Info } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface TripCalendarPageProps {
  onBack: () => void;
  onChecklistClick: () => void;
  onDayClick: (date: number) => void;
  onImportantNotesClick?: () => void;
  onNotifications: () => void;
}

interface CalendarDay {
  date: number;
  hasEvent: boolean;
  events?: string[];
}

export function TripCalendarPage({ onBack, onChecklistClick, onDayClick, onImportantNotesClick, onNotifications }: TripCalendarPageProps) {
  const [selectedDate, setSelectedDate] = useState<number | null>(25);

  // Generate calendar days for October/November
  const calendarDays: CalendarDay[] = [
    { date: 20, hasEvent: false },
    { date: 21, hasEvent: false },
    { date: 22, hasEvent: false },
    { date: 23, hasEvent: false },
    { date: 24, hasEvent: false },
    { date: 25, hasEvent: true, events: ['Flight to Dubai', 'Hotel Check-in'] },
    { date: 26, hasEvent: true, events: ['Burj Khalifa Visit', 'Desert Safari'] },
    { date: 27, hasEvent: true, events: ['City Tour'] },
    { date: 28, hasEvent: true, events: ['Gold Souk', 'Marina Cruise'] },
    { date: 29, hasEvent: true, events: ['Beach Day'] },
    { date: 30, hasEvent: true, events: ['Shopping'] },
    { date: 31, hasEvent: true, events: ['Return Flight'] },
    { date: 1, hasEvent: false },
    { date: 2, hasEvent: false },
    { date: 3, hasEvent: false },
    { date: 4, hasEvent: false },
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
          <div className="flex-1">
            <h1 className="font-semibold">Trip to Dubai</h1>
            <p className="text-sm text-gray-500">Oct 25 - Oct 31, 2025</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>

        {/* Checklist Button */}
        <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 mb-3">
          <button
            onClick={onChecklistClick}
            className="w-full p-4 flex items-center justify-between hover:bg-green-100/50 transition-colors rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <CheckSquare className="w-5 h-5 text-white" />
              </div>
              <div className="text-left">
                <p className="font-semibold">Checklist</p>
                <p className="text-sm text-gray-600">8 of 14 completed</p>
              </div>
            </div>
            <div className="relative w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="absolute h-full bg-green-500 rounded-full" style={{ width: '57%' }} />
            </div>
          </button>
        </Card>

        {/* Important Notes Button */}
        <Card className="bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
          <button
            onClick={onImportantNotesClick}
            className="w-full p-4 flex items-center justify-between hover:bg-orange-100/50 transition-colors rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-white" />
              </div>
              <div className="text-left">
                <p className="font-semibold">Important Notes</p>
                <p className="text-sm text-gray-600">Travel tips & requirements</p>
              </div>
            </div>
            <Badge variant="secondary" className="bg-orange-200 text-orange-800 border-0">
              New
            </Badge>
          </button>
        </Card>
      </div>

      {/* Google Calendar Section */}
      <div className="px-6 py-6">
        <Card className="p-4 border-2">
          <h3 className="font-semibold mb-4">Google Calendar</h3>
          
          {/* Calendar Grid */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            {calendarDays.map((day) => (
              <button
                key={day.date}
                onClick={() => {
                  if (day.hasEvent) {
                    setSelectedDate(day.date);
                    onDayClick(day.date);
                  }
                }}
                className={`
                  aspect-square rounded-lg flex items-center justify-center transition-all
                  ${day.hasEvent 
                    ? selectedDate === day.date
                      ? 'bg-green-500 text-white'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-50 text-gray-400'
                  }
                  ${selectedDate === day.date ? 'ring-2 ring-green-500 ring-offset-2' : ''}
                `}
              >
                <span className="font-semibold">{day.date}</span>
              </button>
            ))}
          </div>

          {/* Export Button */}
          <Button 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            <CalendarIcon className="w-4 h-4 mr-2" />
            Export to Google Calendar
          </Button>
        </Card>
      </div>
    </div>
  );
}