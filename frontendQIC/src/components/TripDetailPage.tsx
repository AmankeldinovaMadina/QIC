import { ArrowLeft, ChevronLeft, ChevronRight, MapPin, Clock, CheckSquare, Calendar as CalendarIcon } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { tripsApi, TripResponse } from '../utils/api';
import { generateICS, downloadICS, CalendarEvent } from '../utils/calendar';

interface TripDetailPageProps {
  onBack: () => void;
  onChecklistClick: () => void;
  onCalendarClick: () => void;
  tripId: string;
}

interface TimelineEvent {
  time: string;
  title: string;
  location?: string;
  status: 'completed' | 'upcoming' | 'optional';
  startTime?: Date;
  endTime?: Date;
}

interface TripDay {
  date: string; // Format: "Oct 25"
  day: string; // Format: "Friday"
  dateObj: Date;
}

export function TripDetailPage({ onBack, onChecklistClick, onCalendarClick, tripId }: TripDetailPageProps) {
  const [currentDate, setCurrentDate] = useState(0);
  const [trip, setTrip] = useState<TripResponse | null>(null);
  const [tripPlan, setTripPlan] = useState<any>(null);
  const [tripDays, setTripDays] = useState<TripDay[]>([]);
  const [dailySchedules, setDailySchedules] = useState<{ [key: number]: TimelineEvent[] }>({});
  const [isLoading, setIsLoading] = useState(true);

  // Fetch trip data and plan
  useEffect(() => {
    const fetchTripData = async () => {
      try {
        setIsLoading(true);
        const tripData = await tripsApi.getTrip(tripId);
        setTrip(tripData);
        
        // Generate trip days from start_date to end_date
        const startDate = new Date(tripData.start_date);
        const endDate = new Date(tripData.end_date);
        const days: TripDay[] = [];
        
        const currentDate = new Date(startDate);
        while (currentDate <= endDate) {
          const dateStr = currentDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          const dayStr = currentDate.toLocaleDateString('en-US', { weekday: 'long' });
          days.push({
            date: dateStr,
            day: dayStr,
            dateObj: new Date(currentDate)
          });
          currentDate.setDate(currentDate.getDate() + 1);
        }
        setTripDays(days);
        
        // Fetch trip plan if available (may not exist if trip not finalized)
        // Note: 404s are expected and handled silently - browser may still log them
        try {
          const plan = await tripsApi.getTripPlan(tripId);
          if (plan) {
            setTripPlan(plan);
          }
        } catch (planError) {
          // Silently ignore - plan may not exist yet
        }
      } catch (error) {
        console.error('Failed to fetch trip data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTripData();
  }, [tripId]);
  
  // Build daily schedules from trip plan and flight data
  useEffect(() => {
    if (!trip || tripDays.length === 0) return;
    
    const schedules: { [key: number]: TimelineEvent[] } = {};
    
    // Add flight arrival on first day if available
    if (trip.selected_flight?.arrival_time && tripDays.length > 0) {
      const arrivalDate = new Date(trip.selected_flight.arrival_time);
      const firstDay = tripDays[0].dateObj;
      if (arrivalDate.toDateString() === firstDay.toDateString()) {
        if (!schedules[0]) schedules[0] = [];
        schedules[0].push({
          time: arrivalDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
          title: `Arrival at ${trip.selected_flight.arrival_airport || 'Airport'}`,
          location: trip.selected_flight.arrival_airport || undefined,
          status: 'upcoming',
          startTime: arrivalDate,
          endTime: arrivalDate
        });
      }
    }
    
    // Add flight departure on last day if available
    if (trip.selected_flight?.departure_time && tripDays.length > 0) {
      const departureDate = new Date(trip.selected_flight.departure_time);
      const lastDay = tripDays[tripDays.length - 1].dateObj;
      if (departureDate.toDateString() === lastDay.toDateString()) {
        const dayIndex = tripDays.length - 1;
        if (!schedules[dayIndex]) schedules[dayIndex] = [];
        schedules[dayIndex].push({
          time: departureDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
          title: `Departure from ${trip.selected_flight.departure_airport || 'Airport'}`,
          location: trip.selected_flight.departure_airport || undefined,
          status: 'upcoming',
          startTime: departureDate,
          endTime: departureDate
        });
      }
    }
    
    // Add hotel check-in on first day
    if (trip.selected_hotel && tripDays.length > 0) {
      if (!schedules[0]) schedules[0] = [];
      schedules[0].push({
        time: '3:00 PM', // Default check-in time
        title: 'Hotel Check-in',
        location: trip.selected_hotel.name || 'Hotel',
        status: 'upcoming',
        startTime: new Date(tripDays[0].dateObj.setHours(15, 0, 0, 0)),
        endTime: new Date(tripDays[0].dateObj.setHours(15, 30, 0, 0))
      });
    }
    
    // Add events from trip plan
    if (tripPlan?.plan_json?.days) {
      tripPlan.plan_json.days.forEach((planDay: any) => {
        const dayDate = new Date(planDay.date);
        const dayIndex = tripDays.findIndex(d => 
          d.dateObj.toDateString() === dayDate.toDateString()
        );
        
        if (dayIndex >= 0 && planDay.events) {
          if (!schedules[dayIndex]) schedules[dayIndex] = [];
          
          planDay.events.forEach((event: any) => {
            const startTime = new Date(event.start);
            const endTime = new Date(event.end);
            
            schedules[dayIndex].push({
              time: startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
              title: event.title,
              location: event.location_name || event.address || undefined,
              status: event.priority === 'optional' ? 'optional' : 'upcoming',
              startTime,
              endTime
            });
          });
        }
      });
    }
    
    // Sort events by time for each day
    Object.keys(schedules).forEach(key => {
      const index = parseInt(key);
      schedules[index].sort((a, b) => {
        if (a.startTime && b.startTime) {
          return a.startTime.getTime() - b.startTime.getTime();
        }
        return 0;
      });
    });
    
    setDailySchedules(schedules);
  }, [trip, tripPlan, tripDays]);
  
  const schedule = dailySchedules[currentDate] || [];
  
  // Handle Google Calendar export
  const handleExportToCalendar = () => {
    if (!trip) return;
    
    const calendarEvents: CalendarEvent[] = [];
    
    // Add flight events
    if (trip.selected_flight?.arrival_time) {
      const arrivalDate = new Date(trip.selected_flight.arrival_time);
      calendarEvents.push({
        title: `Arrival at ${trip.selected_flight.arrival_airport || 'Airport'}`,
        description: `Flight ${trip.selected_flight.airline || ''} ${trip.selected_flight.flight_number || ''}`,
        location: trip.selected_flight.arrival_airport || undefined,
        start: arrivalDate,
        end: new Date(arrivalDate.getTime() + 30 * 60000) // 30 minutes
      });
    }
    
    if (trip.selected_flight?.departure_time) {
      const departureDate = new Date(trip.selected_flight.departure_time);
      calendarEvents.push({
        title: `Departure from ${trip.selected_flight.departure_airport || 'Airport'}`,
        description: `Flight ${trip.selected_flight.airline || ''} ${trip.selected_flight.flight_number || ''}`,
        location: trip.selected_flight.departure_airport || undefined,
        start: departureDate,
        end: new Date(departureDate.getTime() + 30 * 60000) // 30 minutes
      });
    }
    
    // Add hotel check-in
    if (trip.selected_hotel) {
      const checkInDate = new Date(trip.start_date);
      checkInDate.setHours(15, 0, 0, 0);
      calendarEvents.push({
        title: 'Hotel Check-in',
        description: trip.selected_hotel.name || 'Hotel',
        location: trip.selected_hotel.address || trip.selected_hotel.name || undefined,
        start: checkInDate,
        end: new Date(checkInDate.getTime() + 30 * 60000)
      });
    }
    
    // Add events from trip plan
    if (tripPlan?.plan_json?.days) {
      tripPlan.plan_json.days.forEach((planDay: any) => {
        if (planDay.events) {
          planDay.events.forEach((event: any) => {
            calendarEvents.push({
              title: event.title,
              description: event.notes || undefined,
              location: event.location_name || event.address || undefined,
              start: new Date(event.start),
              end: new Date(event.end)
            });
          });
        }
      });
    }
    
    const icsContent = generateICS(calendarEvents, `Trip to ${trip.to_city}`);
    const filename = `trip-${trip.to_city.toLowerCase().replace(/\s+/g, '-')}-${tripId}.ics`;
    downloadICS(icsContent, filename);
  };

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
            <h1 className="font-semibold">
              {isLoading ? 'Loading...' : trip ? `Trip to ${trip.to_city}` : 'Trip Details'}
            </h1>
            <p className="text-sm text-gray-500">
              {trip && tripDays.length > 0 
                ? `${tripDays[0].date} - ${tripDays[tripDays.length - 1].date}, ${new Date(trip.start_date).getFullYear()}`
                : 'Loading dates...'}
            </p>
          </div>

        </div>

        {/* Date Navigation */}
        <div className="px-6 pb-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentDate(Math.max(0, currentDate - 1))}
              disabled={currentDate === 0 || tripDays.length === 0}
              className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button 
              onClick={onCalendarClick}
              className="flex-1 text-center bg-gray-50 rounded-lg py-3 px-4 hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <p className="font-semibold">
                {tripDays.length > 0 ? tripDays[currentDate]?.date : 'Loading...'}
              </p>
              <p className="text-sm text-gray-600">
                {tripDays.length > 0 ? tripDays[currentDate]?.day : ''}
              </p>
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
        {isLoading ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading itinerary...</p>
          </div>
        ) : schedule.length === 0 ? (
          <div className="text-center py-8 px-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <p className="text-gray-700 font-semibold mb-2">No Events Scheduled</p>
              <p className="text-sm text-gray-600 mb-4">
                {tripPlan 
                  ? 'No events scheduled for this day.'
                  : 'Trip plan not available. Finalize your trip to see the AI-generated daily itinerary with activities and events.'}
              </p>
            </div>
          </div>
        ) : (
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
        )}

        {/* Export to Calendar */}
        <div className="mt-6 mb-20">
          <Button 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" 
            onClick={handleExportToCalendar}
            disabled={isLoading || !trip}
          >
            <CalendarIcon className="w-4 h-4 mr-2" />
            Export to Google Calendar
          </Button>
        </div>
      </div>

    </div>
  );
}