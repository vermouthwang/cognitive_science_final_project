import React, { useState, useEffect } from 'react';
import { useKnowledge } from '../context/KnowledgeContext';
// import './ChatBox.css';
import './DomainConsultant.css';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'consultant' | 'collaborator';
  timestamp: Date;
}

export const DomainConsultant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const { items } = useKnowledge();
  const [lastAnalyzedImageIndex, setLastAnalyzedImageIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);

  const getFormattedHistory = (messages: Message[]) => {
    return messages.map(msg => ({
      role: msg.sender === 'user' ? 'user' : 
            msg.sender === 'consultant' ? 'consultant' : 'assistant',
      content: msg.text
    }));
  };

  const fetchCritique = async (imageContent: string, previousTexts: string[]) => {
    try {
      const base64Data = imageContent.split(',')[1];
      
      // Get consultant critique first
      const consultantResponse = await fetch('http://localhost:8000/consultant/critique', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: base64Data,
          previous_texts: previousTexts
        })
      });

      if (consultantResponse.ok) {
        const consultantData = await consultantResponse.json();
        if (consultantData.critique) {
          const consultantMessage = {
            id: messages.length + 1,
            text: consultantData.critique,
            sender: 'consultant' as const,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, consultantMessage]);

          // Now get collaborator's response to the consultant's critique
          const collaboratorResponse = await fetch('http://localhost:8000/collaborator/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: "Please respond to the consultant's critique of your latest design",
              history: getFormattedHistory([...messages, consultantMessage])
            })
          });

          if (collaboratorResponse.ok) {
            const collaboratorData = await collaboratorResponse.json();
            if (collaboratorData.response) {
              setMessages(prev => [...prev, {
                id: prev.length + 1,
                text: collaboratorData.response,
                sender: 'collaborator',
                timestamp: new Date()
              }]);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error fetching responses:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      setIsLoading(true);
      
      // Get consultant's response first
      const consultantResponse = await fetch('http://localhost:8000/consultant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          previous_texts: messages.map(m => m.text)
        })
      });

      if (consultantResponse.ok) {
        const consultantData = await consultantResponse.json();
        const consultantMessage = {
          id: messages.length + 2,
          text: consultantData.response,
          sender: 'consultant' as const,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, consultantMessage]);

        // Get collaborator's response to both user and consultant
        const collaboratorResponse = await fetch('http://localhost:8000/collaborator/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: inputMessage,
            history: getFormattedHistory([...messages, userMessage, consultantMessage])
          })
        });

        if (collaboratorResponse.ok) {
          const collaboratorData = await collaboratorResponse.json();
          setMessages(prev => [...prev, {
            id: prev.length + 1,
            text: collaboratorData.response,
            sender: 'collaborator',
            timestamp: new Date()
          }]);
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  useEffect(() => {
    const analyzeNewImages = async () => {
      const imageItems = items.filter(item => item.type === 'image');
      
      if (imageItems.length > lastAnalyzedImageIndex + 1) {
        const previousTexts = messages.map(msg => msg.text);
        const latestImage = imageItems[imageItems.length - 1];
        
        await fetchCritique(latestImage.content as string, previousTexts);
        setLastAnalyzedImageIndex(imageItems.length - 1);
      }
    };

    analyzeNewImages();
  }, [items, lastAnalyzedImageIndex]);

  return (
    <div className="domain-consultant">
      <h2>Design Consultant</h2>
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}`}
          >
            <div className="message-content">
              {message.text}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSendMessage} className="message-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask the consultant about the design..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}; 