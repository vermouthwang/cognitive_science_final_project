# Project overview

This is a project for multi-ai-agent collaboration creation platform aim to research on cognitive science in terms of distribution cognition.

Main Task flow
graph TB  
    A[User submits initial requirements] --> B[User uploads draft + Creative Collaborator generates 1st logo variant]  
    B --> C[User and Collaborator communicate asynchronously]  
    C --> D[User uploads revised draft + Collaborator generates 2nd variant]  
    D --> E{2 rounds completed?}  
    E -- Yes --> F[Mystery Evaluator scores the design]  
    E -- No --> B  
    F --> G[Scores broadcast to all agents]  
    G --> H{3 evaluations reached?}  
    H -- No --> B  
    H -- Yes --> I[Task completed]  

Asynchronous Flow (Domain Consultant Intervention)graph LR  
    A'[Domain Consultant proactively suggests] -->|Random trigger (every 2 min)| B'[Displays expert advice (e.g., "Gold enhances luxury but control saturation")]  
    B' --> C'[User chooses: Adopt/Archive/Ignore]  
    C' -->|Adopt| D'[Suggestion auto-synced to next Collaborator iteration]  
    C' -->|Archive| E'[Suggestion saved to blue-area Knowledge Base]  

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```
