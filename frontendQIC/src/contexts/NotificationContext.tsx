import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

export interface Notification {
  id: string;
  type: 'trip' | 'like' | 'comment' | 'system' | 'reminder' | 'event';
  title: string;
  message: string;
  time: string;
  timestamp: Date;
  isRead: boolean;
  icon?: string;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  unreadCount: number;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}

const MOCK_EVENT_NOTIFICATIONS = [
  {
    type: 'event' as const,
    title: 'Concert Alert',
    message: 'Taylor Swift concert tickets are now available! Go buy tickets before they sell out.',
  },
  {
    type: 'event' as const,
    title: 'Sports Event',
    message: 'Champions League final tickets are on sale! Don\'t miss this exciting match.',
  },
  {
    type: 'event' as const,
    title: 'Music Festival',
    message: 'Coachella 2025 tickets are available now! Book your spot for the biggest music festival.',
  },
  {
    type: 'event' as const,
    title: 'Theater Show',
    message: 'Hamilton tickets are now available! Experience the award-winning musical.',
  },
  {
    type: 'event' as const,
    title: 'Comedy Show',
    message: 'Stand-up comedy night tickets are on sale! Get ready for a night of laughter.',
  },
  {
    type: 'event' as const,
    title: 'Food Festival',
    message: 'International Food Festival tickets available! Taste cuisines from around the world.',
  },
  {
    type: 'event' as const,
    title: 'Art Exhibition',
    message: 'Van Gogh immersive experience tickets on sale! Don\'t miss this unique art event.',
  },
  {
    type: 'event' as const,
    title: 'Tech Conference',
    message: 'Tech Summit 2025 tickets are available! Join industry leaders and innovators.',
  },
];

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  }
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'isRead'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      isRead: false,
      time: 'Just now',
    };
    
    setNotifications(prev => [newNotification, ...prev]);
    
    // Update time format after a moment
    setTimeout(() => {
      setNotifications(prev =>
        prev.map(n =>
          n.id === newNotification.id
            ? { ...n, time: formatTimeAgo(n.timestamp) }
            : n
        )
      );
    }, 1000);
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, isRead: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  }, []);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  // Generate random notifications every 30-60 seconds
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    
    const scheduleNextNotification = () => {
      const delay = 30000 + Math.random() * 30000; // 30-60 seconds
      timeoutId = setTimeout(() => {
        const randomEvent = MOCK_EVENT_NOTIFICATIONS[
          Math.floor(Math.random() * MOCK_EVENT_NOTIFICATIONS.length)
        ];
        addNotification(randomEvent);
        scheduleNextNotification(); // Schedule the next one
      }, delay);
    };

    // Start scheduling notifications
    scheduleNextNotification();

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [addNotification]);

  // Update time strings periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setNotifications(prev =>
        prev.map(n => ({
          ...n,
          time: formatTimeAgo(n.timestamp),
        }))
      );
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        markAsRead,
        markAllAsRead,
        unreadCount,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

