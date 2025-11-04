import { ArrowLeft, Check, Plane, Hotel, MapPin, Bell, ChevronRight, Settings } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { flightsApi, hotelsApi, entertainmentApi, tripsApi } from '../utils/api';
import { LoadingGame } from './LoadingGame';

interface TripPlannerStepByStepPageProps {
  onBack: () => void;
  tripData: any;
  onConfirm: (selectedOptions: any) => void;
  onNotifications?: () => void;
}

type Step = 'tickets' | 'hotels' | 'activities' | 'confirmation';

export function TripPlannerStepByStepPage({ onBack, tripData, onConfirm, onNotifications }: TripPlannerStepByStepPageProps) {
  const [currentStep, setCurrentStep] = useState<Step>('tickets');
  const [selectedFlight, setSelectedFlight] = useState<string | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<string | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);
  
  // API data
  const [flightOptions, setFlightOptions] = useState<any[]>([]);
  const [hotelOptions, setHotelOptions] = useState<any[]>([]);
  const [activityOptions, setActivityOptions] = useState<any[]>([]);
  const [isLoadingFlights, setIsLoadingFlights] = useState(false);
  const [isLoadingHotels, setIsLoadingHotels] = useState(false);
  const [isLoadingActivities, setIsLoadingActivities] = useState(false);
  const [isSavingSelections, setIsSavingSelections] = useState(false);
  
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

  const toggleActivity = (id: string) => {
    setSelectedActivities(prev =>
      prev.includes(id) ? prev.filter(actId => actId !== id) : [...prev, id]
    );
  };

  // Fetch flight data when component mounts
  useEffect(() => {
    if (currentStep === 'tickets' && tripData?.id) {
      fetchFlightOptions();
    }
  }, [currentStep, tripData?.id]);

  // Fetch hotel data when step changes
  useEffect(() => {
    if (currentStep === 'hotels' && tripData?.id) {
      fetchHotelOptions();
    }
  }, [currentStep, tripData?.id]);

  // Fetch activity data when step changes
  useEffect(() => {
    if (currentStep === 'activities' && tripData?.id) {
      fetchActivityOptions();
    }
  }, [currentStep, tripData?.id]);

  const fetchFlightOptions = async () => {
    if (!tripData?.id || isLoadingFlights) return;
    setIsLoadingFlights(true);
    try {
      // Search flights using SerpAPI
      const searchResult: any = await flightsApi.searchFlights({
        trip_id: tripData.id
      });

      const flights = searchResult.flights || [];
      
      // Transform to UI format
      const formattedFlights = flights.map((flight: any) => {
        const allLegs = flight.legs || [];
        if (allLegs.length === 0) return null;
        
        const firstLeg = allLegs[0];
        const lastLeg = allLegs[allLegs.length - 1];
        
        // Determine if this is a round trip by checking if we return to origin
        // Round trip: first departs from origin, last arrives at origin
        const originIata = firstLeg.dep_iata;
        const destinationIata = lastLeg.arr_iata;
        const isRoundTrip = firstLeg && lastLeg && 
          lastLeg.arr_iata === originIata && 
          destinationIata !== originIata;
        
        // Separate outbound and return legs
        // Outbound: legs that go from origin to destination
        // Return: legs that go from destination back to origin
        let outboundLegs: any[] = [];
        let returnLegs: any[] = [];
        
        if (isRoundTrip) {
          // Find the transition point where we start returning
          let foundReturn = false;
          for (let i = 0; i < allLegs.length; i++) {
            const leg = allLegs[i];
            // Check if this leg departs from destination (means we're returning)
            if (leg.dep_iata === destinationIata && leg.arr_iata === originIata) {
              foundReturn = true;
            }
            if (foundReturn) {
              returnLegs.push(leg);
            } else {
              outboundLegs.push(leg);
            }
          }
          
          // Alternative: if we didn't find return by transition, check all legs
          if (returnLegs.length === 0) {
            returnLegs = allLegs.filter((leg: any) => 
              leg.dep_iata === destinationIata && leg.arr_iata === originIata
            );
            outboundLegs = allLegs.filter((leg: any) => 
              !returnLegs.includes(leg)
            );
          }
        } else {
          // One-way flight - all legs are outbound
          outboundLegs = allLegs;
        }
        
        // Use outbound legs for main flight info
        const outboundFirstLeg = outboundLegs[0];
        const outboundLastLeg = outboundLegs[outboundLegs.length - 1];
        
        // Extract outbound flight details with dates
        const outboundDepDate = outboundFirstLeg ? new Date(outboundFirstLeg.dep_time) : null;
        const outboundArrDate = outboundLastLeg ? new Date(outboundLastLeg.arr_time) : null;
        
        const depTime = outboundDepDate ? outboundDepDate.toLocaleString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        }) : '';
        const arrTime = outboundArrDate ? outboundArrDate.toLocaleString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        }) : '';
        
        const depDate = outboundDepDate ? outboundDepDate.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }) : '';
        
        const arrDate = outboundArrDate ? outboundArrDate.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }) : '';
        
        // Extract city information for outbound
        const depCity = outboundFirstLeg?.dep_city || outboundFirstLeg?.dep_name || outboundFirstLeg?.dep_iata || 'Unknown';
        const arrCity = outboundLastLeg?.arr_city || outboundLastLeg?.arr_name || outboundLastLeg?.arr_iata || 'Unknown';
        const depAirport = outboundFirstLeg?.dep_iata || '';
        const arrAirport = outboundLastLeg?.arr_iata || '';
        
        // Calculate outbound duration
        const outboundDurationHrs = Math.floor(flight.total_duration_min / 60);
        const outboundDurationMins = flight.total_duration_min % 60;
        const durationStr = `${outboundDurationHrs}h ${outboundDurationMins}m`;
        const stopsStr = flight.stops === 0 
          ? 'Direct' 
          : `${flight.stops} Stop${flight.stops > 1 ? 's' : ''}`;
        
        // For round trip, extract return flight details
        let returnDepTime = '';
        let returnArrTime = '';
        let returnDepDate = '';
        let returnArrDate = '';
        let returnDuration = '';
        let returnStops = '';
        let returnAirline = '';
        let returnDepCity = '';
        let returnArrCity = '';
        let returnDepAirport = '';
        let returnArrAirport = '';
        
        if (isRoundTrip && returnLegs.length > 0) {
          const firstReturnLeg = returnLegs[0];
          const lastReturnLeg = returnLegs[returnLegs.length - 1];
          
          const returnDepDateObj = new Date(firstReturnLeg.dep_time);
          const returnArrDateObj = new Date(lastReturnLeg.arr_time);
          
          returnDepTime = returnDepDateObj.toLocaleString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          });
          returnArrTime = returnArrDateObj.toLocaleString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          });
          
          returnDepDate = returnDepDateObj.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          });
          
          returnArrDate = returnArrDateObj.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          });
          
          // Extract return city information
          returnDepCity = firstReturnLeg?.dep_city || firstReturnLeg?.dep_name || firstReturnLeg?.dep_iata || 'Unknown';
          returnArrCity = lastReturnLeg?.arr_city || lastReturnLeg?.arr_name || lastReturnLeg?.arr_iata || 'Unknown';
          returnDepAirport = firstReturnLeg?.dep_iata || '';
          returnArrAirport = lastReturnLeg?.arr_iata || '';
          
          // Calculate return duration
          const returnDurationMin = Math.floor(
            (returnArrDateObj.getTime() - returnDepDateObj.getTime()) / 60000
          );
          const returnDurationHrs = Math.floor(returnDurationMin / 60);
          const returnDurationMins = returnDurationMin % 60;
          returnDuration = `${returnDurationHrs}h ${returnDurationMins}m`;
          
          // Calculate return stops (number of legs - 1)
          returnStops = returnLegs.length === 1 
            ? 'Direct' 
            : `${returnLegs.length - 1} Stop${returnLegs.length - 1 > 1 ? 's' : ''}`;
          
          // Get return airline
          returnAirline = firstReturnLeg?.marketing || 'Unknown';
        }
        
        return {
          id: flight.id,
          airline: outboundFirstLeg?.marketing || 'Unknown',
          price: `$${flight.price?.amount || 0}`,
          time: `${depTime} - ${arrTime}`,
          duration: durationStr,
          stops: stopsStr,
          class: 'Economy', // Default class
          rawFlight: flight, // Keep for ranking
          google_flights_url: flight.google_flights_url,
          isRoundTrip,
          // Outbound city info
          depCity,
          arrCity,
          depAirport,
          arrAirport,
          // Outbound dates
          depDate,
          arrDate,
          // Return flight info
          returnTime: returnDepTime && returnArrTime ? `${returnDepTime} - ${returnArrTime}` : null,
          returnDepDate: returnDepDate || null,
          returnArrDate: returnArrDate || null,
          returnDuration: returnDuration || null,
          returnStops: returnStops || null,
          returnAirline: returnAirline || null,
          returnDepTime: returnDepTime || null,
          returnArrTime: returnArrTime || null,
          returnDepCity: returnDepCity || null,
          returnArrCity: returnArrCity || null,
          returnDepAirport: returnDepAirport || null,
          returnArrAirport: returnArrAirport || null
        };
      }).filter((f: any) => f !== null); // Filter out null entries

      // Rank flights with AI if we have flights
      if (formattedFlights.length > 0) {
        try {
          const ranked: any = await flightsApi.rankFlights({
            search_id: searchResult.search_id,
            preferences_prompt: buildFlightPreferences(),
            flights: flights
          });
          
          const rankedFlights = ranked.items.map((item: any) => {
            const original = formattedFlights.find((f: any) => f.id === item.id);
            return {
              ...original,
              score: item.score,
              aiPros: item.pros_keywords,
              aiCons: item.cons_keywords
            };
          });
          
          setFlightOptions(rankedFlights);
        } catch (error) {
          console.error('Flight ranking failed, using unranked:', error);
          setFlightOptions(formattedFlights);
        }
      } else {
        setFlightOptions(formattedFlights);
      }
    } catch (error) {
      console.error('Failed to fetch flights:', error);
      setFlightOptions([]);
    } finally {
      setIsLoadingFlights(false);
    }
  };

  const buildFlightPreferences = (): string => {
    let pref = '';
    if (flightTransit !== 'any') {
      pref += `Prefer ${flightTransit} flights. `;
    }
    if (flightClass !== 'economy') {
      pref += `Prefer ${flightClass}. `;
    }
    return pref || 'Good value for money with reasonable comfort.';
  };

  const fetchHotelOptions = async () => {
    if (!tripData?.id || isLoadingHotels) return;
    setIsLoadingHotels(true);
    try {
      const toCity = tripData?.to_city || tripData?.toCity || 'Bali';
      const startDate = new Date(tripData?.start_date || tripData?.startDate);
      const endDate = new Date(tripData?.end_date || tripData?.endDate);
      
      const searchQuery = {
        q: `Hotels in ${toCity}`,
        check_in_date: startDate.toISOString().split('T')[0],
        check_out_date: endDate.toISOString().split('T')[0],
        adults: tripData?.adults || 2,
        currency: 'USD'
      };

      const searchResult: any = await hotelsApi.searchHotels(searchQuery);
      
      // Transform SerpApi results to our format
      const hotels = transformHotelResults(searchResult.data);
      
      // Rank hotels with AI
      const ranked: any = await hotelsApi.rankHotels({
        search_id: `hotel_search_${tripData.id}`,
        preferences_prompt: buildHotelPreferences(),
        hotels: hotels
      });
      
      const formatted = ranked.items.map((item: any) => {
        const original = hotels.find((h: any) => h.id === item.id);
        return {
          ...original,
          score: item.score,
          aiPros: item.pros_keywords,
          aiCons: item.cons_keywords
        };
      });
      
      setHotelOptions(formatted.slice(0, 10)); // Limit to 10
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
      setHotelOptions([]);
    } finally {
      setIsLoadingHotels(false);
    }
  };

  const transformHotelResults = (data: any): any[] => {
    const hotels = data?.properties || [];
    return hotels.map((hotel: any, idx: number) => {
      // Convert price fields to numbers and ensure they're valid
      const parsePrice = (price: any): number => {
        if (typeof price === 'number') return price;
        if (typeof price === 'string') {
          // Remove currency symbols and parse
          const cleaned = price.replace(/[^0-9.]/g, '');
          const parsed = parseFloat(cleaned);
          return isNaN(parsed) ? 0 : parsed;
        }
        return 0;
      };

      // Ensure numeric values are within valid ranges
      const rating = hotel.overall_rating ? Math.max(0, Math.min(5, parseFloat(hotel.overall_rating))) : null;
      const reviewsCount = hotel.reviews ? Math.max(0, parseInt(hotel.reviews)) : 0;

      // Try various ID fields that SerpApi might use
      const hotelId = String(
        hotel.property_token || 
        hotel.gmid || 
        hotel.data_id || 
        hotel.data_cid || 
        `hotel_${idx}`
      );
      
      // Get first image thumbnail if available
      const firstImage = Array.isArray(hotel.images) && hotel.images.length > 0 
        ? hotel.images[0].thumbnail 
        : null;
      
      return {
        id: hotelId,
        name: String(hotel.name || 'Unknown Hotel'),
        location: String(hotel.gps_coordinates?.latitude && hotel.gps_coordinates?.longitude 
          ? `${hotel.gps_coordinates.latitude.toFixed(4)}, ${hotel.gps_coordinates.longitude.toFixed(4)}`
          : 'Location not available'),
        price_per_night: parsePrice(hotel.rate_per_night?.extracted_lowest || hotel.rate_per_night?.lowest || 0),
        total_price: parsePrice(hotel.total_rate?.extracted_lowest || hotel.total_rate?.lowest || 0),
        currency: 'USD',
        rating: rating,
        reviews_count: reviewsCount,
        hotel_class: null, // Not provided by SerpApi
        amenities: Array.isArray(hotel.amenities) ? hotel.amenities : [],
        free_cancellation: null, // Not reliably provided
        thumbnail: firstImage
      };
    });
  };

  const buildHotelPreferences = (): string => {
    let pref = '';
    if (hotelNotes) {
      pref += hotelNotes + '. ';
    }
    if (hotelLocation !== 'any') {
      pref += `Prefer ${hotelLocation}. `;
    }
    return pref || 'Good location with essential amenities and value for money.';
  };

  const fetchActivityOptions = async () => {
    if (!tripData?.id || isLoadingActivities) return;
    setIsLoadingActivities(true);
    try {
      const toCity = tripData?.to_city || tripData?.toCity || 'Bali';
      
      const searchResult: any = await entertainmentApi.searchVenues({
        trip_id: tripData.id,
        destination: toCity
      });
      
      const venues = searchResult.venues || [];
      
      console.log('🎭 Found venues:', venues.length);
      if (venues.length > 0) {
        console.log('📋 Sample venue:', venues[0]);
      }
      
      // Rank venues with AI
      const ranked: any = await entertainmentApi.rankVenues({
        trip_id: tripData.id,
        search_id: searchResult.search_id,
        venues: venues
      });
      
      console.log('🏆 Ranked items:', ranked.items.length);
      if (ranked.items.length > 0) {
        console.log('📋 Sample ranked item:', ranked.items[0]);
      }
      
      const formatted = ranked.items.map((item: any) => {
        const original = venues.find((v: any) => v.place_id === item.place_id);
        if (!original) {
          console.log('⚠️  Could not find venue for place_id:', item.place_id);
        }
        return {
          id: item.place_id,
          name: original?.title || 'Unknown',
          description: original?.description || '',
          duration: '2-4 hours',
          price: original?.price || 'Price varies',
          rating: original?.rating || 0,
          reviews: original?.reviews || 0,
          thumbnail: original?.thumbnail,
          address: original?.address,
          type: original?.type,
          score: item.score,
          aiPros: item.pros_keywords,
          aiCons: item.cons_keywords
        };
      });
      
      console.log('✅ Formatted activities:', formatted.length);
      if (formatted.length > 0) {
        console.log('📋 Sample formatted:', formatted[0]);
      }
      
      setActivityOptions(formatted.slice(0, 20)); // Limit to 20
    } catch (error) {
      console.error('Failed to fetch activities:', error);
      setActivityOptions([]);
    } finally {
      setIsLoadingActivities(false);
    }
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

  const handleConfirm = async () => {
    setIsSavingSelections(true);
    try {
      // Save flight selection
      if (selectedFlight) {
        const flight = flightOptions.find(f => f.id === selectedFlight);
        if (flight) {
          const startDate = new Date(tripData?.start_date || tripData?.startDate);
          await flightsApi.selectFlight({
            trip_id: tripData.id,
            flight_id: flight.id,
            airline: flight.airline,
            flight_number: 'TBD',
            departure_airport: tripData?.from_city || tripData?.fromCity,
            arrival_airport: tripData?.to_city || tripData?.toCity,
            departure_time: startDate.toISOString(),
            arrival_time: new Date(startDate.getTime() + 255 * 60000).toISOString(),
            price: parseFloat(flight.price.replace('$', '')),
            currency: 'USD',
            total_duration_min: 255,
            stops: flight.stops === 'Direct' ? 0 : 1,
            title: flight.airline
          });
        }
      }

      // Save hotel selection
      if (selectedHotel) {
        const hotel = hotelOptions.find(h => h.id === selectedHotel);
        if (hotel) {
          const startDate = new Date(tripData?.start_date || tripData?.startDate);
          const endDate = new Date(tripData?.end_date || tripData?.endDate);
          await hotelsApi.selectHotel({
            trip_id: tripData.id,
            hotel_id: hotel.id,
            hotel_name: hotel.name,
            location: hotel.location,
            price_per_night: hotel.price_per_night,
            total_price: hotel.total_price,
            currency: hotel.currency || 'USD',
            check_in_date: startDate.toISOString().split('T')[0],
            check_out_date: endDate.toISOString().split('T')[0],
            rating: hotel.rating,
            reviews_count: hotel.reviews_count,
            hotel_class: hotel.hotel_class,
            amenities: hotel.amenities,
            free_cancellation: hotel.free_cancellation,
            title: hotel.name
          });
        }
      }

      // Save entertainment selections
      if (selectedActivities.length > 0) {
        const activities = activityOptions.filter(a => selectedActivities.includes(a.id));
        const selections = activities.map(activity => ({
          venue: {
            place_id: activity.id,
            title: activity.name,
            type: activity.type,
            address: activity.address,
            rating: activity.rating,
            reviews: activity.reviews,
            price: activity.price,
            gps_coordinates: undefined,
            thumbnail: activity.thumbnail
          },
          ranking: {
            score: activity.score,
            title: activity.name,
            pros_keywords: activity.aiPros || activity.pros || [],
            cons_keywords: activity.aiCons || activity.cons || []
          }
        }));
        
        await entertainmentApi.selectVenues({
          trip_id: tripData.id,
          selections
        });
      }

      // Finalize trip to generate AI plan and checklist
      // This MUST happen after all selections are saved
      console.log('Finalizing trip to generate AI plan and checklist...');
      try {
        const finalizedTrip = await tripsApi.finalizeTrip(tripData.id);
        console.log('Trip finalized successfully:', finalizedTrip);
        console.log('AI plan and checklist have been generated');
      } catch (finalizeError: any) {
        console.error('Failed to finalize trip:', finalizeError);
        // Show error but still proceed - user can manually finalize later
        const errorMessage = finalizeError?.message || 'Failed to generate trip plan';
        alert(`Warning: Could not generate trip plan automatically. ${errorMessage}. You can finalize the trip later from the trip details page.`);
      }

      // Call parent callback with selection data
      onConfirm({
        flight: flightOptions.find(f => f.id === selectedFlight),
        hotel: hotelOptions.find(h => h.id === selectedHotel),
        activities: activityOptions.filter(a => selectedActivities.includes(a.id))
      });
    } catch (error) {
      console.error('Failed to save selections:', error);
      // Still call onConfirm to proceed
      onConfirm({
        flight: flightOptions.find(f => f.id === selectedFlight),
        hotel: hotelOptions.find(h => h.id === selectedHotel),
        activities: activityOptions.filter(a => selectedActivities.includes(a.id))
      });
    } finally {
      setIsSavingSelections(false);
    }
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
    
    // Get number of travelers (adults)
    const travelers = tripData?.adults || tripData?.adults_count || 1;
    
    // Calculate number of nights from trip dates
    let nights = 1; // Default to 1 night
    if (tripData?.start_date || tripData?.startDate) {
      const startDate = new Date(tripData?.start_date || tripData?.startDate);
      const endDate = new Date(tripData?.end_date || tripData?.endDate || tripData?.start_date || tripData?.startDate);
      
      if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime()) && endDate > startDate) {
        const timeDiff = endDate.getTime() - startDate.getTime();
        nights = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
        if (nights < 1) nights = 1;
      }
    }
    
    // Flight cost (per person, multiply by travelers)
    if (selectedFlight) {
      const flight = flightOptions.find(f => f.id === selectedFlight);
      if (flight?.price) {
        const flightPriceStr = flight.price.replace(/[^0-9.]/g, '');
        const flightPrice = parseFloat(flightPriceStr);
        if (!isNaN(flightPrice) && flightPrice > 0) {
          // Flight price is per person, multiply by number of travelers
          total += flightPrice * travelers;
        }
      }
    }
    
    // Hotel cost (per night, multiply by nights and travelers)
    if (selectedHotel) {
      const hotel = hotelOptions.find(h => h.id === selectedHotel);
      if (hotel?.price_per_night) {
        const pricePerNight = typeof hotel.price_per_night === 'number' 
          ? hotel.price_per_night 
          : parseFloat(String(hotel.price_per_night).replace(/[^0-9.]/g, ''));
        
        if (!isNaN(pricePerNight) && pricePerNight > 0) {
          // Hotel price per night * number of nights * number of travelers
          total += pricePerNight * nights * travelers;
        }
      }
    }
    
    // Activities cost (per activity, multiply by travelers)
    selectedActivities.forEach(actId => {
      const activity = activityOptions.find(a => a.id === actId);
      if (activity?.price) {
        const priceStr = String(activity.price);
        
        // Skip if price is "Price varies", "Free", "Contact", etc.
        const lowerPrice = priceStr.toLowerCase();
        if (lowerPrice.includes('varies') || 
            lowerPrice.includes('contact') || 
            lowerPrice.includes('free') ||
            lowerPrice === '' ||
            priceStr.trim() === '') {
          return; // Skip this activity
        }
        
        // Extract numeric value from price string
        const priceMatch = priceStr.match(/[\d.]+/);
        if (priceMatch) {
          const activityPrice = parseFloat(priceMatch[0]);
          if (!isNaN(activityPrice) && activityPrice > 0) {
            // Activity price is per person, multiply by travelers
            total += activityPrice * travelers;
          }
        }
      }
    });
    
    // Return 0 if total is NaN or invalid
    return isNaN(total) || total < 0 ? 0 : Math.round(total * 100) / 100;
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

            {isLoadingFlights ? (
              <div className="text-center py-4">
                <LoadingGame />
                <p className="text-gray-600 mt-4">Loading flight options...</p>
              </div>
            ) : flightOptions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No flights available</p>
              </div>
            ) : (
              flightOptions.map((flight) => (
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
                <div className="space-y-3 text-sm">
                  {/* Outbound Flight */}
                  <div className="pb-3 border-b">
                    <p className="text-xs text-gray-500 mb-2 font-semibold">Outbound Flight</p>
                    <div className="space-y-2">
                      {/* Route */}
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900">{flight.depCity}</p>
                          {flight.depAirport && (
                            <p className="text-xs text-gray-500">{flight.depAirport}</p>
                          )}
                        </div>
                        <div className="mx-2">
                          <Plane className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex-1 text-right">
                          <p className="font-semibold text-gray-900">{flight.arrCity}</p>
                          {flight.arrAirport && (
                            <p className="text-xs text-gray-500">{flight.arrAirport}</p>
                          )}
                        </div>
                      </div>
                      {/* Date and Times */}
                      <div>
                        {flight.depDate && (
                          <p className="text-xs text-gray-500 mb-1">{flight.depDate}</p>
                        )}
                        <p className="text-gray-700 font-medium">{flight.time}</p>
                        {flight.arrDate && flight.arrDate !== flight.depDate && (
                          <p className="text-xs text-gray-500 mt-1">Arrives: {flight.arrDate}</p>
                        )}
                      </div>
                      {/* Details */}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{flight.duration}</span>
                        <span>•</span>
                        <span>{flight.stops}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Return Flight */}
                  {flight.isRoundTrip && flight.returnTime && (
                    <div className="pt-2">
                      <p className="text-xs text-gray-500 mb-2 font-semibold">Return Flight</p>
                      <div className="space-y-2">
                        {/* Route */}
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">{flight.returnDepCity || 'Unknown'}</p>
                            {flight.returnDepAirport && (
                              <p className="text-xs text-gray-500">{flight.returnDepAirport}</p>
                            )}
                          </div>
                          <div className="mx-2">
                            <Plane className="w-4 h-4 text-blue-600 rotate-180" />
                          </div>
                          <div className="flex-1 text-right">
                            <p className="font-semibold text-gray-900">{flight.returnArrCity || 'Unknown'}</p>
                            {flight.returnArrAirport && (
                              <p className="text-xs text-gray-500">{flight.returnArrAirport}</p>
                            )}
                          </div>
                        </div>
                        {/* Date and Times */}
                        <div>
                          {flight.returnDepDate && (
                            <p className="text-xs text-gray-500 mb-1">{flight.returnDepDate}</p>
                          )}
                          <p className="text-gray-700 font-medium">{flight.returnTime}</p>
                          {flight.returnArrDate && flight.returnArrDate !== flight.returnDepDate && (
                            <p className="text-xs text-gray-500 mt-1">Arrives: {flight.returnArrDate}</p>
                          )}
                        </div>
                        {/* Details */}
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {flight.returnDuration && <span>{flight.returnDuration}</span>}
                          {flight.returnDuration && flight.returnStops && <span>•</span>}
                          {flight.returnStops && <span>{flight.returnStops}</span>}
                          {flight.returnAirline && flight.returnAirline !== flight.airline && (
                            <>
                              <span>•</span>
                              <span>{flight.returnAirline}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                {((flight.aiPros && flight.aiPros.length > 0) || (flight.aiCons && flight.aiCons.length > 0) || 
                  (flight.pros && flight.pros.length > 0) || (flight.cons && flight.cons.length > 0)) && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {(flight.aiPros || flight.pros || []).map((pro: string, idx: number) => (
                      <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-2 py-0 h-5">
                        {pro}
                      </Badge>
                    ))}
                    {(flight.aiCons || flight.cons || []).map((con: string, idx: number) => (
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
                {flight.google_flights_url && (
                  <div className="mt-2">
                    <a 
                      href={flight.google_flights_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white text-center text-sm py-2 px-4 rounded-lg transition-colors inline-block"
                    >
                      Book on Google Flights →
                    </a>
                  </div>
                )}
              </Card>
            ))
            )}
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

            {isLoadingHotels ? (
              <div className="text-center py-4">
                <LoadingGame />
                <p className="text-gray-600 mt-4">Searching hotels...</p>
              </div>
            ) : hotelOptions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No hotels found</p>
              </div>
            ) : (
              hotelOptions.map((hotel) => (
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
                    <img src={hotel.thumbnail || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&q=80'} alt={hotel.name} className="w-full h-full object-cover" />
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
                      {(hotel.amenities || []).slice(0, 3).map((amenity, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs px-1.5 py-0 h-5">
                          {amenity}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {(hotel.aiPros || hotel.pros || []).map((pro: string, idx: number) => (
                        <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-1.5 py-0 h-5">
                          {pro}
                        </Badge>
                      ))}
                      {(hotel.aiCons || hotel.cons || []).map((con: string, idx: number) => (
                        <Badge key={`con-${idx}`} className="bg-red-100 text-red-700 border-red-300 text-xs px-1.5 py-0 h-5">
                          {con}
                        </Badge>
                      ))}
                    </div>
                    <p className="font-semibold text-sm text-purple-600">
                      ${hotel.price_per_night}/night
                    </p>
                  </div>
                </div>
              </Card>
            ))
            )}
          </div>
        )}

        {/* Activities Step */}
        {currentStep === 'activities' && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600 mb-4">Choose activities (select multiple)</p>
            {isLoadingActivities ? (
              <div className="text-center py-4">
                <LoadingGame />
                <p className="text-gray-600 mt-4">Finding exciting activities...</p>
              </div>
            ) : activityOptions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No activities found</p>
              </div>
            ) : (
              activityOptions.map((activity) => (
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
                    <img src={activity.thumbnail || 'https://images.unsplash.com/photo-1451337516015-6b6e9a44a8a3?w=400&q=80'} alt={activity.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <p className="font-semibold text-sm mb-1">{activity.name}</p>
                        <p className="text-xs text-gray-600 mb-2">{activity.description}</p>
                        <p className="text-xs text-gray-500 mb-2">{activity.duration}</p>
                        <div className="flex flex-wrap gap-1">
                          {(activity.aiPros || activity.pros || []).map((pro: string, idx: number) => (
                            <Badge key={`pro-${idx}`} className="bg-green-100 text-green-700 border-green-300 text-xs px-1.5 py-0 h-5">
                              {pro}
                            </Badge>
                          ))}
                          {(activity.aiCons || activity.cons || []).map((con: string, idx: number) => (
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
            ))
            )}
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
                    <p className="font-semibold text-purple-600 mt-2">
                      ${hotel.price_per_night}/night
                    </p>
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
                      <p className="font-semibold text-sm text-green-600">
                        {activity.price && activity.price.trim() !== '' 
                          ? activity.price 
                          : 'Price varies'}
                      </p>
                    </div>
                  ) : null;
                })}
              </div>
            </Card>

            {/* Total Cost */}
            <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Estimated Total Cost</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {tripData?.adults || tripData?.adults_count || 1} {tripData?.adults === 1 || tripData?.adults_count === 1 ? 'person' : 'people'}
                    </p>
                  </div>
                  <p className="text-2xl font-semibold text-blue-600">${totalCost().toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                </div>
                {(() => {
                  const travelers = tripData?.adults || tripData?.adults_count || 1;
                  const perPerson = travelers > 0 ? totalCost() / travelers : 0;
                  return travelers > 1 ? (
                    <p className="text-xs text-gray-500 text-right">
                      ${perPerson.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} per person
                    </p>
                  ) : null;
                })()}
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
              disabled={isSavingSelections}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 h-12"
            >
              {isSavingSelections ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Finalizing Trip & Generating Plan...
                </span>
              ) : (
                'Confirm & Create Trip'
              )}
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
