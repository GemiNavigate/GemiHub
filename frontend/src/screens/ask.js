import React, { useState, useRef, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, Dimensions, TouchableOpacity, TextInput, FlatList, Platform, PermissionsAndroid } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import Geolocation from '@react-native-community/geolocation';
import GetLocation from 'react-native-get-location';
import { TokenContext, LocationContext } from './Context';

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    chatContainer: {
        flex: 1,
        paddingHorizontal: 10,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 10,
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    input: { // 輸入框
        flex: 1,
        height: 50,
        borderColor: '#e0e0e0',
        borderWidth: 1,
        borderRadius: 20,
        paddingHorizontal: 15,
        marginRight: 10,
        fontSize: 16,
    },
   
    sendButton: {
        backgroundColor: '#708D81',
        borderRadius: 20, 
        padding: 10, 
    },
    // 訊息容器樣式
    messageContainer: {
        maxWidth: '70%',
        padding: 10,
        borderRadius: 10,
        marginVertical: 5,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    userMessage: {
        alignSelf: 'flex-end',
        backgroundColor: '#708D81',
    },
    systemMessage: {
        alignSelf: 'flex-start',
        backgroundColor: '#fff',
    },
    messageText: {
        fontSize: 16,
        flex: 1,
    },
    userMessageText: {
        color: '#fff',
    },
    systemMessageText: {
        color: '#000',
    },
    mapButton: {
        marginLeft: 10,
    },

    // 地圖相關樣式
    mapContainer: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)', // 半透明背景
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },

    mapContent: {
        width: '100%',
        height: '100%',
        backgroundColor: 'white',
        borderRadius: 0,
        overflow: 'hidden',
    },
    mapView: {
        width: '100%',
        height: '100%',
    },
    // 關閉按鈕樣式
    closeButton: {
        position: 'absolute',
        top: 10,
        right: 10,
        backgroundColor: 'white',
        borderRadius: 15,
        padding: 8,
        zIndex: 1,
        // 陰影效果
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
        elevation: 5,
    },
    tokenContainer: {
      position: 'absolute',
      top: 30, 
      left: 10, 
      padding: 10,
      backgroundColor: '#fff',
      borderRadius: 10,
      flexDirection: 'row',
      alignItems: 'center',
      elevation: 5,
    },
    tokenText: {
        color: '#001427',
        fontSize: 18,
        fontWeight: 'bold',
        marginRight: 5,
    },
    tokenIcon: {
        marginRight: 5,
    },
});


export default function AskerScreen() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [showMap, setShowMap] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [permissionGranter, setPermissionGranter] = useState(false);
  const { tokens, setTokens } = useContext(TokenContext);
  const flatListRef = useRef(null);
  const mapRef = useRef(null);

   /* tokens */
  const decreaseTokens = () => {
    if (tokens > 0) {
        setTokens(tokens - 10); 
    }
  };

  useEffect(() => {
      _getLocationPermission();
  }, []);

  useEffect(() => {
      if (permissionGranter) {
          _getCurrentLocation();
      }
  }, [permissionGranter]);

  async function _getLocationPermission() {
      if (Platform.OS === 'android') {
          try {
              const granted = await PermissionsAndroid.request(
                  PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
                  {
                      title: 'Location Permission',
                      message: 'Please allow permission to continue...',
                      buttonNeutral: 'Ask Me Later',
                      buttonNegative: 'Cancel',
                      buttonPositive: 'OK',
                  },
              );
              if (granted === PermissionsAndroid.RESULTS.GRANTED) {
                  setPermissionGranter(true);
              } else {
                  console.log('Location permission denied');
                  setPermissionGranter(false);
              }
          } catch (err) {
              console.warn(err);
          }
      }
  }

  async function _getCurrentLocation() {
      try {
          const location = await GetLocation.getCurrentPosition({
              enableHighAccuracy: true,
              timeout: 60000,
          });
          const currentCoordinate = {
              latitude: location.latitude,
              longitude: location.longitude,
          };
          setCurrentLocation(currentCoordinate);
          moveToLocation(currentCoordinate.latitude, currentCoordinate.longitude);
      } catch (error) {
          console.warn('Error getting current location:', error);
          const defaultLocation = {
              latitude: 24.787926,
              longitude: 120.997576,
          };
          setCurrentLocation(defaultLocation);
          moveToLocation(defaultLocation.latitude, defaultLocation.longitude);
      }
  }

  async function moveToLocation(latitude, longitude) {
      mapRef.current?.animateToRegion(
          {
              latitude,
              longitude,
              latitudeDelta: 0.015,
              longitudeDelta: 0.0121,
          },
          2000,
      );
  }

  const handleSend = () => {
      if (inputText.trim()) {
          const newUserMessage = {
              id: messages.length,
              text: inputText.trim(),
              isUser: true,
          };
          setMessages([...messages, newUserMessage]);
          decreaseTokens();
          setInputText('');
          
          setTimeout(() => {
              const systemResponse = {
                  id: messages.length + 1,
                  text: `Here's a response to: "${inputText.trim()}"`,
                  isUser: false,
                  location: currentLocation,
              };
              setMessages(prevMessages => [...prevMessages, systemResponse]);
          }, 1000);
      }
  };

  useEffect(() => {
      if (flatListRef.current) {
          flatListRef.current.scrollToEnd({ animated: true });
      }
  }, [messages]);

  const handleMapPress = (message) => {
      setSelectedLocation(message.location || currentLocation);
      setShowMap(true);
  };

  const renderMessage = ({ item }) => (
      <View style={[
          styles.messageContainer,
          item.isUser ? styles.userMessage : styles.systemMessage
      ]}>
          <Text style={[
              styles.messageText,
              item.isUser ? styles.userMessageText : styles.systemMessageText
          ]}>
              {item.text}
          </Text>
          {!item.isUser && (
              <TouchableOpacity 
                  style={styles.mapButton} 
                  onPress={() => handleMapPress(item)}
              >
                  <MaterialCommunityIcons 
                      name="map-marker" 
                      size={24} 
                      color="#708D81" 
                  />
              </TouchableOpacity>
          )}
      </View>
  );

  if (!permissionGranter) {
      return (
          <View style={styles.permissionContainer}>
              <Text style={styles.permissionText}>
                  Please allow location permission to continue...
              </Text>
          </View>
      );
  }

  return (
      <View style={styles.container}>
          <FlatList
              ref={flatListRef}
              data={messages}
              renderItem={renderMessage}
              keyExtractor={item => item.id.toString()}
              style={styles.chatContainer}
          />
          <View style={styles.inputContainer}>
              <TextInput
                  style={styles.input}
                  value={inputText}
                  onChangeText={setInputText}
                  placeholder="Ask a question..."
                  onSubmitEditing={handleSend}
              />
              <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
                  <MaterialCommunityIcons name="send" size={24} color="#fff" />
              </TouchableOpacity>
          </View>

          {showMap && (
              <View style={styles.mapContainer}>
                  <View style={styles.mapContent}>
                      <TouchableOpacity 
                          style={styles.closeButton}
                          onPress={() => setShowMap(false)}
                      >
                          <MaterialCommunityIcons name="close" size={24} color="#000" />
                      </TouchableOpacity>
                      <MapView
                          ref={mapRef}
                          provider={PROVIDER_GOOGLE}
                          style={styles.mapView}
                          region={selectedLocation || currentLocation ? {
                              latitude: (selectedLocation || currentLocation).latitude,
                              longitude: (selectedLocation || currentLocation).longitude,
                              latitudeDelta: 0.01,
                              longitudeDelta: 0.01,
                          } : {
                              latitude: 24.787926,
                              longitude: 120.997576,
                              latitudeDelta: 0.01,
                              longitudeDelta: 0.01,
                          }}
                      >
                          {(selectedLocation || currentLocation) && (
                              <Marker
                                  coordinate={{
                                      latitude: (selectedLocation || currentLocation).latitude,
                                      longitude: (selectedLocation || currentLocation).longitude,
                                  }}
                              />
                          )}
                      </MapView>
                  </View>
              </View>
          )}
          {/* token  */}
          <View style={styles.tokenContainer}>
                <MaterialCommunityIcons name="currency-usd" size={24} color="#001427" style={styles.tokenIcon} />
                <Text style={styles.tokenText}>{tokens}</Text>
            </View>
      </View>
  );
}