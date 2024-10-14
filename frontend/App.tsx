import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ShareScreen from './src/screens/share.js';
import AskScreen from './src/screens/ask.js';


const Tab = createBottomTabNavigator(); 

function App(): React.JSX.Element {
  return (
    <NavigationContainer>
      <Tab.Navigator initialRouteName="GoogleMaps">
        <Tab.Screen 
          name="Share" 
          component={ShareScreen} 
          options={{ headerShown: false }} 
        />
        <Tab.Screen 
          name="Ask" 
          component={AskScreen} 
          options={{ headerShown: false }} 
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

export default App;