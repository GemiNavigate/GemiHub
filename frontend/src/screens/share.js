import { View, Text, StyleSheet, Dimensions, Platform, PermissionsAndroid, TouchableOpacity, TextInput, Image, Animated, PanResponder } from 'react-native';
import React, { useState, useRef, useEffect, useContext } from 'react';
import MapView, { Marker, PROVIDER_GOOGLE, Callout } from 'react-native-maps';
import { launchImageLibrary, launchCamera } from 'react-native-image-picker';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import GetLocation from 'react-native-get-location';
import { TokenContext, LocationContext } from './Context';

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
    container: {
        ...StyleSheet.absoluteFillObject,
        flex: 1,
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    map: {
        ...StyleSheet.absoluteFillObject,
        zIndex: 0,
    },
    inputContainer: {
        position: 'absolute',
        width: width * 0.9,
        paddingHorizontal: 10,
        backgroundColor: '#fafafa',
        borderTopLeftRadius: 25,
        borderTopRightRadius: 25,
        padding: 15,
        alignItems: 'center',
        elevation: 5,
    },
    input: {
        width: '100%',
        height: 100,
        borderColor: '#e0e0e0',
        borderWidth: 1,
        backgroundColor: '#fafafa',
        borderRadius: 25,
        paddingHorizontal: 15,
        fontSize: 16,
        marginBottom: 10,
        textAlignVertical: 'top', // Make it multiline
    },
    imagePreview: {
        width: '100%',
        height: 150,
        borderRadius: 10,
        marginBottom: 10,
    },
    buttonRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '100%',
    },
    submitButton: {
        backgroundColor: '#708D81',
        borderRadius: 25,
        paddingHorizontal: 20,
        paddingVertical: 10,
        flexDirection: 'row',
        alignItems: 'center',
    },
    submitbuttonText: {
        color: '#fff',
        fontSize: 16,
    },
    buttonContainer: {
        position: 'absolute',
        top: 30,
        right: 20,
        zIndex: 2,
        backgroundColor: '#fff',
        borderRadius: 50,
        padding: 10,
        elevation: 5,
    },
    imageButton: {
        backgroundColor: '#708D81',
        borderRadius: 25,
        padding: 10,
        marginRight: 10, 
    },
    calloutContainer: {
        backgroundColor: '#fff', 
        borderRadius: 10,
        padding: 10,
        borderColor: '#001427', 
        borderWidth: 1,
        width: 150,
    },
    calloutText: {
        color: '#001427', 
        fontSize: 14,
        fontWeight: '500', 
    },
    image: {
        width: 100, 
        height: 100,
        position: 'relative', 
        top: -20, 
        zIndex: 5, 
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

export default function ShareScreen({}) {
    const mapRef = useRef(null);
    const [permissionGranter, setPermissionGranter] = useState();
    const [cameraPermission, setCameraPermission] = useState(false);
    const { currentLocation, setCurrentLocation } = useContext(LocationContext);

    const [postText, setPostText] = useState(''); 
    const [selectedImage, setSelectedImage] = useState(null);
    const [userPosts, setUserPosts] = useState({}); // To store the user posts
    const slideAnim = useRef(new Animated.Value(0)).current;
    const { tokens, setTokens } = useContext(TokenContext);
    /* animation */
    const [fixedPosition, setFixedPosition] = useState(false);
    const [position, setPosition] = useState(0);

    useEffect(() => {
        const checkPermissions = async () => {
            const locationGranted = await requestPermission(
                PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
                'Location Permission',
                'Please allow permission to continue...'
            );
            const cameraGranted = await requestPermission(
                PermissionsAndroid.PERMISSIONS.CAMERA,
                'Camera Permission',
                'Please allow camera access to take photos.'
            );

            setPermissionGranter(locationGranted);
            setCameraPermission(cameraGranted);
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
            moveToLocation(currentCoordinate.latitude, currentCoordinate.longitude);
        } catch (error) {
            console.warn('Error getting current location:', error.message);
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
    
     /* animation */
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

    // add coins
    const increaseTokens = () => {
        setTokens(tokens + 10); 
    };

    const handleSubmit = () => {
        if (postText.trim() || selectedImage) {
            // get time
            const timestamp = new Date().toISOString();

            // Save the post (text + image) and location
            const newPost = {
                location: currentLocation,
                text: postText,
                image: selectedImage,
                timestamp: timestamp,
            };
            // TODO: 後端獲取資料: JSON.stringify(newPost)
            const dataToSend = {
                content: postText.trim(),
                image: selectedImage,
                metadata: {
                    location:{
                      latitude: currentLocation.latitude,
                      longitude: currentLocation.longitude,
                    },
                    time: timestamp,  // Current time
                }
              };

            setUserPosts(newPost);
            increaseTokens();

            // Reset fields
            setPostText('');
            setSelectedImage(null);
        }
    };

    const selectImage = () => {
        launchCamera(
            {
                mediaType: 'photo',
                cameraType: 'back', 
                saveToPhotos: true, 
            },
            response => {
                if (!response.didCancel && !response.errorCode) {
                    const uri = response.assets[0]?.uri;
                    setSelectedImage(uri);
                }
            }
        );
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
                }}>
                {/* Display all user posts as markers */}
                {userPosts.location && (
                    <Marker 
                        style={styles.markerContainer}
                        coordinate={userPosts.location}
                        // title="User name"
                        // description={post.text}
                    >
                        {userPosts.image && (
                            <Image
                                source={{ uri: userPosts.image }}
                                style={styles.image}
                            />
                        )}

                        <Callout tooltip>
                            <View style={styles.calloutContainer}>
                                <Text style={styles.calloutText}>{userPosts.text}</Text>
                                <Text style={{color: '#8c8c8c', fontSize: 12}}>{new Date(userPosts.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
                            </View>
                        </Callout>
                    </Marker>
                )}

                {currentLocation && (
                    <Marker
                        coordinate={currentLocation}
                        // title="My Location"
                        // description="You are here"
                    />
                )}
            </MapView>
            
            {/* Input Box for Posting */}
            <Animated.View
            style={[styles.inputContainer, { transform: [{ translateY: slideAnim }] }]}
            {...panResponder.panHandlers} // Add the PanResponder handlers
            >
                <TextInput
                    style={styles.input}
                    placeholder="Wanna share something?"
                    placeholderTextColor="#b0b0b0"
                    value={postText}
                    onChangeText={setPostText}
                    multiline
                />
                {selectedImage && (
                    <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
                )}
                <View style={styles.buttonRow}>
                    <TouchableOpacity style={styles.imageButton} onPress={selectImage}>
                        <MaterialCommunityIcons name="camera" size={24} color="#fff" />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
                        <Text style={styles.submitbuttonText}>Post</Text>
                    </TouchableOpacity>
                </View>
            </Animated.View>

            {/* Move to Current Location Button */}
            <TouchableOpacity
                style={styles.buttonContainer}
                onPress={() => {
                    if (currentLocation) {
                        moveToLocation(currentLocation.latitude, currentLocation.longitude);
                    }
                }}>
                <MaterialCommunityIcons name="map-marker" size={24} color="#001427" />
            </TouchableOpacity>
        </View>
    );
}
