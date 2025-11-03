import { ArrowLeft, Upload, X, Check } from 'lucide-react';
import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface TripSummaryUploadPageProps {
  onBack: () => void;
  onComplete: (data: { images: string[]; activities: string[] }) => void;
  tripId: number;
}

export function TripSummaryUploadPage({ onBack, onComplete, tripId }: TripSummaryUploadPageProps) {
  const [uploadedImages, setUploadedImages] = useState<string[]>([]);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);

  // Mock trip activities - in real app, this would be fetched based on tripId
  const tripActivities = [
    'Desert Safari',
    'Burj Khalifa Visit',
    'Dubai Marina Cruise',
    'Traditional Souk Tour',
    'Beach Activities',
    'Fine Dining Experience',
    'Shopping at Dubai Mall',
    'Museum Visit'
  ];

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      // In a real app, you would upload these to a server
      // For demo, we'll use placeholder images
      const newImages = Array.from(files).slice(0, 5 - uploadedImages.length).map((_, index) => {
        // Using different Unsplash images as placeholders
        const imageIds = [
          'photo-1512453979798-5ea266f8880c',
          'photo-1582672060674-bc2bd808a8b5',
          'photo-1518684079-3c830dcef090',
          'photo-1559827260-dc66d52bef19',
          'photo-1566073771259-6a8506099945'
        ];
        return `https://images.unsplash.com/${imageIds[uploadedImages.length + index]}?w=400&h=400&fit=crop`;
      });
      setUploadedImages([...uploadedImages, ...newImages]);
    }
  };

  const removeImage = (index: number) => {
    setUploadedImages(uploadedImages.filter((_, i) => i !== index));
  };

  const toggleActivity = (activity: string) => {
    if (selectedActivities.includes(activity)) {
      setSelectedActivities(selectedActivities.filter(a => a !== activity));
    } else {
      setSelectedActivities([...selectedActivities, activity]);
    }
  };

  const handleContinue = () => {
    if (uploadedImages.length === 5 && selectedActivities.length > 0) {
      onComplete({ images: uploadedImages, activities: selectedActivities });
    }
  };

  const isComplete = uploadedImages.length === 5 && selectedActivities.length > 0;

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-purple-50 to-white pb-24">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-semibold">Create Trip Summary</h1>
            <p className="text-sm text-gray-500">Share your memories</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 py-6">
        {/* Image Upload Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Upload 5 Photos</h2>
            <span className="text-sm text-gray-600">{uploadedImages.length}/5</span>
          </div>

          {/* Image Grid */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            {uploadedImages.map((image, index) => (
              <div key={index} className="relative aspect-square">
                <ImageWithFallback 
                  src={image}
                  alt={`Uploaded ${index + 1}`}
                  className="w-full h-full object-cover rounded-lg"
                />
                <button
                  onClick={() => removeImage(index)}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
            
            {/* Upload placeholder boxes */}
            {Array.from({ length: 5 - uploadedImages.length }).map((_, index) => (
              <label 
                key={`placeholder-${index}`}
                className="aspect-square border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-purple-400 hover:bg-purple-50 transition-colors"
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  multiple
                />
                <Upload className="w-8 h-8 text-gray-400" />
              </label>
            ))}
          </div>

          <p className="text-xs text-gray-500 text-center">
            Upload high-quality photos from your trip
          </p>
        </div>

        {/* Activities Selection */}
        <div className="mb-6">
          <h2 className="font-semibold mb-4">Select Activities You Did</h2>
          <p className="text-sm text-gray-600 mb-4">Choose the highlights of your trip</p>

          <div className="grid grid-cols-2 gap-3">
            {tripActivities.map((activity) => (
              <Card
                key={activity}
                onClick={() => toggleActivity(activity)}
                className={`p-4 cursor-pointer transition-all ${
                  selectedActivities.includes(activity)
                    ? 'border-2 border-purple-600 bg-purple-50'
                    : 'border hover:border-purple-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    selectedActivities.includes(activity)
                      ? 'border-purple-600 bg-purple-600'
                      : 'border-gray-300'
                  }`}>
                    {selectedActivities.includes(activity) && (
                      <Check className="w-3 h-3 text-white" />
                    )}
                  </div>
                  <span className="text-sm">{activity}</span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
        <div className="max-w-md mx-auto">
          <Button
            onClick={handleContinue}
            disabled={!isComplete}
            className={`w-full h-12 ${
              isComplete
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                : 'bg-gray-300'
            }`}
          >
            {isComplete 
              ? 'Create Summary Collage' 
              : `Upload ${5 - uploadedImages.length} more image${5 - uploadedImages.length !== 1 ? 's' : ''} and select activities`}
          </Button>
        </div>
      </div>
    </div>
  );
}
