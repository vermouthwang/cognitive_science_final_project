import { createContext, useContext, useState, ReactNode } from 'react'

interface KnowledgeItem {
  type: 'image' | 'text'
  content: string
  timestamp: number
}

interface KnowledgeContextType {
  items: KnowledgeItem[]
  addItem: (item: Omit<KnowledgeItem, 'timestamp'>) => void 
}

const KnowledgeContext = createContext<KnowledgeContextType | undefined>(undefined)

export const KnowledgeProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<KnowledgeItem[]>([])

  const addItem = (item: Omit<KnowledgeItem, 'timestamp'>) => {
    setItems(prev => [...prev, { ...item, timestamp: Date.now() }])
  }

  return (
    <KnowledgeContext.Provider value={{ items, addItem }}>
      {children}
    </KnowledgeContext.Provider>
  )
}

export const useKnowledge = () => {
  const context = useContext(KnowledgeContext)
  if (context === undefined) {
    throw new Error('useKnowledge must be used within a KnowledgeProvider')
  }
  return context
} 