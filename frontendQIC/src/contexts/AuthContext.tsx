import { createContext, useContext, useState, ReactNode } from 'react';

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
  login: (username: string) => void;
  logout: () => void;
  updateProfile: (profile: Partial<UserProfile>) => void;
  isProfileComplete: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);

  const login = (username: string) => {
    setUser({ username });
  };

  const logout = () => {
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
    <AuthContext.Provider value={{ user, login, logout, updateProfile, isProfileComplete }}>
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
