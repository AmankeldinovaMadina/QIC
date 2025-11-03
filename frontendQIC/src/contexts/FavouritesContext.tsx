import { createContext, useContext, useState, ReactNode } from 'react';

interface FavouritesContextType {
  favouritePlans: number[];
  toggleFavourite: (planId: number) => void;
  isFavourite: (planId: number) => boolean;
}

const FavouritesContext = createContext<FavouritesContextType | undefined>(undefined);

export function FavouritesProvider({ children }: { children: ReactNode }) {
  const [favouritePlans, setFavouritePlans] = useState<number[]>([]);

  const toggleFavourite = (planId: number) => {
    setFavouritePlans(prev => 
      prev.includes(planId) 
        ? prev.filter(id => id !== planId)
        : [...prev, planId]
    );
  };

  const isFavourite = (planId: number) => {
    return favouritePlans.includes(planId);
  };

  return (
    <FavouritesContext.Provider value={{ favouritePlans, toggleFavourite, isFavourite }}>
      {children}
    </FavouritesContext.Provider>
  );
}

export function useFavourites() {
  const context = useContext(FavouritesContext);
  if (context === undefined) {
    throw new Error('useFavourites must be used within a FavouritesProvider');
  }
  return context;
}
