import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { progressTracker } from '../utils/smartContent';

interface UseProgressTrackingOptions {
  componentId?: string;
  sectionId?: string;
  autoTrack?: boolean;
}

export const useProgressTracking = (options: UseProgressTrackingOptions = {}) => {
  const { componentId, sectionId, autoTrack = true } = options;
  const location = useLocation();
  const startTimeRef = useRef<Date>(new Date());
  const hasTrackedVisitRef = useRef<boolean>(false);

  // Extract component ID from path if not provided
  const extractedComponentId = componentId || extractComponentIdFromPath(location.pathname);
  const extractedSectionId = sectionId || extractSectionIdFromPath(location.pathname);

  useEffect(() => {
    if (!autoTrack || !extractedComponentId) return;

    // Track visit when component loads
    if (!hasTrackedVisitRef.current) {
      if (extractedSectionId) {
        progressTracker.visitSection(extractedComponentId, extractedSectionId);
      }
      hasTrackedVisitRef.current = true;
    }

    // Track time spent when component unmounts or location changes
    return () => {
      const endTime = new Date();
      const timeSpent = Math.round((endTime.getTime() - startTimeRef.current.getTime()) / 1000 / 60); // minutes
      
      if (timeSpent > 0) {
        const currentProgress = progressTracker.getComponentProgress(extractedComponentId);
        progressTracker.updateProgress(extractedComponentId, {
          timeSpent: (currentProgress?.timeSpent || 0) + timeSpent,
          lastVisited: endTime
        });
      }
    };
  }, [extractedComponentId, extractedSectionId, autoTrack]);

  // Reset tracking when location changes
  useEffect(() => {
    startTimeRef.current = new Date();
    hasTrackedVisitRef.current = false;
  }, [location.pathname]);

  // Manual tracking functions
  const trackSectionVisit = (compId: string, sectId: string) => {
    progressTracker.visitSection(compId, sectId);
  };

  const markCompleted = (compId: string) => {
    progressTracker.updateProgress(compId, { completed: true });
  };

  const addRating = (compId: string, rating: number) => {
    progressTracker.updateProgress(compId, { rating });
  };

  const addNotes = (compId: string, notes: string) => {
    progressTracker.updateProgress(compId, { notes });
  };

  const getProgress = (compId?: string) => {
    const targetId = compId || extractedComponentId;
    return targetId ? progressTracker.getComponentProgress(targetId) : null;
  };

  const getCompletionPercentage = (compId?: string, totalSections?: number) => {
    const targetId = compId || extractedComponentId;
    if (!targetId || !totalSections) return 0;
    return progressTracker.getCompletionPercentage(targetId, totalSections);
  };

  return {
    trackSectionVisit,
    markCompleted,
    addRating,
    addNotes,
    getProgress,
    getCompletionPercentage,
    currentComponentId: extractedComponentId,
    currentSectionId: extractedSectionId
  };
};

// Helper functions to extract IDs from URL paths
function extractComponentIdFromPath(pathname: string): string | null {
  const match = pathname.match(/\/components\/([^\/]+)/);
  return match ? match[1] : null;
}

function extractSectionIdFromPath(pathname: string): string | null {
  const parts = pathname.split('/');
  if (parts.length >= 4 && parts[1] === 'components') {
    return parts[parts.length - 1];
  }
  return null;
}