import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, getAccessToken } from '../utils/api';

export interface UserProfile {
  username: string;
  fullName?: string;
  gender?: string;
  dateOfBirth?: string;
  countryOfResidence?: string;
  nationality?: string;
  dependants?: number;
  preferredLanguage?: string;
  avatar?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  login: (username: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (profile: Partial<UserProfile>) => void;
  isProfileComplete: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      const token = getAccessToken();
      if (token) {
        try {
          const userData: any = await authApi.getCurrentUser();
          setUser({ username: userData.username });
        } catch (error) {
          console.error('Failed to get user data:', error);
          authApi.logout();
        }
      }
      setIsLoading(false);
    };

    checkSession();
  }, []);

  const login = async (username: string) => {
    try {
      const response = await authApi.login(username);
      setUser({ username: response.username });
    } catch (error) {
      console.error('Login failed:', error);
      // Try registration if login fails
      try {
        const response = await authApi.register(username);
        setUser({ username: response.username });
      } catch (registerError) {
        console.error('Registration also failed:', registerError);
        throw new Error('Failed to login or register');
      }
    }
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const updateProfile = (profile: Partial<UserProfile>) => {
    if (user) {
      setUser({ ...user, ...profile });
    }
  };

  const isProfileComplete = !!(
    user?.fullName &&
    user?.gender &&
    user?.dateOfBirth &&
    user?.countryOfResidence &&
    user?.nationality &&
    user?.preferredLanguage
  );

  return (
    <AuthContext.Provider value={{ user, login, logout, updateProfile, isProfileComplete, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
