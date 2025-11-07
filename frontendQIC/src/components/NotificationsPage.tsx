import { ArrowLeft, Bell, Calendar, Heart, MessageCircle, Plane, MapPin, Clock, Ticket } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { useNotifications, Notification } from '../contexts/NotificationContext';

interface NotificationsPageProps {
  onBack: () => void;
}

export function NotificationsPage({ onBack }: NotificationsPageProps) {
  const { notifications, markAsRead, markAllAsRead, unreadCount } = useNotifications();

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'trip':
        return <Plane className="w-5 h-5 text-blue-600" />;
      case 'like':
        return <Heart className="w-5 h-5 text-red-500" />;
      case 'comment':
        return <MessageCircle className="w-5 h-5 text-green-600" />;
      case 'reminder':
        return <Clock className="w-5 h-5 text-orange-600" />;
      case 'system':
        return <Bell className="w-5 h-5 text-purple-600" />;
      case 'event':
        return <Ticket className="w-5 h-5 text-blue-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const getNotificationBgColor = (type: Notification['type']) => {
    switch (type) {
      case 'trip':
        return 'bg-blue-100';
      case 'like':
        return 'bg-red-100';
      case 'comment':
        return 'bg-green-100';
      case 'reminder':
        return 'bg-orange-100';
      case 'system':
        return 'bg-purple-100';
      case 'event':
        return 'bg-blue-100';
      default:
        return 'bg-gray-100';
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-purple-50 to-white">
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
            <h1 className="text-lg sm:text-xl font-semibold">Notifications</h1>
            {unreadCount > 0 && (
              <p className="text-xs sm:text-sm text-gray-500">{unreadCount} unread</p>
            )}
          </div>
          <button 
            onClick={markAllAsRead}
            className="text-xs sm:text-sm text-blue-600 hover:text-blue-700 font-semibold"
          >
            Mark all read
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="px-4 sm:px-6 py-4 space-y-3">
        {notifications.map((notification) => (
          <Card
            key={notification.id}
            onClick={() => markAsRead(notification.id)}
            className={`p-3 sm:p-4 cursor-pointer hover:shadow-md transition-shadow ${
              !notification.isRead ? 'bg-blue-50/50 border-blue-200' : 'bg-white'
            }`}
          >
            <div className="flex gap-3">
              {/* Icon */}
              <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full ${getNotificationBgColor(notification.type)} flex items-center justify-center flex-shrink-0`}>
                {getNotificationIcon(notification.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h3 className="font-semibold text-sm sm:text-base truncate">{notification.title}</h3>
                  {!notification.isRead && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-1.5"></div>
                  )}
                </div>
                <p className="text-xs sm:text-sm text-gray-600 line-clamp-2 mb-2">
                  {notification.message}
                </p>
                <div className="flex items-center gap-2">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-500">{notification.time}</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Empty State (if no notifications) */}
      {notifications.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 sm:py-16 px-4">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Bell className="w-8 h-8 sm:w-10 sm:h-10 text-gray-400" />
          </div>
          <h3 className="font-semibold text-base sm:text-lg mb-2">No notifications</h3>
          <p className="text-xs sm:text-sm text-gray-500 text-center">
            You're all caught up! Check back later for updates.
          </p>
        </div>
      )}
    </div>
  );
}
