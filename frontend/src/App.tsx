import './App.css'
import { CreativeCollaborator } from './components/CreativeCollaborator'
import { DomainConsultant } from './components/DomainConsultant'
import { MysteryEvaluator, MysteryEvaluatorRef } from './components/MysteryEvaluator'
import { KnowledgeBase } from './components/KnowledgeBase'
import { KnowledgeProvider } from './context/KnowledgeContext'
import { useRef } from 'react'

export const App = () => {
  const evaluatorRef = useRef<MysteryEvaluatorRef>(null)

  const handleImageSelect = (imageData: string) => {
    console.log('Image data format:', {
      starts_with: imageData.substring(0, 50),
      length: imageData.length,
      contains_data_url: imageData.includes('data:image')
    })
    evaluatorRef.current?.evaluateImage(imageData)
  }

  return (
    <KnowledgeProvider>
      <div className="app-container">
        <div className="grid-container">
          <div className="grid-item collaborator">
            <CreativeCollaborator />
          </div>
          <div className="grid-item consultant">
            <DomainConsultant />
          </div>
          <div className="grid-item evaluator">
            <MysteryEvaluator ref={evaluatorRef} />
          </div>
          <div className="grid-item knowledge">
            <KnowledgeBase onImageSelect={handleImageSelect} />
          </div>
        </div>
      </div>
    </KnowledgeProvider>
  )
}

export default App
