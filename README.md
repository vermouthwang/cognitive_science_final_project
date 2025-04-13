# Multi-AI Agent Collaboration Platform

A research platform focused on studying distributed cognition through AI agent collaboration.

## 🎯 Project Overview

This platform facilitates multi-AI-agent collaboration for creative tasks, specifically designed to research distributed cognition patterns. The system enables interaction between users and various AI agents, including Creative Collaborators, Domain Consultants, and Mystery Evaluators.

## 🔄 Main Task Flow

1. **Initial Phase**
   - User submits requirements
   - User uploads initial draft
   - Creative Collaborator generates first logo variant

2. **Iteration Phase**
   - Asynchronous communication between user and Collaborator
   - User uploads revised drafts
   - Collaborator generates new variants
   - Process repeats for 2 rounds

3. **Evaluation Phase**
   - Mystery Evaluator scores the design
   - Scores are broadcast to all agents
   - Process continues until 3 evaluations are reached

## 🤝 Domain Consultant Intervention

The platform features an asynchronous Domain Consultant that:
- Proactively suggests improvements every 2 minutes
- Provides expert advice (e.g., "Gold enhances luxury but control saturation")
- Allows users to:
  - Adopt (auto-syncs to next iteration)
  - Archive (saves to Knowledge Base)
  - Ignore suggestions

## 🛠️ Technical Stack

- Frontend: React + TypeScript + Vite
- Build Tools: Vite
- Type Checking: TypeScript
- Linting: ESLint

## 🚀 Getting Started

1. Clone the repository
```bash
git clone [repository-url]
```

2. Install dependencies
```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start the development server
```bash
# Frontend
npm run dev

# Backend
python run.py
```


### ESLint Configuration

For production applications, we recommend enabling type-aware lint rules. Update your `eslint.config.js`:

```js
export default tseslint.config({
  extends: [
    ...tseslint.configs.recommendedTypeChecked,
    // or ...tseslint.configs.strictTypeChecked for stricter rules
  ],
  languageOptions: {
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

