import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { FavouritesProvider, useFavourites } from './contexts/FavouritesContext';
import { LoginPage } from './components/LoginPage';
import { MainPage } from './components/MainPage';
import { ProfilePage } from './components/ProfilePage';
import { TravelPage } from './components/TravelPage';
import { EventPage } from './components/EventPage';
import { MapPage } from './components/MapPage';
import { IslamPage } from './components/IslamPage';
import { CarPage } from './components/CarPage';
import { TripChatPage } from './components/TripChatPage';
import { TripPlannerStepByStepPage } from './components/TripPlannerStepByStepPage';
import { TripDetailPage } from './components/TripDetailPage';
import { TripChecklistPage } from './components/TripChecklistPage';
import { TripHistoryPage } from './components/TripHistoryPage';
import { TripCalendarPage } from './components/TripCalendarPage';
import { PopularPlanDetailPage } from './components/PopularPlanDetailPage';
import { FavouritesPage } from './components/FavouritesPage';
import { NotificationsPage } from './components/NotificationsPage';
import { ImportantNotesPage } from './components/ImportantNotesPage';
import { TripGeneratingPage } from './components/TripGeneratingPage';
import { TripSummaryUploadPage } from './components/TripSummaryUploadPage';
import { TripSummaryCollagePage } from './components/TripSummaryCollagePage';

type PageType = 
  | 'main' 
  | 'profile'
  | 'travel' 
  | 'event' 
  | 'map' 
  | 'islam' 
  | 'car'
  | 'trip-chat'
  | 'trip-generating'
  | 'trip-planner'
  | 'trip-detail'
  | 'trip-checklist'
  | 'trip-history'
  | 'trip-calendar'
  | 'popular-plan-detail'
  | 'favourites'
  | 'notifications'
  | 'important-notes'
  | 'trip-summary-upload'
  | 'trip-summary-collage';

function AppContent() {
  const { user, login, isProfileComplete, isLoading } = useAuth();
  const { favouritePlans, toggleFavourite } = useFavourites();
  const [currentPage, setCurrentPage] = useState<PageType>('main');
  const [tripData, setTripData] = useState<any>(null);
  const [selectedOptions, setSelectedOptions] = useState<any>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const [tripSummaryData, setTripSummaryData] = useState<any>(null);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If not logged in, show login page
  if (!user) {
    return <LoginPage onLogin={login} />;
  }

  const handleNavigate = (page: PageType) => {
    setCurrentPage(page);
  };

  const handleTripChatComplete = (data: any) => {
    setTripData(data);
    setCurrentPage('trip-generating');
    
    // Show loading for 3 seconds before showing the planner
    setTimeout(() => {
      setCurrentPage('trip-planner');
    }, 3000);
  };

  const handleTripPlannerConfirm = (options: any) => {
    setSelectedOptions(options);
    setCurrentPage('trip-detail');
  };

  const handleViewPopularPlan = (planId: number) => {
    setSelectedPlanId(planId);
    setCurrentPage('popular-plan-detail');
  };

  const handleTripSummary = (tripId: string) => {
    setSelectedTripId(tripId);
    setCurrentPage('trip-summary-upload');
  };

  const handleTripSummaryUploadComplete = (data: { images: string[]; activities: string[] }) => {
    // Mock trip data - in a real app, this would be fetched based on selectedTripId
    const mockTripData = {
      destination: 'Bali, Indonesia',
      dates: 'Oct 1-8, 2025',
      images: data.images,
      activities: data.activities
    };
    setTripSummaryData(mockTripData);
    setCurrentPage('trip-summary-collage');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {currentPage === 'main' && (
        <MainPage 
          onNavigate={(page) => handleNavigate(page as PageType)} 
          showProfileNotice={!isProfileComplete}
        />
      )}

      {currentPage === 'profile' && (
        <ProfilePage 
          onBack={() => handleNavigate('main')}
          onNavigateToFavourites={() => handleNavigate('favourites')}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}
      
      {currentPage === 'travel' && (
        <TravelPage 
          onBack={() => handleNavigate('main')}
          onStartNewTrip={() => handleNavigate('trip-chat')}
          onViewTrip={(tripId) => handleNavigate('trip-history')}
          onViewHistory={() => handleNavigate('trip-history')}
          onViewPopularPlan={handleViewPopularPlan}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'popular-plan-detail' && selectedPlanId && (
        <PopularPlanDetailPage 
          onBack={() => handleNavigate('travel')}
          planId={selectedPlanId}
        />
      )}

      {currentPage === 'favourites' && (
        <FavouritesPage 
          onBack={() => handleNavigate('profile')}
          onViewPlan={handleViewPopularPlan}
          favouritePlans={favouritePlans}
          onRemoveFavourite={toggleFavourite}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}
      
      {currentPage === 'event' && (
        <EventPage onBack={() => handleNavigate('main')} />
      )}
      
      {currentPage === 'map' && (
        <MapPage onBack={() => handleNavigate('main')} />
      )}
      
      {currentPage === 'islam' && (
        <IslamPage onBack={() => handleNavigate('main')} />
      )}
      
      {currentPage === 'car' && (
        <CarPage onBack={() => handleNavigate('main')} />
      )}

      {currentPage === 'trip-chat' && (
        <TripChatPage 
          onBack={() => handleNavigate('travel')}
          onComplete={handleTripChatComplete}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'trip-generating' && (
        <TripGeneratingPage 
          destination={tripData?.toCity}
        />
      )}

      {currentPage === 'trip-planner' && tripData && (
        <TripPlannerStepByStepPage 
          onBack={() => handleNavigate('trip-chat')}
          tripData={tripData}
          onConfirm={handleTripPlannerConfirm}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'trip-history' && (
        <TripHistoryPage 
          onBack={() => handleNavigate('travel')}
          onViewTrip={(tripId) => handleNavigate('trip-calendar')}
          onCreateNewTrip={() => handleNavigate('trip-chat')}
          onNotifications={() => handleNavigate('notifications')}
          onTripSummary={handleTripSummary}
        />
      )}

      {currentPage === 'trip-calendar' && (
        <TripCalendarPage 
          onBack={() => handleNavigate('trip-history')}
          onChecklistClick={() => handleNavigate('trip-checklist')}
          onDayClick={(date) => handleNavigate('trip-detail')}
          onImportantNotesClick={() => handleNavigate('important-notes')}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'trip-detail' && (
        <TripDetailPage 
          onBack={() => handleNavigate('travel')}
          onChecklistClick={() => handleNavigate('trip-checklist')}
          onCalendarClick={() => handleNavigate('trip-calendar')}
          tripDetails={{ tripData, selectedOptions }}
        />
      )}

      {currentPage === 'trip-checklist' && (
        <TripChecklistPage 
          onBack={() => handleNavigate('trip-calendar')}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'notifications' && (
        <NotificationsPage 
          onBack={() => handleNavigate('main')}
        />
      )}

      {currentPage === 'important-notes' && (
        <ImportantNotesPage 
          onBack={() => handleNavigate('trip-calendar')}
          onNotifications={() => handleNavigate('notifications')}
        />
      )}

      {currentPage === 'trip-summary-upload' && selectedTripId && (
        <TripSummaryUploadPage 
          onBack={() => handleNavigate('trip-history')}
          onComplete={handleTripSummaryUploadComplete}
          tripId={selectedTripId}
        />
      )}

      {currentPage === 'trip-summary-collage' && tripSummaryData && (
        <TripSummaryCollagePage 
          onBack={() => handleNavigate('trip-history')}
          tripData={tripSummaryData}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <FavouritesProvider>
        <AppContent />
      </FavouritesProvider>
    </AuthProvider>
  );
}