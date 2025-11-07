import { useEffect, useState } from 'react';
import { X, Calendar, Ticket } from 'lucide-react';
import { Card } from './ui/card';
import { useNotifications } from '../contexts/NotificationContext';

export function NotificationPopup() {
  const { notifications, markAsRead } = useNotifications();
  const [visibleNotification, setVisibleNotification] = useState<string | null>(null);

  useEffect(() => {
    // Show the most recent unread notification
    const unreadNotifications = notifications.filter(n => !n.isRead);
    if (unreadNotifications.length > 0) {
      const latest = unreadNotifications[0];
      if (visibleNotification !== latest.id) {
        setVisibleNotification(latest.id);
        
        // Auto-hide after 5 seconds
        const timer = setTimeout(() => {
          setVisibleNotification(null);
          markAsRead(latest.id);
        }, 5000);

        return () => clearTimeout(timer);
      }
    } else {
      setVisibleNotification(null);
    }
  }, [notifications, visibleNotification, markAsRead]);

  const currentNotification = notifications.find(n => n.id === visibleNotification);

  if (!currentNotification || currentNotification.isRead) {
    return null;
  }

  const handleClose = () => {
    markAsRead(currentNotification.id);
    setVisibleNotification(null);
  };

  return (
    <div
      className="fixed top-4 left-2 right-0 z-[10000] max-w-sm w-[calc(100%-2rem)]"
      style={{
        animation: 'slideIn 0.3s ease-out',
      }}
    >
      <Card className="p-4 shadow-2xl border-2 border-blue-200 bg-white">
        <div className="flex gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            {currentNotification.type === 'event' ? (
              <Ticket className="w-5 h-5 text-blue-600" />
            ) : (
              <Calendar className="w-5 h-5 text-blue-600" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h3 className="font-semibold text-sm">{currentNotification.title}</h3>
              <button
                onClick={handleClose}
                className="w-5 h-5 rounded-full hover:bg-gray-100 flex items-center justify-center flex-shrink-0 transition-colors"
                aria-label="Close notification"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            </div>
            <p className="text-xs text-gray-600 line-clamp-2 mb-2">
              {currentNotification.message}
            </p>
            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-500">{currentNotification.time}</span>
            </div>
          </div>
        </div>
      </Card>
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

