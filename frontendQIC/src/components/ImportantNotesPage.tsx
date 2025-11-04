import { ArrowLeft, Bell, FileText, Shirt, Globe, AlertTriangle, Info, Plane, DollarSign } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';

import { useEffect, useState } from 'react';
import { tripsApi, TripResponse } from '../utils/api';

interface ImportantNotesPageProps {
  onBack: () => void;
  destination?: string;
  onNotifications: () => void;
  tripId?: string;
}

export function ImportantNotesPage({ onBack, destination, onNotifications, tripId }: ImportantNotesPageProps) {
  const [trip, setTrip] = useState<TripResponse | null>(null);
  const [isLoading, setIsLoading] = useState(!!tripId);
  
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
  
  const finalDestination = destination || (trip ? trip.to_city : 'Dubai, UAE');
  
  // Mock data - in a real app, this would be fetched based on destination from a culture/visa API
  const importantNotes = {
    visa: {
      title: 'Visa Requirements',
      icon: <FileText className="w-5 h-5" />,
      color: 'blue',
      items: [
        {
          title: 'Tourist Visa',
          content: 'Most nationalities can obtain a visa on arrival for 30-90 days. Check with UAE embassy for your specific country requirements.'
        },
        {
          title: 'Passport Validity',
          content: 'Your passport must be valid for at least 6 months from your entry date.'
        },
        {
          title: 'Visa Fees',
          content: 'Visa on arrival costs approximately AED 100-300 (USD 27-82) depending on duration.'
        }
      ]
    },
    clothing: {
      title: 'Dress Code & Clothing',
      icon: <Shirt className="w-5 h-5" />,
      color: 'purple',
      items: [
        {
          title: 'General Guidelines',
          content: 'Dubai is relatively liberal, but modest clothing is recommended. Cover shoulders and knees in public areas, especially government buildings and mosques.'
        },
        {
          title: 'Beach & Pool',
          content: 'Swimwear is acceptable at beaches and hotel pools, but cover up when leaving these areas.'
        },
        {
          title: 'What to Pack',
          content: 'Light, breathable fabrics for hot weather. Bring a light jacket for heavily air-conditioned malls and restaurants. Comfortable walking shoes essential.'
        },
        {
          title: 'Religious Sites',
          content: 'Women should wear an abaya (provided at entrance) and headscarf when visiting mosques. Men should wear long pants and shirts with sleeves.'
        }
      ]
    },
    culture: {
      title: 'Culture & Customs',
      icon: <Globe className="w-5 h-5" />,
      color: 'green',
      items: [
        {
          title: 'Ramadan',
          content: 'During Ramadan, eating, drinking, and smoking in public during daylight hours is prohibited. Many restaurants close during the day.'
        },
        {
          title: 'Public Behavior',
          content: 'Public displays of affection should be minimal. Avoid excessive physical contact in public.'
        },
        {
          title: 'Photography',
          content: 'Always ask permission before photographing people, especially women. Avoid photographing government buildings and military installations.'
        },
        {
          title: 'Greetings',
          content: 'A handshake is common for men. Women may choose to shake hands or simply nod. Wait for a woman to extend her hand first.'
        },
        {
          title: 'Language',
          content: 'Arabic is the official language, but English is widely spoken in tourist areas, hotels, and restaurants.'
        }
      ]
    },
    rules: {
      title: 'Important Rules & Laws',
      icon: <AlertTriangle className="w-5 h-5" />,
      color: 'red',
      items: [
        {
          title: 'Alcohol',
          content: 'Alcohol is only served in licensed hotels and clubs. Public intoxication is illegal and can result in arrest. Drinking and driving has zero tolerance.'
        },
        {
          title: 'Drugs',
          content: 'UAE has extremely strict drug laws. Even trace amounts can lead to imprisonment. This includes some prescription medications - check before traveling.'
        },
        {
          title: 'Public Conduct',
          content: 'Swearing, rude gestures, and offensive behavior can result in fines or imprisonment. Be respectful at all times.'
        },
        {
          title: 'Friday',
          content: 'Friday is the holy day. Many businesses are closed or have reduced hours. Government offices are typically closed Thursday-Friday.'
        },
        {
          title: 'Social Media',
          content: 'Be careful what you post on social media. Defamatory comments about UAE or its leaders can result in legal action.'
        }
      ]
    },
    practical: {
      title: 'Practical Information',
      icon: <Info className="w-5 h-5" />,
      color: 'orange',
      items: [
        {
          title: 'Currency',
          content: 'UAE Dirham (AED). 1 USD ≈ 3.67 AED. Credit cards widely accepted. ATMs available everywhere.'
        },
        {
          title: 'Tipping',
          content: '10-15% is customary in restaurants. Round up taxi fares. Tip hotel staff AED 5-10 per service.'
        },
        {
          title: 'Emergency Numbers',
          content: 'Police: 999, Ambulance: 998, Fire: 997, Tourist Police: 800 4438'
        },
        {
          title: 'Weather',
          content: 'Best time: November-March (20-30°C). Summer (May-September) is extremely hot (40-45°C). Always carry water.'
        },
        {
          title: 'Internet & SIM',
          content: 'Free WiFi in most hotels and malls. Tourist SIM cards available at airport (Etisalat, du).'
        }
      ]
    }
  };

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
            <p className="text-xs sm:text-sm text-gray-500">{destination}</p>
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

      {/* Content Sections */}
      <div className="px-4 sm:px-6 pb-6 space-y-4">
        {/* Visa Requirements */}
        <Card className={`p-4 border-2 ${getColorClasses(importantNotes.visa.color).border}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${getColorClasses(importantNotes.visa.color).bg} flex items-center justify-center`}>
              <div className={getColorClasses(importantNotes.visa.color).text}>
                {importantNotes.visa.icon}
              </div>
            </div>
            <h2 className="font-semibold text-base sm:text-lg">{importantNotes.visa.title}</h2>
          </div>
          <Accordion type="single" collapsible className="space-y-2">
            {importantNotes.visa.items.map((item, index) => (
              <AccordionItem key={index} value={`visa-${index}`} className="border rounded-lg px-3">
                <AccordionTrigger className="text-sm hover:no-underline py-3">
                  {item.title}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3">
                  {item.content}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>

        {/* Clothing */}
        <Card className={`p-4 border-2 ${getColorClasses(importantNotes.clothing.color).border}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${getColorClasses(importantNotes.clothing.color).bg} flex items-center justify-center`}>
              <div className={getColorClasses(importantNotes.clothing.color).text}>
                {importantNotes.clothing.icon}
              </div>
            </div>
            <h2 className="font-semibold text-base sm:text-lg">{importantNotes.clothing.title}</h2>
          </div>
          <Accordion type="single" collapsible className="space-y-2">
            {importantNotes.clothing.items.map((item, index) => (
              <AccordionItem key={index} value={`clothing-${index}`} className="border rounded-lg px-3">
                <AccordionTrigger className="text-sm hover:no-underline py-3">
                  {item.title}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3">
                  {item.content}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>

        {/* Culture & Customs */}
        <Card className={`p-4 border-2 ${getColorClasses(importantNotes.culture.color).border}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${getColorClasses(importantNotes.culture.color).bg} flex items-center justify-center`}>
              <div className={getColorClasses(importantNotes.culture.color).text}>
                {importantNotes.culture.icon}
              </div>
            </div>
            <h2 className="font-semibold text-base sm:text-lg">{importantNotes.culture.title}</h2>
          </div>
          <Accordion type="single" collapsible className="space-y-2">
            {importantNotes.culture.items.map((item, index) => (
              <AccordionItem key={index} value={`culture-${index}`} className="border rounded-lg px-3">
                <AccordionTrigger className="text-sm hover:no-underline py-3">
                  {item.title}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3">
                  {item.content}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>

        {/* Rules & Laws */}
        <Card className={`p-4 border-2 ${getColorClasses(importantNotes.rules.color).border}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${getColorClasses(importantNotes.rules.color).bg} flex items-center justify-center`}>
              <div className={getColorClasses(importantNotes.rules.color).text}>
                {importantNotes.rules.icon}
              </div>
            </div>
            <h2 className="font-semibold text-base sm:text-lg">{importantNotes.rules.title}</h2>
          </div>
          <Accordion type="single" collapsible className="space-y-2">
            {importantNotes.rules.items.map((item, index) => (
              <AccordionItem key={index} value={`rules-${index}`} className="border rounded-lg px-3">
                <AccordionTrigger className="text-sm hover:no-underline py-3">
                  {item.title}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3">
                  {item.content}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>

        {/* Practical Information */}
        <Card className={`p-4 border-2 ${getColorClasses(importantNotes.practical.color).border}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg ${getColorClasses(importantNotes.practical.color).bg} flex items-center justify-center`}>
              <div className={getColorClasses(importantNotes.practical.color).text}>
                {importantNotes.practical.icon}
              </div>
            </div>
            <h2 className="font-semibold text-base sm:text-lg">{importantNotes.practical.title}</h2>
          </div>
          <Accordion type="single" collapsible className="space-y-2">
            {importantNotes.practical.items.map((item, index) => (
              <AccordionItem key={index} value={`practical-${index}`} className="border rounded-lg px-3">
                <AccordionTrigger className="text-sm hover:no-underline py-3">
                  {item.title}
                </AccordionTrigger>
                <AccordionContent className="text-xs sm:text-sm text-gray-600 pb-3">
                  {item.content}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Card>
      </div>
    </div>
  );
}
