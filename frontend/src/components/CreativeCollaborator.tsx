import './CreativeCollaborator.css'
import { useState, useEffect } from 'react'
import { useKnowledge } from '../context/KnowledgeContext'
import { processBase64Image } from '../utils/imageUtils'

export const CreativeCollaborator = () => {
  const [userImage, setUserImage] = useState<string | null>(null)
  const [aiImage, setAiImage] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([])
  const { addItem } = useKnowledge()

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setIsUploading(true)
      const reader = new FileReader()
      reader.onloadend = async () => {
        const imageData = reader.result as string
        setUserImage(imageData)
        addItem({ type: 'image', content: imageData })

        try {
          const concludeResponse = await fetch('/collaborator/conclude-round', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({
              user_image: null,
              ai_image: aiImage,
              chat_history: chatHistory
            }),
          });

          if (!concludeResponse.ok) {
            const errorText = await concludeResponse.text();
            console.error('Conclude round error:', errorText);
            throw new Error(`Conclude round failed: ${concludeResponse.status}`);
          }

          const concludeData = await concludeResponse.json();
          const generatedPrompt = concludeData.generated_prompt;
          console.log('Generated prompt:', generatedPrompt);

          let logoResponse;
          if (!aiImage) {
            // Initial round - use generate-logo
            logoResponse = await fetch('/logo-generator/generate-logo', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify({
                prompt: generatedPrompt
              }),
            });
          } else {
            // Subsequent round - use modify-logo
            logoResponse = await fetch('/logo-generator/modify-logo', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify({
                modification_prompt: generatedPrompt,
                reference_image: aiImage
              }),
            });
          }

          if (!logoResponse.ok) {
            const errorText = await logoResponse.text();
            console.error('Logo generation error:', errorText);
            throw new Error(`Logo generation failed: ${logoResponse.status}`);
          }

          const logoData = await logoResponse.json();
          if (logoData.image) {
            setAiImage(logoData.image);
            // Add AI generated image to knowledge base
            addItem({ 
              type: 'image', 
              content: `data:image/png;base64,${logoData.image}`
            });
          }

        } catch (error) {
          console.error('Error:', error);
        } finally {
          setIsUploading(false);
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSendMessage = async () => {
    if (message.trim()) {
      setIsLoading(true)
      // Add user message to chat history
      const userMessage = { role: 'user', content: message }
      const updatedHistory = [...chatHistory, userMessage]
      setChatHistory(updatedHistory)
      addItem({ type: 'text', content: message })

      try {
        const response = await fetch('/collaborator/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            history: chatHistory,
          }),
        })

        if (!response.ok) {
          throw new Error('Failed to get response')
        }

        const data = await response.json()
        
        // Add AI response to chat history
        const aiMessage = { role: 'assistant', content: data.response }
        setChatHistory([...updatedHistory, aiMessage])
        
        // Add AI response to knowledge base
        addItem({ type: 'text', content: `AI: ${data.response}` })
      } catch (error) {
        console.error('Error sending message:', error)
      } finally {
        setIsLoading(false)
      }

      setMessage('')
    }
  }

  return (
    <div className="creative-collaborator">
      <div className="image-display">
        <div className="image-container">
          {isUploading ? (
            <div className="uploading">Uploading...</div>
          ) : userImage ? (
            <img src={userImage} alt="User Creation" />
          ) : (
            <div className="placeholder">User Creation</div>
          )}
        </div>
        <div className="image-container">
          {aiImage ? (
            <img 
              src={`data:image/png;base64,${aiImage}`}
              alt="AI Creation"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
          ) : (
            <div className="placeholder">Collaborator Creation</div>
          )}
        </div>
      </div>

      <label className="upload-button">
        {isUploading ? 'Uploading...' : 'Upload and Next Round'}
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          disabled={isUploading}
          style={{ display: 'none' }}
        />
      </label>

      <div className="chat-section">
        <div className="chat-messages">
          {chatHistory.map((chat, index) => (
            <div 
              key={index}
              className={`chat-message ${chat.role === 'user' ? 'user' : 'ai'}`}
            >
              {chat.content}
            </div>
          ))}
        </div>
        <div className="message-input">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button onClick={handleSendMessage} disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}
