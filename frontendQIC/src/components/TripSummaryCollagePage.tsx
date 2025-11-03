import { ArrowLeft, Download, Share2, Instagram, Facebook, Twitter } from 'lucide-react';
import { useRef } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface TripSummaryCollagePageProps {
  onBack: () => void;
  tripData: {
    destination: string;
    dates: string;
    images: string[];
    activities: string[];
  };
}

export function TripSummaryCollagePage({ onBack, tripData }: TripSummaryCollagePageProps) {
  const collageRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    // In a real app, you would use html2canvas or similar library to convert the collage to an image
    // For now, we'll just show an alert
    alert('In a real app, this would download the collage as an image file');
  };

  const handleShare = (platform: string) => {
    alert(`Share to ${platform} - In a real app, this would open the share dialog`);
  };

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
            <h1 className="text-xl font-semibold">Trip Summary</h1>
            <p className="text-sm text-gray-500">Ready to share!</p>
          </div>
        </div>
      </div>

      {/* Collage Container */}
      <div className="px-6 py-6">
        <div 
          ref={collageRef}
          className="bg-white rounded-2xl shadow-2xl overflow-hidden mb-6"
        >
          {/* Header Section with Gradient */}
          <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 p-6 text-white">
            <h2 className="text-2xl font-bold mb-2">{tripData.destination}</h2>
            <p className="text-purple-100">{tripData.dates}</p>
            <div className="mt-4 flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <span className="text-xl">✈️</span>
              </div>
              <span className="text-sm">An Unforgettable Journey</span>
            </div>
          </div>

          {/* Image Collage Grid */}
          <div className="p-4">
            <div className="grid grid-cols-6 gap-2 mb-4">
              {/* Large image on the left */}
              <div className="col-span-4 row-span-2 rounded-lg overflow-hidden">
                <ImageWithFallback 
                  src={tripData.images[0]}
                  alt="Main trip photo"
                  className="w-full h-full object-cover"
                />
              </div>
              
              {/* Two smaller images on top right */}
              <div className="col-span-2 rounded-lg overflow-hidden aspect-square">
                <ImageWithFallback 
                  src={tripData.images[1]}
                  alt="Trip photo 2"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="col-span-2 rounded-lg overflow-hidden aspect-square">
                <ImageWithFallback 
                  src={tripData.images[2]}
                  alt="Trip photo 3"
                  className="w-full h-full object-cover"
                />
              </div>
              
              {/* Three images on bottom */}
              <div className="col-span-3 rounded-lg overflow-hidden aspect-video">
                <ImageWithFallback 
                  src={tripData.images[3]}
                  alt="Trip photo 4"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="col-span-3 rounded-lg overflow-hidden aspect-video">
                <ImageWithFallback 
                  src={tripData.images[4]}
                  alt="Trip photo 5"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Activities Section */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 mb-4">
              <h3 className="font-semibold mb-3 text-purple-900">Trip Highlights</h3>
              <div className="grid grid-cols-2 gap-2">
                {tripData.activities.map((activity, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-2 bg-white rounded-lg p-2 shadow-sm"
                  >
                    <div className="w-6 h-6 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs">✓</span>
                    </div>
                    <span className="text-xs">{activity}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Trip Description */}
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-sm text-gray-700 leading-relaxed">
                An incredible journey filled with amazing experiences, unforgettable moments, 
                and beautiful memories. From exploring new places to trying local cuisine, 
                every moment was a treasure. This trip will always hold a special place in my heart.
              </p>
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                    <span className="text-white text-xs">QC</span>
                  </div>
                  <span className="text-xs text-gray-600">Created with Qico</span>
                </div>
                <span className="text-xs text-gray-500">Nov 2025</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={handleDownload}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Summary
          </Button>

          {/* Social Share Buttons */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3 text-center">Share Your Journey</h3>
            <div className="grid grid-cols-3 gap-3">
              <Button
                onClick={() => handleShare('Instagram')}
                className="flex flex-col items-center gap-2 h-auto py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                <Instagram className="w-6 h-6" />
                <span className="text-xs">Instagram</span>
              </Button>
              <Button
                onClick={() => handleShare('Facebook')}
                className="flex flex-col items-center gap-2 h-auto py-3 bg-blue-600 hover:bg-blue-700"
              >
                <Facebook className="w-6 h-6" />
                <span className="text-xs">Facebook</span>
              </Button>
              <Button
                onClick={() => handleShare('Twitter')}
                className="flex flex-col items-center gap-2 h-auto py-3 bg-sky-500 hover:bg-sky-600"
              >
                <Twitter className="w-6 h-6" />
                <span className="text-xs">Twitter</span>
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
