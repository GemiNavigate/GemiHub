import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Dimensions, TouchableOpacity, TextInput, FlatList, Keyboard } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import GetLocation from 'react-native-get-location';

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
    input: {
        flex: 1,
        height: 40,
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
    messageContainer: {
        maxWidth: '80%',
        padding: 10,
        borderRadius: 10,
        marginVertical: 5,
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
    },
    userMessageText: {
        color: '#fff',
    },
    systemMessageText: {
        color: '#000',
    },
});

export default function AskScreen({route}) {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const flatListRef = useRef(null);
    const { currentLocation } = route.params;
    const locationString = `(${currentLocation.latitude.toFixed(5)}, ${currentLocation.longitude.toFixed(5)})`;

    const handleSend = () => {
        if (inputText.trim()) {
            const newUserMessage = {
                id: messages.length,
                text: inputText.trim(),
                isUser: true,
                time: new Date().toISOString()
            };
            setMessages([...messages, newUserMessage]);
            setInputText('');

            // Prepare data to send to the backend
            const dataToSend = {
              content: inputText.trim(),
              metadata: {
                  location:{
                    latitude: currentLocation.latitude,
                    longitude: currentLocation.longitude,
                  },
                  time: newUserMessage.time,  // Current time
              }
            };

            // replace with actual API call
            setTimeout(() => {
                const systemResponse = {
                    id: messages.length + 1,
                    text: `Here's a response to: "${inputText.trim()}" from location ${locationString}`,
                    isUser: false,
                };
                setMessages(prevMessages => [...prevMessages, systemResponse]);
            }, 1000);

            // Send data to the backend
            // fetch('YOUR_BACKEND_URL_HERE', {
            //   method: 'POST',
            //   headers: {
            //       'Content-Type': 'application/json',
            //   },
            //   body: JSON.stringify(dataToSend),  // Convert the data to JSON
            // })
            // .then(response => response.json())
            // .then(responseData => {
            //   console.log('Response from backend:', responseData);
            //   // Handle any additional response logic here if needed
            // })
            // .catch(error => {
            //   console.error('Error sending data to backend:', error);
            // });

        }
    };

    useEffect(() => {
        if (flatListRef.current) {
            flatListRef.current.scrollToEnd({ animated: true });
        }
    }, [messages]);

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
        </View>
    );

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
        </View>
    );
}