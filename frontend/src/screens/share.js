import { View, Text, StyleSheet, Dimensions, Platform, PermissionsAndroid, TouchableOpacity, TextInput } from 'react-native';
import React, { useState, useRef, useEffect } from 'react';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { GOOGLE_MAPS_API_KEY } from '../../config/constants';
import 'react-native-get-random-values';
import MapViewDirections from 'react-native-maps-directions';
import GetLocation from 'react-native-get-location';

const { width } = Dimensions.get('window');

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
        top: 80,
        width: width * 0.9,
        paddingHorizontal: 10,
        flexDirection: 'row',
        alignItems: 'center', 
    },
    input: {
        flex: 1, 
        height: 50,
        borderColor: '#e0e0e0',
        borderWidth: 1,
        backgroundColor: '#fafafa',
        borderRadius: 25,
        paddingHorizontal: 15,
        fontSize: 16,
        marginRight: 10, 
    },
    submitButton: {
        backgroundColor: '#007BFF',
        borderRadius: 25,
        paddingHorizontal: 20,
        paddingVertical: 10,
    },
    submitbuttonText: {
        color: '#fff',
        fontSize: 16,
    },
    buttonText: {
        color: '#007BFF',
        fontSize: 16,
        textAlign: 'center',
    },
    buttonContainer: {
        position: 'absolute',
        bottom: 30,
        right: 20,
        zIndex: 2,
        backgroundColor: '#fff',
        borderRadius: 50,
        padding: 10,
        elevation: 5,
    },
});

export default function ShareScreen({}) {
    const mapRef = useRef(null);
    const [origin, setOrigin] = useState();
    const [destination, setDestination] = useState();
    const [permissionGranter, setPermissionGranter] = useState();
    const [query, setQuery] = useState(''); 
    
    const handleSubmit = () => {
        if (query.trim()) {
            // sending the query to a backend service
            console.log("Submitted query:", query);
            // reset the input field
            setQuery('');
        }
    };

    useEffect(() => {
        _getLocationPermission();
    }, []);

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
            console.log('My current location:', location);

            const currentCoordinate = {
                latitude: location.latitude,
                longitude: location.longitude,
            };
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
                region={{
                    latitude: 24.787926,
                    longitude: 120.997576,
                    latitudeDelta: 0.01,
                    longitudeDelta: 0.01,
                }}>
                {origin !== undefined ? <Marker coordinate={origin}></Marker> : null}
                {destination !== undefined ? <Marker coordinate={destination}></Marker> : null}
                {origin !== undefined && destination !== undefined ? (
                    <MapViewDirections
                        origin={origin}
                        destination={destination}
                        apikey={GOOGLE_MAPS_API_KEY}
                        strokeColor='blue'
                        strokeWidth={4}
                    />
                ) : null}
            </MapView>

            {/* Input Box for Search Query */}
            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    placeholder="Enter your query"
                    placeholderTextColor="#b0b0b0"
                    value={query}
                    onChangeText={setQuery} // Update state with input
                />
                {/* Submit Button */}
                <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
                    <Text style={styles.submitbuttonText}>Submit</Text>
                </TouchableOpacity>
            </View>

            {/* Get Location Button */}
            <TouchableOpacity 
                style={styles.buttonContainer} 
                onPress={_getCurrentLocation}>
                <Text style={styles.buttonText}>My Location</Text>
            </TouchableOpacity>
        </View>
    );
}
