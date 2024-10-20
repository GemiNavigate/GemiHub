import React, { createContext, useState } from 'react';

export const TokenContext = createContext();
export const LocationContext = createContext();

export const TokenProvider = ({ children }) => {
    const [tokens, setTokens] = useState(100); 

    return (
        <TokenContext.Provider value={{ tokens, setTokens }}>
            {children}
        </TokenContext.Provider>
    );
};

export const LocationProvider = ({ children }) => {
  const [currentLocation, setCurrentLocation] = useState(null);

  return (
    <LocationContext.Provider value={{ currentLocation, setCurrentLocation }}>
      {children}
    </LocationContext.Provider>
  );
};
