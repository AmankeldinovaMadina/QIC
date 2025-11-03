import { ArrowLeft, Send, Sparkles, Bell, Calendar as CalendarIcon, MapPin } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';

interface TripChatPageProps {
  onBack: () => void;
  onComplete: (tripData: any) => void;
  onNotifications?: () => void;
}

interface Message {
  id: number;
  text: string;
  isAI: boolean;
  options?: string[];
  showCalendar?: boolean;
  showTextInput?: boolean;
  showCityInput?: boolean;
  showTravelerCount?: boolean;
  showBudgetRange?: boolean;
  showActivitiesMultiple?: boolean;
}

export function TripChatPage({ onBack, onComplete, onNotifications }: TripChatPageProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm Qico, your AI travel assistant. 👋 Let's plan your perfect trip! Where would you like to travel?",
      isAI: true,
      showCityInput: true
    }
  ]);
  const [currentStep, setCurrentStep] = useState(0);
  const [tripData, setTripData] = useState<any>({});
  const [selectedStartDate, setSelectedStartDate] = useState<Date>();
  const [selectedEndDate, setSelectedEndDate] = useState<Date>();
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [fromCity, setFromCity] = useState('');
  const [toCity, setToCity] = useState('');
  const [showFromSuggestions, setShowFromSuggestions] = useState(false);
  const [showToSuggestions, setShowToSuggestions] = useState(false);
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);

  const cities = ['Dubai, UAE', 'Paris, France', 'Tokyo, Japan', 'New York, USA', 'Maldives', 'Istanbul, Turkey', 'Bali, Indonesia', 'London, UK', 'Rome, Italy', 'Barcelona, Spain', 'Singapore', 'Bangkok, Thailand', 'Sydney, Australia'];

  const questions = [
    { 
      key: 'destination', 
      text: "Where would you like to travel?", 
      showCityInput: true
    },
    { 
      key: 'dates', 
      text: 'When do you plan to travel? Please select your travel dates:',
      showCalendar: true
    },
    { 
      key: 'transport', 
      text: 'How would you like to travel?', 
      options: ['✈️ Flight', '🚂 Train', '🚗 Car', '🚢 Cruise', '🚌 Bus']
    },
    { 
      key: 'companions', 
      text: 'Who will be traveling with you?', 
      options: ['👤 Solo', '👨‍👩‍👧‍👦 Family', '👥 Friends', '💑 Couple']
    },
    { 
      key: 'travelerCount', 
      text: 'How many people will be traveling?',
      showTravelerCount: true
    },
    { 
      key: 'budget', 
      text: 'What is your budget per person? (Enter minimum and maximum in USD)',
      showBudgetRange: true
    },
    { 
      key: 'preferences', 
      text: 'What type of activities interest you most? (Select all that apply)', 
      showActivitiesMultiple: true,
      options: ['🏖️ Beach & Relaxation', '🏛️ Museums & Culture', '🍽️ Gastro Tourism', '🏔️ Nature & Adventure', '🛍️ Shopping', '🎭 Entertainment', '🏃 Sports & Activities', '🧘 Wellness & Spa', '🎨 Art & Galleries', '🎪 Theme Parks', '🚴 Outdoor Activities', '🍷 Wine Tasting']
    },
    {
      key: 'notes',
      text: 'Any additional notes or special requirements? (e.g., dietary restrictions, accessibility needs, specific interests)',
      showTextInput: true
    }
  ];

  const handleSend = (value?: string) => {
    const messageText = value || additionalNotes;
    if (!messageText.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: messageText,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);
    setAdditionalNotes('');

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ ...prev, [currentQuestion.key]: messageText }));

    // Move to next question or complete
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      } else {
        // All questions answered
        const finalMessage: Message = {
          id: messages.length + 2,
          text: "Perfect! 🎉 I'm creating your personalized travel plan. This will just take a moment...",
          isAI: true
        };
        setMessages(prev => [...prev, finalMessage]);
        
        setTimeout(() => {
          onComplete({ ...tripData, [currentQuestion.key]: messageText });
        }, 2000);
      }
    }, 500);
  };

  const handleOptionClick = (option: string) => {
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: option,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ ...prev, [currentQuestion.key]: option }));

    // Check if we need to skip traveler count question (for solo travelers)
    const shouldSkipTravelerCount = currentQuestion.key === 'companions' && option === '👤 Solo';

    // Move to next question or complete
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        let nextStep = currentStep + 1;
        
        // Skip traveler count if solo
        if (shouldSkipTravelerCount && questions[nextStep].key === 'travelerCount') {
          setTripData(prev => ({ ...prev, travelerCount: '1 adult' }));
          nextStep = currentStep + 2;
        }
        
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      } else {
        // All questions answered
        const finalMessage: Message = {
          id: messages.length + 2,
          text: "Perfect! 🎉 I'm creating your personalized travel plan. This will just take a moment...",
          isAI: true
        };
        setMessages(prev => [...prev, finalMessage]);
        
        setTimeout(() => {
          onComplete({ ...tripData, [currentQuestion.key]: option });
        }, 2000);
      }
    }, 500);
  };

  const handleDateSelection = () => {
    if (!selectedStartDate || !selectedEndDate) return;

    const dateRange = `${format(selectedStartDate, 'MMM dd, yyyy')} - ${format(selectedEndDate, 'MMM dd, yyyy')}`;
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: dateRange,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ 
      ...prev, 
      [currentQuestion.key]: dateRange,
      startDate: selectedStartDate,
      endDate: selectedEndDate
    }));

    // Reset dates
    setSelectedStartDate(undefined);
    setSelectedEndDate(undefined);

    // Move to next question
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      }
    }, 500);
  };

  const handleCitySelection = () => {
    if (!fromCity.trim() || !toCity.trim()) return;

    const cityText = `From: ${fromCity} → To: ${toCity}`;
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: cityText,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ 
      ...prev, 
      [currentQuestion.key]: cityText,
      fromCity,
      toCity
    }));

    // Reset cities
    setFromCity('');
    setToCity('');

    // Move to next question
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      }
    }, 500);
  };

  const handleTravelerCountSelection = () => {
    const travelerText = `${adults} adult${adults > 1 ? 's' : ''}${children > 0 ? `, ${children} child${children > 1 ? 'ren' : ''}` : ''}`;
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: travelerText,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ 
      ...prev, 
      [currentQuestion.key]: travelerText,
      adults,
      children
    }));

    // Reset
    setAdults(1);
    setChildren(0);

    // Move to next question
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      }
    }, 500);
  };

  const handleBudgetRangeSelection = () => {
    if (!minBudget || !maxBudget) return;
    
    const budgetText = `$${minBudget} - $${maxBudget}`;
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: budgetText,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ 
      ...prev, 
      [currentQuestion.key]: budgetText,
      minBudget: parseInt(minBudget),
      maxBudget: parseInt(maxBudget)
    }));

    // Reset
    setMinBudget('');
    setMaxBudget('');

    // Move to next question
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      }
    }, 500);
  };

  const toggleActivity = (activity: string) => {
    setSelectedActivities(prev => 
      prev.includes(activity) ? prev.filter(a => a !== activity) : [...prev, activity]
    );
  };

  const handleActivitiesSelection = () => {
    if (selectedActivities.length === 0) return;
    
    const activitiesText = selectedActivities.join(', ');
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: activitiesText,
      isAI: false
    };
    setMessages(prev => [...prev, userMessage]);

    // Save answer
    const currentQuestion = questions[currentStep];
    setTripData(prev => ({ 
      ...prev, 
      [currentQuestion.key]: activitiesText,
      selectedActivities: [...selectedActivities]
    }));

    // Reset
    setSelectedActivities([]);

    // Move to next question
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        const nextStep = currentStep + 1;
        const nextQuestion = questions[nextStep];
        const aiMessage: Message = {
          id: messages.length + 2,
          text: nextQuestion.text,
          isAI: true,
          options: nextQuestion.options,
          showCalendar: nextQuestion.showCalendar,
          showTextInput: nextQuestion.showTextInput,
          showCityInput: nextQuestion.showCityInput,
          showTravelerCount: nextQuestion.showTravelerCount,
          showBudgetRange: nextQuestion.showBudgetRange,
          showActivitiesMultiple: nextQuestion.showActivitiesMultiple
        };
        setMessages(prev => [...prev, aiMessage]);
        setCurrentStep(nextStep);
      } else {
        // All questions answered
        const finalMessage: Message = {
          id: messages.length + 2,
          text: "Perfect! 🎉 I'm creating your personalized travel plan. This will just take a moment...",
          isAI: true
        };
        setMessages(prev => [...prev, finalMessage]);
        
        setTimeout(() => {
          onComplete({ ...tripData, [currentQuestion.key]: activitiesText, selectedActivities: [...selectedActivities] });
        }, 2000);
      }
    }, 500);
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 flex-1">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold">Qico AI Assistant</h1>
              <p className="text-xs text-gray-500">Trip Planner</p>
            </div>
          </div>
          <button 
            onClick={() => onNotifications?.()}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id}>
            <div className={`flex ${message.isAI ? 'justify-start' : 'justify-end'}`}>
              {message.isAI && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  message.isAI
                    ? 'bg-white shadow-sm'
                    : 'bg-blue-600 text-white'
                }`}
              >
                <p className="text-sm">{message.text}</p>
              </div>
            </div>
            
            {/* Quick reply options */}
            {message.isAI && message.options && !message.showActivitiesMultiple && (
              <div className="ml-10 mt-2 flex flex-wrap gap-2">
                {message.options.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleOptionClick(option)}
                    className="px-3 py-2 bg-white border-2 border-blue-100 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm"
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}

            {/* Multiple choice activities */}
            {message.isAI && message.showActivitiesMultiple && message.options && (
              <div className="ml-10 mt-3">
                <Card className="p-4">
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    {message.options.map((option, idx) => (
                      <button
                        key={idx}
                        onClick={() => toggleActivity(option)}
                        className={`px-3 py-3 rounded-lg border-2 transition-all text-sm ${
                          selectedActivities.includes(option)
                            ? 'border-blue-600 bg-blue-50 text-blue-700'
                            : 'border-gray-200 bg-white hover:border-blue-200'
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                  <Button
                    onClick={handleActivitiesSelection}
                    disabled={selectedActivities.length === 0}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    Continue ({selectedActivities.length} selected)
                  </Button>
                </Card>
              </div>
            )}

            {/* City selection input */}
            {message.isAI && message.showCityInput && (
              <div className="ml-10 mt-3">
                <Card className="p-4">
                  <div className="space-y-3">
                    <div className="relative">
                      <label className="text-sm font-semibold mb-2 block">From</label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <Input
                          value={fromCity}
                          onChange={(e) => {
                            setFromCity(e.target.value);
                            setShowFromSuggestions(e.target.value.length > 0);
                          }}
                          placeholder="Enter departure city"
                          className="pl-10"
                        />
                      </div>
                      {showFromSuggestions && fromCity && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-48 overflow-y-auto">
                          {cities
                            .filter(city => city.toLowerCase().includes(fromCity.toLowerCase()) && city !== toCity)
                            .map((city, idx) => (
                            <button
                              key={idx}
                              onClick={() => {
                                setFromCity(city);
                                setShowFromSuggestions(false);
                              }}
                              className="w-full px-4 py-2 text-left hover:bg-blue-50 text-sm"
                            >
                              {city}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="relative">
                      <label className="text-sm font-semibold mb-2 block">To</label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <Input
                          value={toCity}
                          onChange={(e) => {
                            setToCity(e.target.value);
                            setShowToSuggestions(e.target.value.length > 0);
                          }}
                          placeholder="Enter destination city"
                          className="pl-10"
                        />
                      </div>
                      {showToSuggestions && toCity && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-48 overflow-y-auto">
                          {cities
                            .filter(city => city.toLowerCase().includes(toCity.toLowerCase()) && city !== fromCity)
                            .map((city, idx) => (
                            <button
                              key={idx}
                              onClick={() => {
                                setToCity(city);
                                setShowToSuggestions(false);
                              }}
                              className="w-full px-4 py-2 text-left hover:bg-blue-50 text-sm"
                            >
                              {city}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    <Button
                      onClick={handleCitySelection}
                      disabled={!fromCity.trim() || !toCity.trim() || fromCity === toCity}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {fromCity === toCity && fromCity ? 'Please select different cities' : 'Confirm Cities'}
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {/* Calendar for date selection */}
            {message.isAI && message.showCalendar && (
              <div className="ml-10 mt-3">
                <Card className="p-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-semibold mb-2 block">Start Date</label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button variant="outline" className="w-full justify-start text-left text-sm">
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {selectedStartDate ? format(selectedStartDate, 'PPP') : 'Select start date'}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 z-50" align="start" sideOffset={4}>
                          <Calendar
                            mode="single"
                            selected={selectedStartDate}
                            onSelect={setSelectedStartDate}
                            disabled={(date) => date < new Date()}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                    <div>
                      <label className="text-sm font-semibold mb-2 block">End Date</label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button variant="outline" className="w-full justify-start text-left text-sm">
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {selectedEndDate ? format(selectedEndDate, 'PPP') : 'Select end date'}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 z-50" align="start" sideOffset={4}>
                          <Calendar
                            mode="single"
                            selected={selectedEndDate}
                            onSelect={setSelectedEndDate}
                            disabled={(date) => !selectedStartDate || date < selectedStartDate}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                    <Button
                      onClick={handleDateSelection}
                      disabled={!selectedStartDate || !selectedEndDate}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      Confirm Dates
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {/* Traveler count input */}
            {message.isAI && message.showTravelerCount && (
              <div className="ml-10 mt-3">
                <Card className="p-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-semibold mb-2 block">Adults (18+)</label>
                      <div className="flex items-center gap-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setAdults(Math.max(1, adults - 1))}
                          className="w-10 h-10"
                        >
                          -
                        </Button>
                        <span className="text-lg font-semibold w-12 text-center">{adults}</span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setAdults(Math.min(20, adults + 1))}
                          className="w-10 h-10"
                        >
                          +
                        </Button>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-semibold mb-2 block">Children (0-17)</label>
                      <div className="flex items-center gap-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setChildren(Math.max(0, children - 1))}
                          className="w-10 h-10"
                        >
                          -
                        </Button>
                        <span className="text-lg font-semibold w-12 text-center">{children}</span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setChildren(Math.min(20, children + 1))}
                          className="w-10 h-10"
                        >
                          +
                        </Button>
                      </div>
                    </div>
                    <Button
                      onClick={handleTravelerCountSelection}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      Confirm
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {/* Budget range input */}
            {message.isAI && message.showBudgetRange && (
              <div className="ml-10 mt-3">
                <Card className="p-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-semibold mb-2 block">Minimum Budget (USD)</label>
                      <Input
                        type="number"
                        value={minBudget}
                        onChange={(e) => setMinBudget(e.target.value)}
                        placeholder="e.g., 500"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-semibold mb-2 block">Maximum Budget (USD)</label>
                      <Input
                        type="number"
                        value={maxBudget}
                        onChange={(e) => setMaxBudget(e.target.value)}
                        placeholder="e.g., 2000"
                        min="0"
                      />
                    </div>
                    <Button
                      onClick={handleBudgetRangeSelection}
                      disabled={!minBudget || !maxBudget || parseInt(minBudget) >= parseInt(maxBudget)}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      Confirm Budget
                    </Button>
                    {minBudget && maxBudget && parseInt(minBudget) >= parseInt(maxBudget) && (
                      <p className="text-xs text-red-500 text-center">
                        Maximum budget must be greater than minimum
                      </p>
                    )}
                  </div>
                </Card>
              </div>
            )}

            {/* Text input for additional notes */}
            {message.isAI && message.showTextInput && (
              <div className="ml-10 mt-3">
                <Card className="p-3">
                  <div className="flex gap-2">
                    <Input
                      value={additionalNotes}
                      onChange={(e) => setAdditionalNotes(e.target.value)}
                      placeholder="Type any additional notes or press skip..."
                      className="flex-1"
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <Button
                      onClick={() => handleSend()}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Send
                    </Button>
                  </div>
                  <Button
                    onClick={() => handleOptionClick('No additional notes')}
                    variant="ghost"
                    size="sm"
                    className="w-full mt-2"
                  >
                    Skip
                  </Button>
                </Card>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Info Footer */}
      <div className="sticky bottom-0 bg-gradient-to-t from-blue-50 to-transparent px-6 py-4">
        <p className="text-xs text-center text-gray-500">
          Select from the options above to continue
        </p>
      </div>
    </div>
  );
}