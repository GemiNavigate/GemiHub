import React, { useState } from 'react';
import { View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons'; 

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#fff',
  },
  messageContainer: {
    flex: 1,
    marginBottom: 10,
  },
  messageBubble: {
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
    maxWidth: '70%',
  },
  userMessage: {
    backgroundColor: '#a2cbba',
    alignSelf: 'flex-end',
  },
  botMessage: {
    backgroundColor: '#f1f0f0',
    alignSelf: 'flex-start',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderColor: '#ddd',
    paddingTop: 10,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 20,
    paddingHorizontal: 10,
    marginRight: 10,
  },
  messageText: {
    fontSize: 16,
    fontWeight: '500' 
  }
});

function AskScreen({}) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  const sendMessage = () => {
    if (inputText.trim()) {
      // 將用戶的訊息加入到訊息列表中
      const newMessages = [...messages, { text: inputText, sender: 'user' }];
      setMessages(newMessages);

      // 清空輸入框
      setInputText('');

      // 模擬對方的回覆
      setTimeout(() => {
        setMessages(prevMessages => [
          ...prevMessages,
          { text: 'This is a reply from the other person.', sender: 'bot' }
        ]);
      }, 1000); // 模擬1秒延遲
    }
  };

  return (
    <View style={styles.container}>
      {/* 滾動視圖顯示所有訊息 */}
      <ScrollView style={styles.messageContainer}>
        {messages.map((message, index) => (
          <View
            key={index}
            style={[
              styles.messageBubble,
              message.sender === 'user' ? styles.userMessage : styles.botMessage
            ]}
          >
            <Text style={styles.messageText}>{message.text}</Text> 
          </View>
        ))}
      </ScrollView>

      {/* 輸入框和發送按鈕 */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type a message"
          value={inputText}
          onChangeText={text => setInputText(text)}
        />
        <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
          <Icon name="arrow-forward-circle" size={32} color="#001427" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default AskScreen;
