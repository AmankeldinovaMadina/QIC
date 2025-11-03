import { useState } from 'react';
import { ArrowLeft, User, LogOut, Camera, Bell, Save, Heart, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useAuth } from '../contexts/AuthContext';
import { useFavourites } from '../contexts/FavouritesContext';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface ProfilePageProps {
  onBack: () => void;
  onNavigateToFavourites?: () => void;
  onNotifications: () => void;
}

export function ProfilePage({ onBack, onNavigateToFavourites, onNotifications }: ProfilePageProps) {
  const { user, logout, updateProfile } = useAuth();
  const { favouritePlans } = useFavourites();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: user?.fullName || '',
    gender: user?.gender || '',
    dateOfBirth: user?.dateOfBirth || '',
    countryOfResidence: user?.countryOfResidence || '',
    nationality: user?.nationality || '',
    dependants: user?.dependants?.toString() || '0',
    preferredLanguage: user?.preferredLanguage || 'English',
    avatar: user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username}`
  });

  const handleSave = () => {
    updateProfile({
      ...formData,
      dependants: parseInt(formData.dependants) || 0
    });
    setIsEditing(false);
  };

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  const countries = [
    'Qatar', 'United Arab Emirates', 'Saudi Arabia', 'Kuwait', 'Bahrain', 'Oman',
    'United States', 'United Kingdom', 'France', 'Germany', 'India', 'Pakistan',
    'Philippines', 'Egypt', 'Jordan', 'Lebanon', 'Turkey', 'Other'
  ];

  const languages = ['English', 'Arabic', 'French', 'Spanish', 'German', 'Urdu', 'Hindi', 'Filipino'];

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-purple-50 to-white">
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
            <h1 className="text-xl font-semibold">Profile</h1>
            <p className="text-sm text-gray-500">Manage your account</p>
          </div>
          <button 
            onClick={onNotifications}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>
      </div>

      <div className="px-6 py-6 space-y-6">
        {/* Avatar Section */}
        <Card className="p-6">
          <div className="flex flex-col items-center">
            <div className="relative">
              <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-white shadow-lg">
                <ImageWithFallback
                  src={formData.avatar}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              </div>
              {isEditing && (
                <button className="absolute bottom-0 right-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center shadow-lg hover:bg-blue-700">
                  <Camera className="w-4 h-4 text-white" />
                </button>
              )}
            </div>
            <div className="mt-4 text-center">
              <h2 className="font-semibold text-lg">{formData.fullName || 'Complete your profile'}</h2>
              <p className="text-sm text-gray-500">@{user?.username}</p>
            </div>
          </div>
        </Card>

        {/* Personal Information */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Personal Information</h3>
            {!isEditing ? (
              <Button
                onClick={() => setIsEditing(true)}
                variant="outline"
                size="sm"
              >
                Edit
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    setIsEditing(false);
                    setFormData({
                      fullName: user?.fullName || '',
                      gender: user?.gender || '',
                      dateOfBirth: user?.dateOfBirth || '',
                      countryOfResidence: user?.countryOfResidence || '',
                      nationality: user?.nationality || '',
                      dependants: user?.dependants?.toString() || '0',
                      preferredLanguage: user?.preferredLanguage || 'English',
                      avatar: user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username}`
                    });
                  }}
                  variant="outline"
                  size="sm"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSave}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </Button>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="fullName">Full Name *</Label>
              <Input
                id="fullName"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                disabled={!isEditing}
                placeholder="Enter your full name"
              />
            </div>

            <div>
              <Label htmlFor="gender">Gender *</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => setFormData({ ...formData, gender: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Male">Male</SelectItem>
                  <SelectItem value="Female">Female</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                  <SelectItem value="Prefer not to say">Prefer not to say</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="dateOfBirth">Date of Birth *</Label>
              <Input
                id="dateOfBirth"
                type="date"
                value={formData.dateOfBirth}
                onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="countryOfResidence">Country of Residence *</Label>
              <Select
                value={formData.countryOfResidence}
                onValueChange={(value) => setFormData({ ...formData, countryOfResidence: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select country" />
                </SelectTrigger>
                <SelectContent>
                  {countries.map((country) => (
                    <SelectItem key={country} value={country}>
                      {country}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="nationality">Nationality *</Label>
              <Select
                value={formData.nationality}
                onValueChange={(value) => setFormData({ ...formData, nationality: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select nationality" />
                </SelectTrigger>
                <SelectContent>
                  {countries.map((country) => (
                    <SelectItem key={country} value={country}>
                      {country}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="dependants">Dependants/Children</Label>
              <Select
                value={formData.dependants}
                onValueChange={(value) => setFormData({ ...formData, dependants: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select number" />
                </SelectTrigger>
                <SelectContent>
                  {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                    <SelectItem key={num} value={num.toString()}>
                      {num}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="preferredLanguage">Preferred Language *</Label>
              <Select
                value={formData.preferredLanguage}
                onValueChange={(value) => setFormData({ ...formData, preferredLanguage: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang} value={lang}>
                      {lang}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        {/* Quick Actions */}
        <Card className="p-4">
          <h3 className="font-semibold mb-3">Quick Actions</h3>
          <button
            onClick={onNavigateToFavourites}
            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Heart className="w-5 h-5 text-red-500" />
              </div>
              <div className="text-left">
                <p className="font-semibold text-sm">Favourite Trips</p>
                <p className="text-xs text-gray-500">{favouritePlans.length} saved plans</p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        </Card>

        {/* Logout Button */}
        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 h-12"
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
}
