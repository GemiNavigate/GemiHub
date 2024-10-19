import React, { useState, useRef, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, Dimensions, TouchableOpacity, TextInput, FlatList, Platform, PermissionsAndroid, Animated, PanResponder } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import MapView, { Marker, PROVIDER_GOOGLE, Callout } from 'react-native-maps';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';
import 'react-native-get-random-values';
import { GOOGLE_MAPS_API_KEY } from '../config/constants';
import GetLocation from 'react-native-get-location';
import { TokenContext, LocationContext } from './Context';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    map: {
      ...StyleSheet.absoluteFillObject,
      zIndex: 0,
    },
    coordinatesContainer: {
        position: 'absolute',
        bottom: 20,
        left: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: 10,
        borderRadius: 5,
        zIndex: 1,
    },
    coordinatesText: {
        fontSize: 12,
        color: '#333',
    },
    buttonContainer: {
      position: 'absolute',
      top: 580,
      right: 20,
      zIndex: 2,
      backgroundColor: '#fff',
      borderRadius: 50,
      padding: 10,
      elevation: 5,
    },
    searchInputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        // marginBottom: 10,
    },
    searchButton: {
        backgroundColor: '#708D81',
        borderRadius: 25,
        paddingHorizontal: 15,
        paddingVertical: 10,
        position: 'absolute',
        right: 0,
        top: 0
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 10,
        top: 50,
        position: 'absolute'
    },
    input: {
        flex: 1,
        height: 40,
        borderColor: 'gray',
        borderWidth: 1,
        borderRadius: 20,
        paddingHorizontal: 15,
        backgroundColor: 'white',
        marginRight: 10,
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
    searchContainer: {
        position: 'absolute',
        top: 20,
        left: 10,
        right: 10,
        zIndex: 1,
        backgroundColor: 'transparent',
    },
    submitButton: {
        backgroundColor: '#708D81',
        borderRadius: 25,
        paddingHorizontal: 20,
        paddingVertical: 10,
        flexDirection: 'row',
        alignItems: 'center',
    },
    buttonText: {
        color: 'white',
        fontWeight: 'bold',
        marginLeft: 5,
    },
});


export default function AskerScreen() {
  const mapRef = useRef(null);
  const [permissionGranter, setPermissionGranter] = useState();
  const { currentLocation, setCurrentLocation } = useContext(LocationContext);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { tokens, setTokens } = useContext(TokenContext);
  const [mapRegion, setMapRegion] = useState(null);
  const [cornerCoordinates, setCornerCoordinates] = useState(null);


  useEffect(() => {
      const checkPermissions = async () => {
          const locationGranted = await requestPermission(
              PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
              'Location Permission',
              'Please allow permission to continue...'
          );
          setPermissionGranter(locationGranted);
      };
      checkPermissions();
  }, []);

  useEffect(() => {
      if (permissionGranter) {
          _getCurrentLocation();
      }
  }, [permissionGranter]);

  const requestPermission = async (permission, title, message) => {
      if (Platform.OS === 'android') {
          try {
              const granted = await PermissionsAndroid.request(permission, {
                  title,
                  message,
                  buttonNeutral: 'Ask Me Later',
                  buttonNegative: 'Cancel',
                  buttonPositive: 'OK',
              });
              return granted === PermissionsAndroid.RESULTS.GRANTED;
          } catch (err) {
              console.warn(err);
              return false;
          }
      } else {
          return true; // iOS permissions are handled differently
      }
  };

  const _getCurrentLocation = async () => {
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
          setMapRegion(currentCoordinate);
          moveToLocation(currentCoordinate.latitude, currentCoordinate.longitude);
      } catch (error) {
        //   console.warn('Error getting current location:', error.message);
      }
  };

  // Function to move map to the current location
  const moveToLocation = (latitude, longitude) => {
      if (mapRef.current) {
          mapRef.current.animateToRegion(
              {
                  latitude,
                  longitude,
                  latitudeDelta: 0.015,
                  longitudeDelta: 0.0121,
              },
              2000
          );
      }
  };
  
  // add coins
  const increaseTokens = () => {
      setTokens(tokens + 10); 
  };

  const handleSubmit = async () => {
    try {
        setIsLoading(true);
        if (selectedLocation && question) {
            console.log('Selected Location:', selectedLocation);
            console.log('Question:', question);
        } else {
            alert('Please select a location and enter a question');
        }
    } catch (error) {
        console.error('Error submitting:', error);
        alert('An error occurred while submitting');
    } finally {
        setIsLoading(false);
    }
  };

  const onRegionChangeComplete = (region) => {
    setMapRegion(region);
    if (mapRef.current) {
        mapRef.current.getMapBoundaries().then((bounds) => {
            setCornerCoordinates({
                northEast: bounds.northEast,
                southWest: bounds.southWest,
            });
        });
    }
  };

  if (!permissionGranter) return (
      <View>
          <Text>Please allow permission to continue...</Text>
      </View>
  );

  return (
      <View style={styles.container}>
          <MapView
              ref={mapRef}
              provider={PROVIDER_GOOGLE}
              style={styles.map}
              region={currentLocation ? {
                  latitude: currentLocation.latitude,
                  longitude: currentLocation.longitude,
                  latitudeDelta: 0.01,
                  longitudeDelta: 0.01,
              } : {
                  // Fallback value if location is not available yet
                  latitude: 25.01349,  
                  longitude: 121.540646,
                  latitudeDelta: 0.01,
                  longitudeDelta: 0.01,
              }}
              onRegionChangeComplete={onRegionChangeComplete}
            >
              
              {currentLocation && (
                  <Marker
                      coordinate={currentLocation}
                      title="My Location"
                      description="You are here"
                  />
              )}
          </MapView>
          
          {/* Input Box for Posting */}
          <View style={styles.searchContainer}>
            <View style={styles.searchInputContainer}>
                <GooglePlacesAutocomplete 
                    placeholder="Search location"
                    placeholderTextColor="#b0b0b0"
                    fetchDetails={true}
                    onPress={(data, details = null) => {
                        // 使用者選擇地點後，處理資料
                        const searchRegion = {
                            latitude: details?.geometry?.location.lat,
                            longitude: details?.geometry?.location.lng,
                            latitudeDelta: 0.01,
                            longitudeDelta: 0.01,
                        };
                        // console.log(data, details);
                        console.log(searchRegion.latitude, searchRegion.longitude);
                        moveToLocation(searchRegion.latitude, searchRegion.longitude);
                        setMapRegion(searchRegion);
                        setSelectedLocation(searchRegion);
                    }}
                    query={{
                        key: GOOGLE_MAPS_API_KEY, 
                        language: 'zh-TW',            
                    }}
                    styles={{
                        textInputContainer: {
                            flexDirection: 'row',
                            alignItems: 'center',
                            backgroundColor: 'transparent', // Adjust the background
                            marginHorizontal: 10,           // Horizontal margin
                            zIndex: 50,
                            width: 320,
                            left: -10
                        },
                        textInput: {
                            flex: 1,
                            height: 40,
                            borderColor: 'gray',
                            borderWidth: 1,
                            borderRadius: 20,
                            paddingHorizontal: 15,
                            backgroundColor: 'white',
                            marginRight: 10,
                            zIndex: 50
                        },
                        listView: {
                            backgroundColor: '#fff',        // Background color of the suggestions list
                            borderWidth: 1,
                            borderColor: '#ccc',            // Border color of the dropdown
                            borderRadius: 10,               // Radius for dropdown items
                            marginHorizontal: 10,
                            zIndex: 50
                        },
                        
                    }}
                />
                <TouchableOpacity 
                    style={styles.searchButton} 
                    onPress={() => {
                        if (currentLocation) {
                            moveToLocation(currentLocation.latitude, currentLocation.longitude);
                        }
                    }}
                    disabled={isLoading}
                >
                    <MaterialCommunityIcons name="map-marker" size={20} color="white" />
                </TouchableOpacity>
            </View>

            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    placeholder="Enter your question"
                    value={question}
                    onChangeText={setQuestion}
                />
                <TouchableOpacity 
                    style={styles.submitButton} 
                    onPress={handleSubmit}
                    disabled={isLoading}
                >
                    <Icon name="send" size={20} color="white" />
                    <Text style={styles.buttonText}>
                        {isLoading ? 'Sending...' : 'Submit'}
                    </Text>
                </TouchableOpacity>
            </View>
          </View>

          {cornerCoordinates && (
                <View style={styles.coordinatesContainer}>
                    <Text style={styles.coordinatesText}>
                        NE: {cornerCoordinates.northEast.latitude.toFixed(6)}, {cornerCoordinates.northEast.longitude.toFixed(6)}
                    </Text>
                    <Text style={styles.coordinatesText}>
                        SW: {cornerCoordinates.southWest.latitude.toFixed(6)}, {cornerCoordinates.southWest.longitude.toFixed(6)}
                    </Text>
                    <Text style={styles.coordinatesText}>
                        NW: {cornerCoordinates.southWest.latitude.toFixed(6)}, {cornerCoordinates.northEast.longitude.toFixed(6)}
                    </Text>
                    <Text style={styles.coordinatesText}>
                        SE: {cornerCoordinates.northEast.latitude.toFixed(6)}, {cornerCoordinates.southWest.longitude.toFixed(6)}
                    </Text>
                </View>
            )}
          {/* Move to Current Location Button */}
          {/* <TouchableOpacity
              style={styles.buttonContainer}
              onPress={() => {
                  if (currentLocation) {
                      moveToLocation(currentLocation.latitude, currentLocation.longitude);
                  }
              }}>
              <MaterialCommunityIcons name="map-marker" size={24} color="#001427" />
          </TouchableOpacity> */}
      </View>
  );
}