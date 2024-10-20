import React, { useState, useRef, useEffect, useContext } from 'react';
import { Image, View, Text, StyleSheet, Dimensions, ScrollView, TouchableOpacity, TextInput, FlatList, Platform, PermissionsAndroid, Animated, PanResponder } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import MapView, { Marker, PROVIDER_GOOGLE, Callout } from 'react-native-maps';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete'
import 'react-native-get-random-values';
import { GOOGLE_MAPS_API_KEY } from '../config/constants';
import GetLocation from 'react-native-get-location';
import { TokenContext, LocationContext } from './Context';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width, height } = Dimensions.get('window');
const mapstyle = [
    {
        "featureType": "administrative",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "poi",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "water",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "transit",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "landscape",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road.local",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "water",
        "stylers": [
            {
                "color": "#abbaa4"
            }
        ]
    },
    {
        "featureType": "transit.line",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#3f518c"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "stylers": [
            {
                "color": "#ad9b8d"
            }
        ]
    }
]

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
    ansContainer: {
        position: 'absolute',
        width: width * 0.9,
        paddingHorizontal: 10,
        backgroundColor: '#fafafa',
        borderTopLeftRadius: 25,
        borderTopRightRadius: 25,
        padding: 15,
        alignItems: 'flex-start',
        elevation: 5,
    },
    ansText: {
        width: '100%',
        // height: 100,
        // borderColor: '#e0e0e0',
        // borderWidth: 1,
        backgroundColor: '#fafafa', //#faefd7
        // borderRadius: 25,
        paddingHorizontal: 15,
        fontSize: 16,
        marginBottom: 10,
        textAlignVertical: 'top', // Make it multiline
        color: 'black'
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
    responseContainer: {
        position: 'absolute',
        bottom: 80,
        left: 10,
        right: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        padding: 10,
        borderRadius: 5,
        maxHeight: 200,
        width: width*0.9
    },
    responseItem: {
        marginBottom: 10,
    },
    responseText: {
        fontSize: 16,
    },
    logo: {
        height: 40,
        width: 40,
        left: 0,
    },
    calloutContainer: {
        backgroundColor: 'transparent',
        alignItems: 'center',
    },
    calloutBubble: {
        backgroundColor: 'rgba(255, 255, 255, 0.9)', // 調整背景透明度
        borderRadius: 10,
        padding: 10,
        width: 200,
        borderWidth: 1,  // 添加邊框
        borderColor: 'rgba(112, 141, 129, 0.5)', 
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.15,  // 調整陰影透明度
        shadowRadius: 3,
        elevation: 5,
    },
    calloutTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
        marginBottom: 4,
        lineHeight: 18,
    },
    calloutTime: {
        fontSize: 12,
        color: '#666',
        marginTop: 1,
        borderTopWidth: 1,
        borderTopColor: 'rgba(0,0,0,0.1)',  // 添加分隔線
        paddingTop: 4,
    },
    calloutArrow: {
        width: 12,
        height: 12,
        backgroundColor: '#708D81', 
        borderRightWidth: 1,  // 箭頭邊框
        borderBottomWidth: 1,
        borderColor: '#ddd',
        transform: [{ rotate: '45deg' }],
        marginTop: -6,
        alignSelf: 'center',
    }
    
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
  const slideAnim = useRef(new Animated.Value(0)).current;
  const [answer, setAnswer] = useState(null);
  const [references, setReferences] = useState([]);
  /* animation */
  const [fixedPosition, setFixedPosition] = useState(false);
  const [position, setPosition] = useState(0);
  const googlePlacesRef = useRef(null);

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
  const decreaseTokens = () => {
      setTokens(tokens - 10); 
  };

  // animation
  const panResponder = useRef(
    PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (event, gestureState) => {
            // 更新 slideAnim 值
            slideAnim.setValue(gestureState.dy);
        },
        onPanResponderRelease: (event, gestureState) => {
            if (gestureState.dy < -30) { // 向上滑动
                slideAnim.setValue(0);
            } else if (gestureState.dy > 30) { // 向下滑动
                slideAnim.setValue(100);
            } else {
                // 否则返回原始位置
                Animated.timing(slideAnim, {
                    toValue: fixedPosition ? position : 0,
                    duration: 200,
                    useNativeDriver: true,
                }).start();
            }
        },
    })
  ).current;

  const formatDateTime = (dateTime) => {
    const date = new Date(dateTime);
    const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从0开始，所以加1
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
  };

    const handleSubmit = async () => {
        try {
            setIsLoading(true);
            if(!selectedLocation){
                const currentRegion = {
                    latitude: currentLocation.latitude,
                    longitude: currentLocation.longitude,
                    latitudeDelta: 0.01,
                    longitudeDelta: 0.01,
                };
                setSelectedLocation(currentRegion);
            }
            if (selectedLocation || question) {
                console.log('Selected Location:', selectedLocation);
                console.log('Content:', question);

                const currentTime = new Date().toISOString();
                
                const dataToSend = {
                    content: question.trim(),
                    cur_lat: currentLocation.latitude,
                    cur_lng: currentLocation.longitude,
                    filter: {
                        min_lat: mapRegion.latitude - mapRegion.latitudeDelta / 2,
                        max_lat: mapRegion.latitude + mapRegion.latitudeDelta / 2,
                        min_lng: mapRegion.longitude - mapRegion.longitudeDelta / 2,
                        max_lng: mapRegion.longitude + mapRegion.longitudeDelta / 2,
                        cur_time: currentTime,
                        time_range: 60
                    },
                };
                console.log(JSON.stringify(dataToSend));
                const response = await fetch("https://mchackathon.benson0402.com/api/ask", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(dataToSend),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const responseData = await response.json();
                setAnswer(responseData.response);
                setReferences(responseData.references);
                decreaseTokens();
                setIsLoading(false);
                setQuestion('');
            } else {
                alert('請選擇一個位置並輸入問題');
                setIsLoading(false);
            }
        } catch (error) {
            console.error('提交時發生錯誤:', error);
            alert('提交時發生錯誤');
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
              customMapStyle={mapstyle}
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
              {/* current location marker  */}
              {currentLocation && (
                  <Marker
                      coordinate={currentLocation}
                      title="My Location"
                      description="You are here"
                  />
              )}
              {/* multiple reference marker  */}
            {references.map((ref, index) => (
                <Marker
                    key={index}
                    coordinate={{
                        latitude: ref.lat,
                        longitude: ref.lng,
                    }}
                    pinColor="#F4D58D"
                >
                    <Callout tooltip>
                        <View style={styles.calloutContainer}>
                            <View style={styles.calloutBubble}>
                                <Text style={styles.calloutTitle}>
                                    {ref.info}
                                </Text>
                                <Text style={styles.calloutTime}>
                                    {formatDateTime(ref.time)}
                                </Text>
                            </View>
                            <View style={styles.calloutArrow} />
                        </View>
                    </Callout>
                </Marker>
            ))}
          </MapView>
          
          {/* Input Box for Posting */}
          <View style={styles.searchContainer}>
            <View style={styles.searchInputContainer}>
                <GooglePlacesAutocomplete 
                    ref={googlePlacesRef}
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
                        if (googlePlacesRef.current) {
                            googlePlacesRef.current.setAddressText("");
                        }
                    }}
                    // Clear the search input
                    
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

          {answer && (
                // <View style={styles.ansContainer}>
                //     {/* <View style={styles.responseItem}> */}
                //         <Image source={require('../assets/gemini.png')} style={styles.logo} />
                //         <Text style={styles.ansText}>這是測試測測試測試測測試測試</Text>
                //     {/* </View> */}
                // </View>
                <Animated.View
                style={[styles.ansContainer, { transform: [{ translateY: slideAnim }] }]}
                {...panResponder.panHandlers} // Add the PanResponder handlers
                >
                    <Image source={require('../assets/gemini.png')} style={styles.logo} />
                    {/* <Text style={styles.ansText}>{answer}</Text> */}
                    <Text style={styles.ansText}>{answer}</Text>
                </Animated.View>
           )}


      </View>
  );
}