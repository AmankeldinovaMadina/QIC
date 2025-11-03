import { ArrowLeft, CheckCircle2, Circle, ShoppingBag, Shield, Smartphone, Car as CarIcon, Bell } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface TripChecklistPageProps {
  onBack: () => void;
  onNotifications: () => void;
}

interface ChecklistItem {
  id: number;
  text: string;
  checked: boolean;
  category: string;
}

export function TripChecklistPage({ onBack, onNotifications }: TripChecklistPageProps) {
  const [checklist, setChecklist] = useState<ChecklistItem[]>([
    { id: 1, text: 'Passport (valid for 6+ months)', checked: false, category: 'Documents' },
    { id: 2, text: 'Flight tickets / booking confirmation', checked: false, category: 'Documents' },
    { id: 3, text: 'Travel insurance', checked: false, category: 'Documents' },
    { id: 4, text: 'Visa (if required)', checked: false, category: 'Documents' },
    { id: 5, text: 'Hotel booking confirmation', checked: false, category: 'Documents' },
    { id: 6, text: 'Local currency / credit cards', checked: false, category: 'Money' },
    { id: 7, text: 'Power bank & chargers', checked: false, category: 'Electronics' },
    { id: 8, text: 'Travel adapter', checked: false, category: 'Electronics' },
    { id: 9, text: 'Phone & camera', checked: false, category: 'Electronics' },
    { id: 10, text: 'Medications & first aid kit', checked: false, category: 'Health' },
    { id: 11, text: 'Sunscreen & toiletries', checked: false, category: 'Health' },
    { id: 12, text: 'Comfortable walking shoes', checked: false, category: 'Clothing' },
    { id: 13, text: 'Weather-appropriate clothing', checked: false, category: 'Clothing' },
    { id: 14, text: 'Swimwear', checked: false, category: 'Clothing' }
  ]);

  const toggleItem = (id: number) => {
    setChecklist(prev =>
      prev.map(item =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    );
  };

  const categories = ['Documents', 'Money', 'Electronics', 'Health', 'Clothing'];
  const completedCount = checklist.filter(item => item.checked).length;
  const totalCount = checklist.length;
  const progress = Math.round((completedCount / totalCount) * 100);

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-green-50 to-white pb-6">
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
            <h1 className="text-xl font-semibold">Pre-Trip Checklist</h1>
            <p className="text-sm text-gray-500">Make sure you're ready!</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>

        {/* Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Your progress</span>
            <span className="text-sm font-semibold text-green-600">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{completedCount} of {totalCount} completed</p>
        </div>
      </div>

      {/* Checklist Items */}
      <div className="px-6 py-4">
        {categories.map((category) => {
          const categoryItems = checklist.filter(item => item.category === category);
          if (categoryItems.length === 0) return null;

          return (
            <div key={category} className="mb-6">
              <h3 className="font-semibold mb-3 text-gray-700">{category}</h3>
              <div className="space-y-2">
                {categoryItems.map((item) => (
                  <Card
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    className={`p-4 cursor-pointer transition-all ${
                      item.checked
                        ? 'bg-green-50 border-green-200'
                        : 'bg-white hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {item.checked ? (
                        <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-300 flex-shrink-0" />
                      )}
                      <span className={`flex-1 ${item.checked ? 'line-through text-gray-500' : ''}`}>
                        {item.text}
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Commercial Offers */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-2 mb-4">
          <ShoppingBag className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold">Recommended Services</h2>
        </div>

        <div className="space-y-3">
          {/* Travel Insurance */}
          <Card className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Travel Insurance</h3>
                <p className="text-sm text-blue-100 mb-3">Protect your trip with comprehensive coverage</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm">From $25/day</span>
                  <Button size="sm" className="bg-white text-blue-600 hover:bg-blue-50">
                    Get Quote
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* eSIM */}
          <Card className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <Smartphone className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">International eSIM</h3>
                <p className="text-sm text-purple-100 mb-3">Stay connected with affordable data plans</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm">From $15</span>
                  <Button size="sm" className="bg-white text-purple-600 hover:bg-purple-50">
                    Order Now
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Car Rental */}
          <Card className="p-4 bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <CarIcon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Car Rental & Insurance</h3>
                <p className="text-sm text-orange-100 mb-3">Explore at your own pace with rental cars</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm">From $40/day</span>
                  <Button size="sm" className="bg-white text-orange-600 hover:bg-orange-50">
                    Book Now
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Push Notification Setting */}
      <div className="px-6 py-4">
        <Card className="p-4 bg-yellow-50 border-yellow-200">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-xl">🔔</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1">Enable Trip Reminders</h3>
              <p className="text-sm text-gray-600 mb-3">
                Get notified about flight times, activity bookings, and important updates
              </p>
              <Button variant="outline" size="sm" className="w-full">
                Turn On Notifications
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}