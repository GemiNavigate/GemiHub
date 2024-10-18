import { View, Text, StyleSheet, Dimensions, Platform, PermissionsAndroid, TouchableOpacity, TextInput, Image, Animated, PanResponder } from 'react-native';
import React, { useState, useRef, useEffect, useContext } from 'react';
import MapView, { Marker, PROVIDER_GOOGLE, Callout } from 'react-native-maps';
import { launchImageLibrary } from 'react-native-image-picker';
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
        bottom: 0,
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
        width: 40,
        height: 40,
        borderRadius: 10,
        marginBottom: 5,
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
    const [postText, setPostText] = useState(''); 
    const { currentLocation, setCurrentLocation } = useContext(LocationContext);
    const [selectedImage, setSelectedImage] = useState(null);
    const [userPosts, setUserPosts] = useState([]); // To store the user posts
    const slideAnim = useRef(new Animated.Value(0)).current;
    const [isInputExpanded, setIsInputExpanded] = useState(false);
    const { tokens, setTokens } = useContext(TokenContext);
    
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

            setUserPosts([...userPosts, newPost]);
            increaseTokens();

            // Reset fields
            setPostText('');
            setSelectedImage(null);
        }
    };

    const selectImage = () => {
        launchImageLibrary({ mediaType: 'photo' }, response => {
            if (!response.didCancel && !response.errorCode) {
                const uri = response.assets[0]?.uri;
                setSelectedImage(uri);
            }
        });
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
        }
    }

    async function moveToLocation(latitude, longitude) {
        mapRef.current.animateToRegion(
            {
                latitude,
                longitude,
                latitudeDelta: 0.015,
                longitudeDelta: 0.0121,
            },
            2000,
        );
    }

    const handleFocus = () => {
        // 當聚焦時，上移動畫
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }).start(() => {
            setIsInputExpanded(isInputExpanded); // Update the expansion state
        });
    };
    
    const handleBlur = () => {
        // 當失焦時，返回原位
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }).start();
    };
    
    /* animation */
    const toggleInputContainer = () => {
        Animated.timing(slideAnim, {
            toValue: slideAnim._value === 0 ? 110 : 0, // Adjust this value based on your design
            duration: 200,
            useNativeDriver: true,
        }).start(() => {
            setIsInputExpanded(!isInputExpanded); // Update the expansion state
        });
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
                {userPosts.map((post, index) => (
                    <Marker 
                        style={styles.markerContainer}
                        key={index}
                        coordinate={post.location}
                        // title="User name"
                        // description={post.text}
                    >
                        {post.image && (
                            <Image
                                source={{ uri: post.image }}
                                style={styles.image}
                            />
                        )}

                        <Callout tooltip>
                            <View style={styles.calloutContainer}>
                                <Text style={styles.calloutText}>{post.text}</Text>
                                <Text style={{color: '#8c8c8c', fontSize: 12}}>{new Date(post.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
                            </View>
                        </Callout>

                    </Marker>
                ))}

                {currentLocation && (
                    <Marker
                        coordinate={currentLocation}
                        // title="My Location"
                        // description="You are here"
                    />
                )}
            </MapView>
            
            {/* Input Box for Posting */}
            {/* <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    placeholder="Wanna share something?"
                    placeholderTextColor="#b0b0b0"
                    value={postText}
                    onChangeText={setPostText}
                    multiline
                />

                Image Preview 
                {selectedImage && (
                    <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
                )}

                Button Row for Image Picker and Submit
                <View style={styles.buttonRow}>
                    Image Picker Button
                    <TouchableOpacity style={styles.imageButton} onPress={selectImage}>
                        <MaterialCommunityIcons name="image" size={24} color="#fff" />
                    </TouchableOpacity>

                    Submit Button
                    <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
                        <Text style={styles.submitbuttonText}>Submit</Text>
                    </TouchableOpacity>
                </View>
            </View> */}

            <Animated.View style={[styles.inputContainer, { transform: [{ translateY: slideAnim }] }]}>
                <TouchableOpacity onPress={toggleInputContainer} style={styles.arrow}>
                    <MaterialCommunityIcons name={isInputExpanded ? "arrow-up" : "arrow-down"} size={24} color="#708D81"/>
                </TouchableOpacity>
                <TextInput
                    style={styles.input}
                    placeholder="Wanna share something?"
                    placeholderTextColor="#b0b0b0"
                    value={postText}
                    onChangeText={setPostText}
                    multiline
                    onFocus={handleFocus} // 當輸入框獲得焦點時
                    // onBlur={handleBlur}   // 當輸入框失去焦點時
                />
                {selectedImage && (
                    <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
                )}
                <View style={styles.buttonRow}>
                    <TouchableOpacity style={styles.imageButton} onPress={selectImage}>
                        <MaterialCommunityIcons name="image" size={24} color="#fff" />
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

            <View style={styles.tokenContainer}>
                <MaterialCommunityIcons name="currency-usd" size={24} color="#001427" style={styles.tokenIcon} />
                <Text style={styles.tokenText}>{tokens}</Text>
            </View>

        </View>
    );
}
