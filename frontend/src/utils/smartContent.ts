export interface UserProgress {
  componentId: string;
  sectionsVisited: string[];
  timeSpent: number; // in minutes
  lastVisited: Date;
  completed: boolean;
  rating?: number; // 1-5 stars
  notes?: string;
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  components: string[];
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  estimatedTime: string;
  prerequisites: string[];
}

export interface SmartSuggestion {
  componentId: string;
  reason: 'prerequisite' | 'next-step' | 'related' | 'popular' | 'difficulty-match';
  confidence: number; // 0-1
  explanation: string;
}

class ProgressTracker {
  private readonly STORAGE_KEY = 'ctrlhub-progress';
  
  // Get user's progress for all components
  getAllProgress(): UserProgress[] {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  }
  
  // Get progress for specific component
  getComponentProgress(componentId: string): UserProgress | null {
    const allProgress = this.getAllProgress();
    return allProgress.find(p => p.componentId === componentId) || null;
  }
  
  // Update progress for a component
  updateProgress(componentId: string, updates: Partial<UserProgress>): void {
    const allProgress = this.getAllProgress();
    const existingIndex = allProgress.findIndex(p => p.componentId === componentId);
    
    if (existingIndex >= 0) {
      allProgress[existingIndex] = { ...allProgress[existingIndex], ...updates };
    } else {
      allProgress.push({
        componentId,
        sectionsVisited: [],
        timeSpent: 0,
        lastVisited: new Date(),
        completed: false,
        ...updates
      });
    }
    
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(allProgress));
  }
  
  // Mark section as visited
  visitSection(componentId: string, sectionId: string): void {
    const progress = this.getComponentProgress(componentId);
    const sectionsVisited = progress?.sectionsVisited || [];
    
    if (!sectionsVisited.includes(sectionId)) {
      sectionsVisited.push(sectionId);
    }
    
    this.updateProgress(componentId, {
      sectionsVisited,
      lastVisited: new Date()
    });
  }
  
  // Calculate completion percentage
  getCompletionPercentage(componentId: string, totalSections: number): number {
    const progress = this.getComponentProgress(componentId);
    if (!progress || totalSections === 0) return 0;
    
    return Math.round((progress.sectionsVisited.length / totalSections) * 100);
  }
  
  // Get learning statistics
  getLearningStats(): {
    totalComponents: number;
    completedComponents: number;
    totalTimeSpent: number;
    averageRating: number;
    streakDays: number;
  } {
    const allProgress = this.getAllProgress();
    
    const totalComponents = allProgress.length;
    const completedComponents = allProgress.filter(p => p.completed).length;
    const totalTimeSpent = allProgress.reduce((sum, p) => sum + p.timeSpent, 0);
    const ratingsSum = allProgress.filter(p => p.rating).reduce((sum, p) => sum + (p.rating || 0), 0);
    const ratingsCount = allProgress.filter(p => p.rating).length;
    const averageRating = ratingsCount > 0 ? ratingsSum / ratingsCount : 0;
    
    // Calculate streak (simplified - consecutive days with activity)
    const streakDays = this.calculateStreakDays(allProgress);
    
    return {
      totalComponents,
      completedComponents,
      totalTimeSpent,
      averageRating,
      streakDays
    };
  }
  
  private calculateStreakDays(progress: UserProgress[]): number {
    const activityDates = progress
      .map(p => new Date(p.lastVisited).toDateString())
      .filter((date, index, arr) => arr.indexOf(date) === index)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime());
    
    let streak = 0;
    const today = new Date().toDateString();
    let checkDate = new Date();
    
    for (const activityDate of activityDates) {
      const checkDateStr = checkDate.toDateString();
      if (activityDate === checkDateStr) {
        streak++;
        checkDate.setDate(checkDate.getDate() - 1);
      } else {
        break;
      }
    }
    
    return streak;
  }
}

// Predefined learning paths
export const LEARNING_PATHS: LearningPath[] = [
  {
    id: 'control-fundamentals',
    title: 'Control Systems Fundamentals',
    description: 'Start with actuators, add sensing, then implement control',
    components: ['dc-motor', 'encoder', 'arduino'],
    difficulty: 'Beginner',
    estimatedTime: '8-10 hours',
    prerequisites: []
  },
  {
    id: 'power-electronics',
    title: 'Power Electronics Mastery',
    description: 'Deep dive into motor drivers and power management',
    components: ['dc-motor', 'driver', 'stepper-motor'],
    difficulty: 'Intermediate',
    estimatedTime: '10-12 hours',
    prerequisites: ['control-fundamentals']
  },
  {
    id: 'advanced-actuation',
    title: 'Advanced Actuation Systems',
    description: 'Master different types of motors and precision control',
    components: ['dc-motor', 'stepper-motor', 'encoder', 'driver'],
    difficulty: 'Advanced',
    estimatedTime: '12-15 hours',
    prerequisites: ['control-fundamentals', 'power-electronics']
  }
];

class SmartContentOrganizer {
  constructor(private progressTracker: ProgressTracker) {}
  
  // Get personalized suggestions based on user progress
  getSmartSuggestions(limit: number = 3): SmartSuggestion[] {
    const allProgress = this.progressTracker.getAllProgress();
    const suggestions: SmartSuggestion[] = [];
    
    // Add prerequisite-based suggestions
    suggestions.push(...this.getPrerequisiteSuggestions(allProgress));
    
    // Add next-step suggestions
    suggestions.push(...this.getNextStepSuggestions(allProgress));
    
    // Add difficulty-matched suggestions
    suggestions.push(...this.getDifficultyMatchedSuggestions(allProgress));
    
    // Add popular content suggestions
    suggestions.push(...this.getPopularSuggestions(allProgress));
    
    // Sort by confidence and return top suggestions
    return suggestions
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, limit);
  }
  
  private getPrerequisiteSuggestions(progress: UserProgress[]): SmartSuggestion[] {
    const completedComponents = progress.filter(p => p.completed).map(p => p.componentId);
    const suggestions: SmartSuggestion[] = [];
    
    // Check learning paths for next logical steps
    for (const path of LEARNING_PATHS) {
      const pathProgress = path.components.filter(comp => completedComponents.includes(comp));
      const nextComponent = path.components.find(comp => !completedComponents.includes(comp));
      
      if (pathProgress.length > 0 && nextComponent) {
        suggestions.push({
          componentId: nextComponent,
          reason: 'next-step',
          confidence: 0.9,
          explanation: `Next in ${path.title} learning path`
        });
      }
    }
    
    return suggestions;
  }
  
  private getNextStepSuggestions(progress: UserProgress[]): SmartSuggestion[] {
    // Implementation for next step suggestions based on component relationships
    return [];
  }
  
  private getDifficultyMatchedSuggestions(progress: UserProgress[]): SmartSuggestion[] {
    // Implementation for difficulty-matched suggestions
    return [];
  }
  
  private getPopularSuggestions(progress: UserProgress[]): SmartSuggestion[] {
    const visitedComponents = progress.map(p => p.componentId);
    const suggestions: SmartSuggestion[] = [];
    
    // Suggest popular components not yet visited
    const popularComponents = ['dc-motor', 'arduino', 'encoder'];
    
    for (const comp of popularComponents) {
      if (!visitedComponents.includes(comp)) {
        suggestions.push({
          componentId: comp,
          reason: 'popular',
          confidence: 0.6,
          explanation: 'Popular choice for beginners'
        });
      }
    }
    
    return suggestions;
  }
  
  // Get adaptive learning path based on user progress
  getAdaptiveLearningPath(): LearningPath | null {
    const stats = this.progressTracker.getLearningStats();
    const allProgress = this.progressTracker.getAllProgress();
    
    // Determine user's current level
    let userLevel: 'Beginner' | 'Intermediate' | 'Advanced';
    
    if (stats.completedComponents === 0) {
      userLevel = 'Beginner';
    } else if (stats.completedComponents < 3) {
      userLevel = 'Intermediate';
    } else {
      userLevel = 'Advanced';
    }
    
    // Find most suitable learning path
    const suitablePaths = LEARNING_PATHS.filter(path => {
      // Check if user meets prerequisites
      const hasPrerequisites = path.prerequisites.every(prereq => 
        LEARNING_PATHS.find(p => p.id === prereq)?.components.every(comp =>
          allProgress.find(progress => progress.componentId === comp)?.completed
        )
      );
      
      return path.difficulty === userLevel && hasPrerequisites;
    });
    
    return suitablePaths[0] || null;
  }
}

// Export singleton instances
export const progressTracker = new ProgressTracker();
export const smartContentOrganizer = new SmartContentOrganizer(progressTracker);