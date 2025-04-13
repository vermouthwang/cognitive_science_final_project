import { useKnowledge } from '../context/KnowledgeContext'
import './KnowledgeBase.css'

export const KnowledgeBase = ({ onImageSelect }: { onImageSelect?: (imageData: string) => void }) => {
  const { items } = useKnowledge()

  return (
    <div className="knowledge-base">
      <h2>Knowledge Base</h2>
      <div className="knowledge-items">
        {items.map((item, index) => (
          <div key={index} className="knowledge-item">
            {item.type === 'image' ? (
              <img 
                src={item.content} 
                alt="Knowledge item" 
                className="knowledge-image"
                onClick={() => onImageSelect && onImageSelect(item.content)}
                style={{ cursor: onImageSelect ? 'pointer' : 'default' }}
              />
            ) : (
              <div className="knowledge-text">{item.content}</div>
            )}
            <div className="knowledge-timestamp">
              {new Date(item.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 