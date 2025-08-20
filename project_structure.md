# Instagram Reels Analysis - Project Architecture

## System Overview

```mermaid
flowchart TD
    A[User] -->|Interacts with| B[Main Application]
    B --> C[Authentication Module]
    B --> D[Data Collection]
    B --> E[Content Analysis]
    B --> F[User Interface]
    
    C -->|Uses| C1[Instagram API]
    D -->|Collects| D1[Reels Data]
    E -->|Analyzes| E1[Content]
    E -->|Generates| E2[Insights]
    F -->|Displays| F1[Analysis Results]
    
    G[(Database)] <-->|Stores/Retrieves| B
    H[.env] -->|Configuration| B
```

## Component Architecture

```mermaid
classDiagram
    class InstagramAuth {
        +login(username, password)
        +handle_two_factor(otp)
        +fetch_explore_reels(limit)
        +logout()
    }
    
    class ReelProcessor {
        +comprehensive_analysis(reels, config)
        +analyze_sentiment(content)
        +categorize_content(content)
    }
    
    class Config {
        +load_environment()
        +validate()
        -username
        -password
        -target_reels
    }
    
    class GradioInterface {
        +launch_app(auth, config)
        +display_results(analysis)
        +handle_user_input()
    }
    
    InstagramAuth --> Config
    ReelProcessor --> Config
    GradioInterface --> InstagramAuth
    GradioInterface --> ReelProcessor
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Application
    participant I as Instagram API
    participant D as Database
    
    U->>A: Start Application
    A->>I: Authenticate
    I-->>A: Authentication Token
    
    loop For each analysis
        U->>A: Request Analysis
        A->>I: Fetch Reels Data
        I-->>A: Reels JSON
        A->>A: Process & Analyze
        A->>D: Store Results
        A-->>U: Display Insights
    end
    
    U->>A: Logout
    A->>I: End Session
```

## Deployment Architecture

```mermaid
graph TD
    subgraph Local Development
        A[Local Machine] -->|Runs| B[Python Application]
        B -->|Reads| C[.env File]
        B -->|Stores| D[Local Database]
    end
    
    subgraph Production
        E[Web Server] -->|Hosts| F[Gradio Interface]
        F -->|Connects to| G[Instagram API]
        G -->|Returns| H[Reels Data]
        F -->|Stores| I[Cloud Database]
    end
    
    A -.->|Deploy| E
```

## Personality Integration

```mermaid
flowchart LR
    A[User Profile] -->|Influences| B[Content Preferences]
    B --> C[Analysis Parameters]
    C --> D[Personalized Results]
    
    subgraph Profile Analysis
        E[Personality Traits] --> F[Content Affinity]
        E --> G[Engagement Style]
        E --> H[Interaction Patterns]
    end
    
    D -->|Feeds back into| A
```

## Error Handling

```mermaid
stateDiagram-v2
    [*] --> Authentication
    Authentication --> DataCollection: Success
    Authentication --> RetryAuth: Failed
    
    DataCollection --> Analysis: Data Retrieved
    DataCollection --> HandleAPIError: API Error
    
    Analysis --> DisplayResults: Success
    Analysis --> HandleAnalysisError: Error
    
    RetryAuth --> Authentication: Retry
    RetryAuth --> [*]: Max Retries Reached
    
    HandleAPIError --> [*]: Fatal Error
    HandleAPIError --> DataCollection: Retry
    
    HandleAnalysisError --> [*]: Fatal Error
    HandleAnalysisError --> DataCollection: Retry with Different Parameters
```

## Development Workflow

```mermaid
gantt
    title Project Development Timeline
    dateFormat  YYYY-MM-DD
    section Core Development
    Authentication       :done,    des1, 2025-08-15, 3d
    Data Collection      :active,  des2, 2025-08-18, 5d
    Content Analysis     :         des3, 2025-08-23, 5d
    
    section UI/UX
    CLI Interface        :done,    des4, 2025-08-16, 2d
    Web Interface        :         des5, 2025-08-25, 7d
    
    section Testing
    Unit Tests           :         des6, 2025-08-22, 3d
    Integration Tests    :         des7, 2025-08-26, 3d
    User Acceptance      :         des8, 2025-08-29, 2d
```
