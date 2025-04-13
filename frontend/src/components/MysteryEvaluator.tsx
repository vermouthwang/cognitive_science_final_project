import { useState, forwardRef, useImperativeHandle } from 'react'
import './MysteryEvaluator.css'
import { processBase64Image } from '../utils/imageUtils'

type EvaluationEntity = {
  score: number
  feedback: string
  hidden_markers: {
    missing_elements: string[]
    color_violations: string[]
    similarity_score: number
  }
}

export interface MysteryEvaluatorRef {
  evaluateImage: (imageData: string) => Promise<void>
}

export const MysteryEvaluator = forwardRef<MysteryEvaluatorRef>((props, ref) => {
  const [evaluations, setEvaluations] = useState<EvaluationEntity[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentRound, setCurrentRound] = useState(1)
  const [error, setError] = useState<string | null>(null)

  const evaluateImage = async (imageData: string) => {
    setIsLoading(true)
    setError(null)
    try {
      console.log('Starting evaluation...')
      const base64Data = processBase64Image(imageData)
      
      const response = await fetch('http://localhost:8000/evaluator/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Data,
          current_round: currentRound
        })
      })

      if (!response.ok) {
        const errorData = await response.text()
        console.error('Server error:', errorData)
        setError(`Evaluation failed: ${errorData}`)
        return
      }

      const newEvaluation = await response.json()
      console.log('Received evaluation:', newEvaluation)
      setEvaluations(prev => [newEvaluation, ...prev])
      setCurrentRound(prev => prev + 1)
    } catch (error) {
      console.error('Evaluation failed:', error)
      setError(error instanceof Error ? error.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  useImperativeHandle(ref, () => ({
    evaluateImage
  }))

  return (
    <div className="evaluator-container">
      <div className="evaluator-header">
        <h2 className="evaluator-title">Mystery Evaluator</h2>
        {isLoading && <div className="loading-indicator">Evaluating...</div>}
        {error && <div className="error-message">{error}</div>}
      </div>
      <div className="evaluations-list">
        {evaluations.map((entity, index) => (
          <div key={index} className="evaluation-card">
            <span className={`score-badge ${entity.score === 10 ? 'perfect' : ''}`}>
              Score: {entity.score}/10
            </span>
            <p className="judgment-text">{entity.feedback}</p>
            <div className="hidden-markers">
              {entity.hidden_markers.missing_elements.length > 0 && (
                <p>Missing concepts: {entity.hidden_markers.missing_elements.join(', ')}</p>
              )}
              {entity.hidden_markers.color_violations.length > 0 && (
                <p>Color violations: {entity.hidden_markers.color_violations.join(', ')}</p>
              )}
              <p>Close to expectation: {(entity.hidden_markers.similarity_score * 100).toFixed(1)}%</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})

export type { EvaluationEntity } 