import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import ShareScreen from './src/screens/share.js';
import AskScreen from './src/screens/ask.js';
import { TokenProvider, LocationProvider } from './src/screens/Context.js';


const Tab = createBottomTabNavigator(); 

function CustomHeader() {
  return (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>GemiHub</Text>
    </View>
  );
}

function App(): React.JSX.Element {
  return (
    <LocationProvider>
      <TokenProvider>
        <CustomHeader />
        <NavigationContainer>
          <Tab.Navigator
            initialRouteName="Share"
            screenOptions={({ route }) => ({
              tabBarIcon: ({ color, size }) => {
                let iconName: string;

                if (route.name === 'Share') {
                  iconName = 'share-variant'; // 圖標名稱
                } else if (route.name === 'Ask') {
                  iconName = 'comment-question-outline'; // 圖標名稱
                }else {
                  iconName = 'help-circle'; // 預設圖標，防止 undefined
                }

                // 返回圖標組件
                return <MaterialCommunityIcons name={iconName} size={size} color={color} />;
              },
              tabBarActiveTintColor: '#F4D58D', // 活躍狀態的圖標顏色
              tabBarInactiveTintColor: '#001427', // 非活躍狀態的圖標顏色
            })}
          >
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
      </TokenProvider>
    </LocationProvider>
  );
}

const styles = StyleSheet.create({
  header: {
    backgroundColor: '#001427',  
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4, 
  },
  headerTitle: {
    color: '#F4D58D',
    fontSize: 20,
    fontWeight: 'bold',
  },
});

export default App;