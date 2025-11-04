import { ArrowLeft, Bell, CheckSquare, Calendar as CalendarIcon, AlertCircle, Shirt, FileText, Info } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { tripsApi, TripResponse } from '../utils/api';
import { generateICS, downloadICS, CalendarEvent } from '../utils/calendar';

interface TripCalendarPageProps {
  onBack: () => void;
  onChecklistClick: () => void;
  onDayClick: (date: number) => void;
  onImportantNotesClick?: () => void;
  onNotifications: () => void;
  tripId: string;
}

interface CalendarDay {
  date: number;
  month: number;
  year: number;
  hasEvent: boolean;
  events?: string[];
  dateObj: Date;
}

export function TripCalendarPage({ onBack, onChecklistClick, onDayClick, onImportantNotesClick, onNotifications, tripId }: TripCalendarPageProps) {
  const [trip, setTrip] = useState<TripResponse | null>(null);
  const [tripPlan, setTripPlan] = useState<any>(null);
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);
  const [selectedDate, setSelectedDate] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [checklistProgress, setChecklistProgress] = useState({ completed: 0, total: 0 });

  // Fetch trip data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const tripData = await tripsApi.getTrip(tripId);
        setTrip(tripData);
        
        // Generate calendar days - proper calendar grid
        const startDate = new Date(tripData.start_date);
        const endDate = new Date(tripData.end_date);
        const days: CalendarDay[] = [];
        
        // Determine which month(s) to show
        // If trip spans multiple months, show both months
        const startMonth = startDate.getMonth();
        const endMonth = endDate.getMonth();
        const startYear = startDate.getFullYear();
        const endYear = endDate.getFullYear();
        
        // Show from start month
        const monthStart = new Date(startYear, startMonth, 1);
        
        // Determine end month (if trip spans months, show end month too)
        let displayEnd: Date;
        if (startMonth === endMonth && startYear === endYear) {
          // Same month - show that month plus next month
          displayEnd = new Date(startYear, startMonth + 2, 0); // Last day of next month
        } else {
          // Different months - show end month
          displayEnd = new Date(endYear, endMonth + 1, 0); // Last day of end month
        }
        
        // Find the first day of the week (Sunday = 0) for the start month
        const firstDayOfWeek = monthStart.getDay();
        
        // Add empty cells for days before month starts (to align with weekday headers)
        for (let i = 0; i < firstDayOfWeek; i++) {
          days.push({
            date: 0, // Placeholder
            month: monthStart.getMonth(),
            year: monthStart.getFullYear(),
            hasEvent: false,
            events: [],
            dateObj: new Date(0) // Invalid date as placeholder
          });
        }
        
        // Add all days from start month to display end
        const currentDate = new Date(monthStart);
        while (currentDate <= displayEnd) {
          const date = currentDate.getDate();
          const month = currentDate.getMonth();
          const year = currentDate.getFullYear();
          
          days.push({
            date,
            month,
            year,
            hasEvent: currentDate >= startDate && currentDate <= endDate,
            events: [],
            dateObj: new Date(currentDate)
          });
          
          currentDate.setDate(currentDate.getDate() + 1);
        }
        
        setCalendarDays(days);
        
        // Fetch trip plan (may not exist if trip not finalized)
        // Note: 404s are expected and handled silently - browser may still log them
        try {
          const plan = await tripsApi.getTripPlan(tripId);
          if (plan && typeof plan === 'object' && 'plan_json' in plan) {
            setTripPlan(plan);
            
            // Update calendar with events
            const planJson = (plan as any).plan_json;
            if (planJson?.days) {
              const updatedDays = days.map(day => {
                const planDay = planJson.days.find((d: any) => {
                  const planDate = new Date(d.date);
                  return planDate.toDateString() === day.dateObj.toDateString();
                });
                
                if (planDay && planDay.events && planDay.events.length > 0) {
                  return {
                    ...day,
                    hasEvent: true,
                    events: planDay.events.map((e: any) => e.title)
                  };
                }
                return day;
              });
              setCalendarDays(updatedDays);
            }
          }
        } catch (planError) {
          // Silently ignore - plan may not exist yet
        }
        
        // Fetch checklist for progress (may not exist if trip not finalized)
        // Note: 404s are expected and handled silently - browser may still log them
        try {
          const checklist = await tripsApi.getTripChecklist(tripId);
          if (checklist && typeof checklist === 'object' && 'checklist_json' in checklist) {
            const checklistJson = (checklist as any).checklist_json;
            const allItems: any[] = [
              ...(checklistJson.pre_trip || []),
              ...(checklistJson.packing || []),
              ...(checklistJson.documents || []),
              ...(checklistJson.during_trip || [])
            ];
            setChecklistProgress({
              completed: allItems.filter((item: any) => typeof item === 'object' && item.checked).length,
              total: allItems.length
            });
          }
        } catch (checklistError) {
          // Silently ignore - checklist may not exist yet
        }
      } catch (error) {
        console.error('Failed to fetch trip data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [tripId]);
  
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
        end: new Date(arrivalDate.getTime() + 30 * 60000)
      });
    }
    
    if (trip.selected_flight?.departure_time) {
      const departureDate = new Date(trip.selected_flight.departure_time);
      calendarEvents.push({
        title: `Departure from ${trip.selected_flight.departure_airport || 'Airport'}`,
        description: `Flight ${trip.selected_flight.airline || ''} ${trip.selected_flight.flight_number || ''}`,
        location: trip.selected_flight.departure_airport || undefined,
        start: departureDate,
        end: new Date(departureDate.getTime() + 30 * 60000)
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
            <h1 className="font-semibold">
              {isLoading ? 'Loading...' : trip ? `Trip to ${trip.to_city}` : 'Trip Calendar'}
            </h1>
            <p className="text-sm text-gray-500">
              {trip 
                ? `${new Date(trip.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${new Date(trip.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
                : 'Loading dates...'}
            </p>
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
                <p className="text-sm text-gray-600">
                  {checklistProgress.total > 0 
                    ? `${checklistProgress.completed} of ${checklistProgress.total} completed`
                    : 'Loading...'}
                </p>
              </div>
            </div>
            <div className="relative w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="absolute h-full bg-green-500 rounded-full" 
                style={{ 
                  width: checklistProgress.total > 0 
                    ? `${(checklistProgress.completed / checklistProgress.total) * 100}%` 
                    : '0%' 
                }} 
              />
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
          {isLoading ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading calendar...</p>
            </div>
          ) : (
            <>
              {/* Month Header */}
              {trip && calendarDays.length > 0 && (
                <div className="mb-4 text-center">
                  <h4 className="text-lg font-semibold text-gray-800">
                    {new Date(trip.start_date).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    {new Date(trip.start_date).getMonth() !== new Date(trip.end_date).getMonth() && (
                      <span> - {new Date(trip.end_date).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
                    )}
                  </h4>
                </div>
              )}
              
              <div className="mb-4">
                {/* Weekday headers */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="text-center text-xs font-semibold text-gray-600 py-2">
                      {day}
                    </div>
                  ))}
                </div>
                
                {/* Calendar grid */}
                <div className="grid grid-cols-7 gap-1">
                  {calendarDays.map((day, index) => {
                    // Skip placeholder days (date === 0)
                    if (day.date === 0 || !day.dateObj || day.dateObj.getTime() === 0) {
                      return <div key={`empty-${index}`} className="aspect-square min-h-[44px] rounded-lg" />;
                    }
                    
                    const isSelected = selectedDate !== null && 
                      selectedDate < calendarDays.length &&
                      calendarDays[selectedDate]?.dateObj &&
                      day.dateObj.toDateString() === calendarDays[selectedDate]?.dateObj?.toDateString();
                    const isTripDay = day.hasEvent;
                    
                    return (
              <button
                        key={`${day.date}-${day.month}-${day.year}-${index}`}
                onClick={() => {
                          if (isTripDay) {
                            setSelectedDate(index);
                            onDayClick(index);
                  }
                }}
                className={`
                          aspect-square rounded-lg flex flex-col items-center justify-center transition-all text-xs min-h-[44px] p-1
                          ${isTripDay 
                            ? isSelected
                              ? 'bg-green-500 text-white shadow-md'
                              : 'bg-green-100 text-green-700 hover:bg-green-200 border border-green-300'
                            : 'bg-gray-50 text-gray-400 hover:bg-gray-100'
                          }
                          ${isSelected ? 'ring-2 ring-green-500 ring-offset-1' : ''}
                          ${!isTripDay ? 'cursor-default' : 'cursor-pointer'}
                        `}
                      >
                        <span className="font-semibold text-sm">{day.date}</span>
                        {day.events && day.events.length > 0 && (
                          <span className="text-[8px] text-green-600 mt-0.5 font-medium">
                            {day.events.length}
                          </span>
                        )}
              </button>
                    );
                  })}
                </div>
          </div>

          {/* Export Button */}
          <Button 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                onClick={handleExportToCalendar}
                disabled={isLoading || !trip}
          >
            <CalendarIcon className="w-4 h-4 mr-2" />
            Export to Google Calendar
          </Button>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}