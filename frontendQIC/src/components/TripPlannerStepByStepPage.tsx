import { ArrowLeft, Check, Plane, Hotel, MapPin, Bell, ChevronRight, Settings } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';

interface TripPlannerStepByStepPageProps {
  onBack: () => void;
  tripData: any;
  onConfirm: (selectedOptions: any) => void;
  onNotifications?: () => void;
}

type Step = 'tickets' | 'hotels' | 'activities' | 'confirmation';

export function TripPlannerStepByStepPage({ onBack, tripData, onConfirm, onNotifications }: TripPlannerStepByStepPageProps) {
  const [currentStep, setCurrentStep] = useState<Step>('tickets');
  const [selectedFlight, setSelectedFlight] = useState<number | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<number | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<number[]>([]);
  
  // Flight preferences
  const [showFlightPreferences, setShowFlightPreferences] = useState(false);
  const [flightClass, setFlightClass] = useState('economy');
  const [flightTransit, setFlightTransit] = useState('any');
  const [flightLuggage, setFlightLuggage] = useState('standard');
  const [flightCabinLuggage, setFlightCabinLuggage] = useState('1-bag');
  
  // Hotel preferences
  const [showHotelPreferences, setShowHotelPreferences] = useState(false);
  const [hotelLocation, setHotelLocation] = useState('any');
  const [hotelNotes, setHotelNotes] = useState('');

  const flightOptions = [
    { 
      id: 1, 
      airline: 'Emirates', 
      price: '$450', 
      time: '10:30 AM - 2:45 PM', 
      duration: '4h 15m', 
      stops: 'Direct', 
      class: 'Economy',
      pros: ['Direct flight', 'Great timing', 'Premium airline'],
      cons: []
    },
    { 
      id: 2, 
      airline: 'Qatar Airways', 
      price: '$520', 
      time: '2:15 PM - 6:30 PM', 
      duration: '4h 15m', 
      stops: 'Direct', 
      class: 'Economy',
      pros: ['Direct flight', 'Award-winning service'],
      cons: ['Higher price']
    },
    { 
      id: 3, 
      airline: 'FlyDubai', 
      price: '$380', 
      time: '6:00 AM - 10:15 AM', 
      duration: '4h 15m', 
      stops: '1 Stop', 
      class: 'Economy',
      pros: ['Best price', 'Morning arrival'],
      cons: ['One stop', 'Early departure']
    },
    { 
      id: 4, 
      airline: 'Emirates Business', 
      price: '$1250', 
      time: '11:00 AM - 3:15 PM', 
      duration: '4h 15m', 
      stops: 'Direct', 
      class: 'Business',
      pros: ['Business class', 'Direct flight', 'Luxury service'],
      cons: ['Premium price']
    }
  ];

  const hotelOptions = [
    { 
      id: 1, 
      name: 'Luxury Resort & Spa', 
      price: '$250/night', 
      rating: 4.8, 
      amenities: ['Pool', 'Spa', 'Restaurant', 'Beach Access'],
      image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&q=80',
      location: 'Downtown',
      pros: ['Best rating', 'Beach access', 'Full spa'],
      cons: ['Higher price']
    },
    { 
      id: 3, 
      name: 'Boutique Hotel', 
      price: '$180/night', 
      rating: 4.7, 
      amenities: ['Rooftop', 'Bar', 'WiFi', 'Concierge'],
      image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400&q=80',
      location: 'Old Town',
      pros: ['Great value', 'Historic area', 'Rooftop bar'],
      cons: []
    },
    { 
      id: 2, 
      name: 'City Center Hotel', 
      price: '$150/night', 
      rating: 4.5, 
      amenities: ['Gym', 'WiFi', 'Breakfast', 'Parking'],
      image: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400&q=80',
      location: 'City Center',
      pros: ['Best price', 'Central location', 'Free breakfast'],
      cons: ['Basic amenities']
    }
  ];

  const activityOptions = [
    { 
      id: 1, 
      name: 'Desert Safari', 
      price: '$80', 
      duration: '6 hours', 
      image: 'https://images.unsplash.com/photo-1451337516015-6b6e9a44a8a3?w=400&q=80',
      description: 'Experience dune bashing and camel riding',
      pros: ['Must-see experience', 'Sunset views', 'Traditional dinner'],
      cons: []
    },
    { 
      id: 3, 
      name: 'Burj Khalifa Visit', 
      price: '$60', 
      duration: '2 hours',
      image: 'https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?w=400&q=80',
      description: 'Visit the worlds tallest building',
      pros: ['Iconic landmark', 'Amazing views', 'Quick visit'],
      cons: []
    },
    { 
      id: 4, 
      name: 'Marina Dinner Cruise', 
      price: '$100', 
      duration: '3 hours',
      image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&q=80',
      description: 'Luxury dining on the water',
      pros: ['Romantic setting', 'Live entertainment', 'Premium dining'],
      cons: ['Higher price']
    },
    { 
      id: 6, 
      name: 'Water Park Day', 
      price: '$70', 
      duration: 'Full day',
      image: 'https://images.unsplash.com/photo-1525268771113-32d9e9021a97?w=400&q=80',
      description: 'Thrilling water slides and attractions',
      pros: ['Family-friendly', 'All-day fun', 'Beat the heat'],
      cons: ['Full day required']
    },
    { 
      id: 2, 
      name: 'City Tour', 
      price: '$50', 
      duration: '4 hours',
      image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400&q=80',
      description: 'Explore major landmarks and attractions',
      pros: ['Budget-friendly', 'Comprehensive overview'],
      cons: ['Basic tour']
    },
    { 
      id: 5, 
      name: 'Shopping Tour', 
      price: '$40', 
      duration: '5 hours',
      image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80',
      description: 'Visit premium malls and souks',
      pros: ['Best shopping deals', 'Local markets'],
      cons: ['Long duration']
    }
  ];

  const toggleActivity = (id: number) => {
    setSelectedActivities(prev =>
      prev.includes(id) ? prev.filter(actId => actId !== id) : [...prev, id]
    );
  };

  const handleNext = () => {
    if (currentStep === 'tickets' && selectedFlight) {
      setCurrentStep('hotels');
    } else if (currentStep === 'hotels' && selectedHotel) {
      setCurrentStep('activities');
    } else if (currentStep === 'activities' && selectedActivities.length > 0) {
      setCurrentStep('confirmation');
    }
  };

  const handleConfirm = () => {
    onConfirm({
      flight: flightOptions.find(f => f.id === selectedFlight),
      hotel: hotelOptions.find(h => h.id === selectedHotel),
      activities: activityOptions.filter(a => selectedActivities.includes(a.id))
    });
  };

  const getStepNumber = (step: Step) => {
    const steps = ['tickets', 'hotels', 'activities', 'confirmation'];
    return steps.indexOf(step) + 1;
  };

  const getProgressPercentage = () => {
    return (getStepNumber(currentStep) / 4) * 100;
  };

  const canProceed = () => {
    if (currentStep === 'tickets') return selectedFlight !== null;
    if (currentStep === 'hotels') return selectedHotel !== null;
    if (currentStep === 'activities') return selectedActivities.length > 0;
    return true;
  };

  const totalCost = () => {
    let total = 0;
    if (selectedFlight) {
      const flight = flightOptions.find(f => f.id === selectedFlight);
      total += parseFloat(flight?.price.replace('$', '') || '0');
    }
    if (selectedHotel) {
      const hotel = hotelOptions.find(h => h.id === selectedHotel);
      const nights = 7; // Assume 7 nights
      total += parseFloat(hotel?.price.replace('$', '').replace('/night', '') || '0') * nights;
    }
    selectedActivities.forEach(actId => {
      const activity = activityOptions.find(a => a.id === actId);
      total += parseFloat(activity?.price.replace('$', '') || '0');
    });
    return total;
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button
            onClick={currentStep === 'tickets' ? onBack : () => {
              const steps: Step[] = ['tickets', 'hotels', 'activities', 'confirmation'];
              const currentIndex = steps.indexOf(currentStep);
              if (currentIndex > 0) {
                setCurrentStep(steps[currentIndex - 1]);
              }
            }}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-semibold">
              {currentStep === 'tickets' && 'Select Flight'}
              {currentStep === 'hotels' && 'Choose Hotel'}
              {currentStep === 'activities' && 'Pick Activities'}
              {currentStep === 'confirmation' && 'Confirm Booking'}
            </h1>
            <p className="text-sm text-gray-500">Step {getStepNumber(currentStep)} of 4</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4">
          <Progress value={getProgressPercentage()} className="h-2" />
        </div>

        {/* Step Indicators */}
        <div className="flex justify-between mt-4">
          {['Tickets', 'Hotels', 'Activities', 'Confirm'].map((label, index) => {
            const stepNames: Step[] = ['tickets', 'hotels', 'activities', 'confirmation'];
            const stepName = stepNames[index];
            const isActive = currentStep === stepName;
            const isPast = getStepNumber(currentStep) > index + 1;
            
            return (
              <div key={label} className="flex flex-col items-center flex-1">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 ${
                  isPast ? 'bg-green-500 text-white' :
                  isActive ? 'bg-blue-600 text-white' : 
                  'bg-gray-200 text-gray-500'
                }`}>
                  {isPast ? <Check className="w-4 h-4" /> : index + 1}
                </div>
                <span className={`text-xs ${isActive ? 'font-semibold' : 'text-gray-500'}`}>
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {/* Tickets Step */}
        {currentStep === 'tickets' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600">Choose your preferred flight option</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFlightPreferences(!showFlightPreferences)}
                className="flex items-center gap-1"
              >
                <Settings className="w-4 h-4" />
                Preferences
              </Button>
            </div>

            {/* Flight Preferences Collapsible */}
            {showFlightPreferences && (
              <Card className="p-4 mb-3">
                <h3 className="font-semibold text-sm mb-3">Flight Preferences (Optional)</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Class</label>
                    <Select value={flightClass} onValueChange={setFlightClass}>
                      <SelectTrigger className="text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="economy">Economy</SelectItem>
                        <SelectItem value="premium-economy">Premium Economy</SelectItem>
                        <SelectItem value="business">Business</SelectItem>
                        <SelectItem value="first">First Class</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Flight Type</label>
                    <Select value={flightTransit} onValueChange={setFlightTransit}>
                      <SelectTrigger className="text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="any">Any</SelectItem>
                        <SelectItem value="direct">Direct only</SelectItem>
                        <SelectItem value="transit">Transit OK</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Checked Luggage</label>
                    <Select value={flightLuggage} onValueChange={setFlightLuggage}>
                      <SelectTrigger className="text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">No checked luggage</SelectItem>
                        <SelectItem value="standard">Standard (1 bag)</SelectItem>
                        <SelectItem value="extra">Extra (2+ bags)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Cabin Luggage</label>
                    <Select value={flightCabinLuggage} onValueChange={setFlightCabinLuggage}>
                      <SelectTrigger className="text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1-bag">1 bag</SelectItem>
                        <SelectItem value="2-bags">2 bags</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </Card>
            )}

            {flightOptions.map((flight) => (
              <Card
                key={flight.id}
                onClick={() => setSelectedFlight(flight.id)}
                className={`p-4 cursor-pointer transition-all ${
                  selectedFlight === flight.id
                    ? 'border-2 border-blue-600 bg-blue-50'
                    : 'border hover:border-blue-200'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <Plane className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-semibold">{flight.airline}</p>
                      <p className="text-xs text-gray-500">{flight.class}</p>
                    </div>
                  </div>
                  {selectedFlight === flight.id && (
                    <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-600">{flight.time}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{flight.duration}</span>
                    <span>•</span>
                    <span>{flight.stops}</span>
                  </div>
                </div>
                {(flight.pros.length > 0 || flight.cons.length > 0) && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {flight.pros.map((pro, idx) => (
                      <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-2 py-0 h-5">
                        {pro}
                      </Badge>
                    ))}
                    {flight.cons.map((con, idx) => (
                      <Badge key={`con-${idx}`} className="bg-red-100 text-red-700 border-red-300 text-xs px-2 py-0 h-5">
                        {con}
                      </Badge>
                    ))}
                  </div>
                )}
                <div className="mt-3 pt-3 border-t flex items-center justify-between">
                  <span className="text-lg font-semibold text-blue-600">{flight.price}</span>
                  <span className="text-xs text-gray-500">per person</span>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Hotels Step */}
        {currentStep === 'hotels' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600">Select your accommodation</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowHotelPreferences(!showHotelPreferences)}
                className="flex items-center gap-1"
              >
                <Settings className="w-4 h-4" />
                Preferences
              </Button>
            </div>

            {/* Hotel Preferences Collapsible */}
            {showHotelPreferences && (
              <Card className="p-4 mb-3">
                <h3 className="font-semibold text-sm mb-3">Hotel Preferences (Optional)</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Location</label>
                    <Select value={hotelLocation} onValueChange={setHotelLocation}>
                      <SelectTrigger className="text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="any">Any</SelectItem>
                        <SelectItem value="district">Specific District</SelectItem>
                        <SelectItem value="nature">Near to Nature</SelectItem>
                        <SelectItem value="city-center">City Center</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold mb-1 block">Additional Notes</label>
                    <Textarea
                      value={hotelNotes}
                      onChange={(e) => setHotelNotes(e.target.value)}
                      placeholder="e.g., near shopping area, quiet neighborhood..."
                      className="text-sm resize-none"
                      rows={2}
                    />
                  </div>
                </div>
              </Card>
            )}

            {hotelOptions.map((hotel) => (
              <Card
                key={hotel.id}
                onClick={() => setSelectedHotel(hotel.id)}
                className={`overflow-hidden cursor-pointer transition-all ${
                  selectedHotel === hotel.id
                    ? 'border-2 border-purple-600 bg-purple-50'
                    : 'border hover:border-purple-200'
                }`}
              >
                <div className="flex gap-3 p-3">
                  <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200">
                    <img src={hotel.image} alt={hotel.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <p className="font-semibold text-sm mb-1">{hotel.name}</p>
                        <div className="flex items-center gap-1 mb-2">
                          <span className="text-xs">⭐</span>
                          <span className="text-xs font-semibold">{hotel.rating}</span>
                          <span className="text-xs text-gray-500">• {hotel.location}</span>
                        </div>
                      </div>
                      {selectedHotel === hotel.id && (
                        <div className="w-5 h-5 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </div>
                    <div className="flex gap-1 flex-wrap mb-2">
                      {hotel.amenities.slice(0, 3).map((amenity, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs px-1.5 py-0 h-5">
                          {amenity}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {hotel.pros.map((pro, idx) => (
                        <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-1.5 py-0 h-5">
                          {pro}
                        </Badge>
                      ))}
                      {hotel.cons.map((con, idx) => (
                        <Badge key={`con-${idx}`} className="bg-red-100 text-red-700 border-red-300 text-xs px-1.5 py-0 h-5">
                          {con}
                        </Badge>
                      ))}
                    </div>
                    <p className="font-semibold text-sm text-purple-600">{hotel.price}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Activities Step */}
        {currentStep === 'activities' && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600 mb-4">Choose activities (select multiple)</p>
            {activityOptions.map((activity) => (
              <Card
                key={activity.id}
                onClick={() => toggleActivity(activity.id)}
                className={`overflow-hidden cursor-pointer transition-all ${
                  selectedActivities.includes(activity.id)
                    ? 'border-2 border-green-600 bg-green-50'
                    : 'border hover:border-green-200'
                }`}
              >
                <div className="flex gap-3 p-3">
                  <div className="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200">
                    <img src={activity.image} alt={activity.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <p className="font-semibold text-sm mb-1">{activity.name}</p>
                        <p className="text-xs text-gray-600 mb-2">{activity.description}</p>
                        <p className="text-xs text-gray-500 mb-2">{activity.duration}</p>
                        <div className="flex flex-wrap gap-1">
                          {activity.pros.map((pro, idx) => (
                            <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-1.5 py-0 h-5">
                              {pro}
                            </Badge>
                          ))}
                          {activity.cons.map((con, idx) => (
                            <Badge key={`con-${idx}`} className="bg-red-100 text-red-700 border-red-300 text-xs px-1.5 py-0 h-5">
                              {con}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      {selectedActivities.includes(activity.id) && (
                        <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </div>
                    <p className="font-semibold text-sm text-green-600 mt-2">{activity.price}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Confirmation Step */}
        {currentStep === 'confirmation' && (
          <div className="space-y-4">
            <h2 className="font-semibold text-lg mb-4">Review Your Trip</h2>
            
            {/* Selected Flight */}
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Plane className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold">Flight</h3>
              </div>
              {selectedFlight && (() => {
                const flight = flightOptions.find(f => f.id === selectedFlight);
                return flight ? (
                  <div>
                    <p className="font-semibold">{flight.airline}</p>
                    <p className="text-sm text-gray-600">{flight.time}</p>
                    <p className="text-sm text-gray-500">{flight.duration} • {flight.stops}</p>
                    <p className="font-semibold text-blue-600 mt-2">{flight.price}</p>
                  </div>
                ) : null;
              })()}
            </Card>

            {/* Selected Hotel */}
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Hotel className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold">Hotel</h3>
              </div>
              {selectedHotel && (() => {
                const hotel = hotelOptions.find(h => h.id === selectedHotel);
                return hotel ? (
                  <div>
                    <p className="font-semibold">{hotel.name}</p>
                    <p className="text-sm text-gray-600">⭐ {hotel.rating} • {hotel.location}</p>
                    <div className="flex gap-1 flex-wrap mt-2">
                      {hotel.amenities.map((amenity, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {amenity}
                        </Badge>
                      ))}
                    </div>
                    <p className="font-semibold text-purple-600 mt-2">{hotel.price}</p>
                  </div>
                ) : null;
              })()}
            </Card>

            {/* Selected Activities */}
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <MapPin className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold">Activities ({selectedActivities.length})</h3>
              </div>
              <div className="space-y-2">
                {selectedActivities.map(actId => {
                  const activity = activityOptions.find(a => a.id === actId);
                  return activity ? (
                    <div key={actId} className="flex items-center justify-between py-2 border-b last:border-0">
                      <div>
                        <p className="font-semibold text-sm">{activity.name}</p>
                        <p className="text-xs text-gray-500">{activity.duration}</p>
                      </div>
                      <p className="font-semibold text-sm text-green-600">{activity.price}</p>
                    </div>
                  ) : null;
                })}
              </div>
            </Card>

            {/* Total Cost */}
            <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Estimated Total Cost</p>
                  <p className="text-xs text-gray-500 mt-1">Per person</p>
                </div>
                <p className="text-2xl font-semibold text-blue-600">${totalCost()}</p>
              </div>
            </Card>
          </div>
        )}
      </div>

      {/* Bottom Action Button */}
      <div className="sticky bottom-0 bg-white border-t p-4">
        <div className="flex gap-2">
          {currentStep !== 'confirmation' && (
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 h-12"
            >
              Continue
              <ChevronRight className="w-5 h-5 ml-1" />
            </Button>
          )}
          {currentStep === 'confirmation' && (
            <Button
              onClick={handleConfirm}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 h-12"
            >
              Confirm & Create Trip
            </Button>
          )}
        </div>
        {!canProceed() && (
          <p className="text-xs text-center text-gray-500 mt-2">
            Please make a selection to continue
          </p>
        )}
      </div>
    </div>
  );
}
