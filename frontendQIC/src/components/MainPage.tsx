import {
  Plane,
  Calendar,
  Map,
  Moon,
  Car,
  User,
  Bell,
  X,
  ChevronRight,
} from "lucide-react";
import { Card } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { useState } from "react";

interface MainPageProps {
  onNavigate: (
    page:
      | "travel"
      | "event"
      | "map"
      | "islam"
      | "car"
      | "profile"
      | "notifications",
  ) => void;
  showProfileNotice?: boolean;
}

export function MainPage({
  onNavigate,
  showProfileNotice = true,
}: MainPageProps) {
  const [isNoticeDismissed, setIsNoticeDismissed] =
    useState(false);

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-purple-50 to-white">
      {/* Header */}
      <div className="px-6 py-4 flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">Welcome back</p>
          <h1 className="text-2xl font-bold">QICO</h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate("notifications")}
            className="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center relative hover:bg-gray-50 transition-colors"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <button
            onClick={() => onNavigate("profile")}
            className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center hover:scale-105 transition-transform"
          >
            <User className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>

      {/* Profile Completion Notice */}
      {showProfileNotice && !isNoticeDismissed && (
        <div className="px-6 pb-4">
          <Alert className="bg-blue-50 border-blue-200 !px-6 py-3">
            <div className="flex gap-3 w-full">
              <div className="flex-1">
                <AlertDescription className="col-start-1">
                  <p className="font-semibold text-blue-900 text-sm">
                    Complete your profile
                  </p>
                  <p className="text-blue-700 mt-1 text-sm">
                    Get more accurate recommendations by filling
                    out your profile details.
                  </p>
                  <button
                    onClick={() => onNavigate("profile")}
                    className="text-blue-600 hover:text-blue-700 font-semibold mt-2 flex items-center gap-1 text-sm"
                  >
                    Go to Profile
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </AlertDescription>
              </div>
              <button
                onClick={() => setIsNoticeDismissed(true)}
                className="flex-shrink-0 text-blue-600 hover:text-blue-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </Alert>
        </div>
      )}

      {/* Hero Section */}
      <div className="px-6 py-6">
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl p-6 text-white shadow-lg">
          <h2 className="text-xl mb-2">
            Explore Your Lifestyle
          </h2>
          <p className="text-indigo-100 text-sm">
            Discover travel, events, and services all in one
            place
          </p>
        </div>
      </div>

      {/* Main Categories */}
      <div className="px-6 py-4">
        <h3 className="text-lg font-semibold mb-4">
          Categories
        </h3>
        <div className="grid grid-cols-2 gap-4">
          {/* Travel Card */}
          <Card
            className="p-6 bg-gradient-to-br from-blue-500 to-cyan-400 border-0 cursor-pointer hover:scale-105 transition-transform shadow-lg"
            onClick={() => onNavigate("travel")}
          >
            <div className="flex flex-col items-center text-white">
              <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-3 backdrop-blur-sm">
                <Plane className="w-7 h-7" />
              </div>
              <span className="font-semibold">Travel</span>
            </div>
          </Card>

          {/* Event Card */}
          <Card
            className="p-6 bg-gradient-to-br from-purple-500 to-pink-400 border-0 cursor-pointer hover:scale-105 transition-transform shadow-lg"
            onClick={() => onNavigate("event")}
          >
            <div className="flex flex-col items-center text-white">
              <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-3 backdrop-blur-sm">
                <Calendar className="w-7 h-7" />
              </div>
              <span className="font-semibold">Event</span>
            </div>
          </Card>

          {/* Map Card */}
          <Card
            className="p-6 bg-gradient-to-br from-green-500 to-emerald-400 border-0 cursor-pointer hover:scale-105 transition-transform shadow-lg"
            onClick={() => onNavigate("map")}
          >
            <div className="flex flex-col items-center text-white">
              <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-3 backdrop-blur-sm">
                <Map className="w-7 h-7" />
              </div>
              <span className="font-semibold">Map</span>
            </div>
          </Card>

          {/* Islam Card */}
          <Card
            className="p-6 bg-gradient-to-br from-teal-500 to-cyan-600 border-0 cursor-pointer hover:scale-105 transition-transform shadow-lg"
            onClick={() => onNavigate("islam")}
          >
            <div className="flex flex-col items-center text-white">
              <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-3 backdrop-blur-sm">
                <Moon className="w-7 h-7" />
              </div>
              <span className="font-semibold">Islam</span>
            </div>
          </Card>
        </div>
      </div>

      {/* Car Services Section */}
      <div className="px-6 py-4 mb-6">
        <h3 className="text-lg font-semibold mb-4">
          Car Services
        </h3>
        <Card
          className="p-5 bg-gradient-to-r from-slate-700 to-slate-500 border-0 cursor-pointer hover:scale-[1.02] transition-transform shadow-lg"
          onClick={() => onNavigate("car")}
        >
          <div className="flex items-center justify-between text-white">
            <div>
              <h4 className="font-semibold mb-1">
                Vehicle Services
              </h4>
              <p className="text-slate-200 text-sm">
                Rental, repair, wash & more
              </p>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <Car className="w-6 h-6" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}