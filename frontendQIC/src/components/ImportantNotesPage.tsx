import { ArrowLeft, Bell, FileText, Shirt, Globe, AlertTriangle, Info, Plane, DollarSign } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';

import { useEffect, useState } from 'react';
import { tripsApi, TripResponse, cultureApi, CultureGuide, CultureTip } from '../utils/api';

interface ImportantNotesPageProps {
  onBack: () => void;
  destination?: string;
  onNotifications: () => void;
  tripId?: string;
}

export function ImportantNotesPage({ onBack, destination, onNotifications, tripId }: ImportantNotesPageProps) {
  const [trip, setTrip] = useState<TripResponse | null>(null);
  const [cultureGuide, setCultureGuide] = useState<CultureGuide | null>(null);
  const [isLoading, setIsLoading] = useState(!!tripId);
  const [isLoadingGuide, setIsLoadingGuide] = useState(false);
  
  useEffect(() => {
    if (tripId) {
      const fetchTrip = async () => {
        try {
          const tripData = await tripsApi.getTrip(tripId);
          setTrip(tripData);
        } catch (error) {
          console.error('Failed to fetch trip:', error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchTrip();
    } else {
      setIsLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    const fetchCultureGuide = async () => {
      if (!tripId || !trip) return;
      
      setIsLoadingGuide(true);
      try {
        // Try to get saved guide first
        let guide = await cultureApi.getSavedGuide(tripId);
        
        // If no saved guide, generate a new one
        if (!guide) {
          guide = await cultureApi.getGuide(tripId, trip.to_city, 'en');
        }
        
        setCultureGuide(guide);
      } catch (error) {
        console.error('Failed to fetch culture guide:', error);
      } finally {
        setIsLoadingGuide(false);
      }
    };

    if (tripId && trip) {
      fetchCultureGuide();
    }
  }, [tripId, trip]);
  
  const finalDestination = destination || (trip ? trip.to_city : 'Dubai, UAE');

  // Organize tips by category
  const organizeTipsByCategory = (tips: CultureTip[]) => {
    const categories: Record<string, CultureTip[]> = {};
    
    tips.forEach(tip => {
      if (!categories[tip.category]) {
        categories[tip.category] = [];
      }
      categories[tip.category].push(tip);
    });
    
    return categories;
  };

  // Get category display name
  const getCategoryDisplayName = (category: string): string => {
    const categoryNames: Record<string, string> = {
      'greeting_etiquette': 'Greeting & Etiquette',
      'dress_code': 'Dress Code',
      'behavioral_norms': 'Behavioral Norms',
      'dining_etiquette': 'Dining Etiquette',
      'communication': 'Communication',
      'social_customs': 'Social Customs',
      'religious_practices': 'Religious Practices',
      'business_etiquette': 'Business Etiquette',
    };
    return categoryNames[category] || category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Get category icon and color
  const getCategoryStyle = (category: string) => {
    const styles: Record<string, { icon: JSX.Element; color: string }> = {
      'greeting_etiquette': { icon: <Globe className="w-5 h-5" />, color: 'blue' },
      'dress_code': { icon: <Shirt className="w-5 h-5" />, color: 'purple' },
      'behavioral_norms': { icon: <AlertTriangle className="w-5 h-5" />, color: 'green' },
      'dining_etiquette': { icon: <Info className="w-5 h-5" />, color: 'orange' },
      'communication': { icon: <FileText className="w-5 h-5" />, color: 'blue' },
      'social_customs': { icon: <Globe className="w-5 h-5" />, color: 'green' },
      'religious_practices': { icon: <AlertTriangle className="w-5 h-5" />, color: 'red' },
      'business_etiquette': { icon: <Plane className="w-5 h-5" />, color: 'purple' },
    };
    return styles[category] || { icon: <Info className="w-5 h-5" />, color: 'gray' };
  };
  
  const importantNotes = cultureGuide ? organizeTipsByCategory(cultureGuide.tips) : {};

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' };
      case 'purple':
        return { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' };
      case 'green':
        return { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' };
      case 'red':
        return { bg: 'bg-red-100', text: 'text-red-600', border: 'border-red-200' };
      case 'orange':
        return { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' };
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-4 sm:px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors flex-shrink-0"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-lg sm:text-xl font-semibold">Important Notes</h1>
            <p className="text-xs sm:text-sm text-gray-500">{finalDestination}</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative flex-shrink-0"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Alert Banner */}
      <div className="px-4 sm:px-6 py-4">
        <Card className="p-3 sm:p-4 bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-sm text-orange-900">Important</p>
              <p className="text-xs sm:text-sm text-orange-700 mt-1">
                Please read all travel requirements carefully before your trip. Laws and customs may differ significantly from your home country.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Summary Section */}
      {cultureGuide?.summary && (
        <div className="px-4 sm:px-6 py-4">
          <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <div className="flex gap-3">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-sm text-blue-900 mb-2">Cultural Overview</p>
                <p className="text-xs sm:text-sm text-blue-700">
                  {cultureGuide.summary}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Loading State */}
      {isLoadingGuide && (
        <div className="px-4 sm:px-6 py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading cultural information...</p>
          </div>
        </div>
      )}

      {/* Content Sections - Organized by Category */}
      {!isLoadingGuide && Object.keys(importantNotes).length > 0 && (
        <div className="px-4 sm:px-6 pb-6 space-y-4">
          {Object.entries(importantNotes).map(([category, tips]) => {
            const categoryStyle = getCategoryStyle(category);
            const colorClasses = getColorClasses(categoryStyle.color);
            
            return (
              <Card key={category} className={`p-4 border-2 ${colorClasses.border}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${colorClasses.bg} flex items-center justify-center`}>
                    <div className={colorClasses.text}>
                      {categoryStyle.icon}
                    </div>
                  </div>
                  <h2 className="font-semibold text-base sm:text-lg">
                    {getCategoryDisplayName(category)}
                  </h2>
                </div>
                <Accordion type="single" collapsible className="space-y-2">
                  {tips.map((tip, index) => (
                    <AccordionItem key={index} value={`${category}-${index}`} className="border rounded-lg px-3">
                      <AccordionTrigger className="text-sm hover:no-underline py-3">
                        <div className="flex items-center gap-2">
                          {tip.emoji && <span className="text-base">{tip.emoji}</span>}
                          <span>{tip.title}</span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3 space-y-2">
                        <p>{tip.tip}</p>
                        {tip.do && (
                          <div className="mt-2 pt-2 border-t border-gray-200">
                            <p className="font-semibold text-green-700 mb-1">✓ Do:</p>
                            <p className="text-gray-700">{tip.do}</p>
                          </div>
                        )}
                        {tip.avoid && (
                          <div className="mt-2 pt-2 border-t border-gray-200">
                            <p className="font-semibold text-red-700 mb-1">✗ Avoid:</p>
                            <p className="text-gray-700">{tip.avoid}</p>
                          </div>
                        )}
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </Card>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoadingGuide && Object.keys(importantNotes).length === 0 && (
        <div className="px-4 sm:px-6 py-12 flex flex-col items-center justify-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Info className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="font-semibold text-base mb-2">No cultural information available</h3>
          <p className="text-xs sm:text-sm text-gray-500 text-center">
            Cultural guide will be generated when you finalize your trip.
          </p>
        </div>
      )}
    </div>
  );
}
