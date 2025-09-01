import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { NAV, findByPath, NavNode } from '../nav';

export interface NavigationItem {
  current: NavNode | undefined;
  previous: NavNode | undefined;
  next: NavNode | undefined;
  progress: {
    currentIndex: number;
    total: number;
    percentage: number;
  };
  siblings: NavNode[];
}

/**
 * Hook for managing navigation between sibling pages in a learning sequence
 * Provides current, previous, next items and progress tracking
 */
export const useNavigationSequence = (): NavigationItem => {
  const { pathname } = useLocation();

  return useMemo(() => {
    // Find current page node
    const current = findByPath(NAV.hubs, pathname);
    
    if (!current) {
      return {
        current: undefined,
        previous: undefined,
        next: undefined,
        progress: { currentIndex: -1, total: 0, percentage: 0 },
        siblings: []
      };
    }

    // Find parent to get siblings
    const findParentWithChildren = (nodes: NavNode[], targetPath: string): NavNode | undefined => {
      for (const node of nodes) {
        if (node.children) {
          // Check if any child matches the target
          if (node.children.some(child => child.path === targetPath)) {
            return node;
          }
          // Recursively search deeper
          const found = findParentWithChildren(node.children, targetPath);
          if (found) return found;
        }
      }
      return undefined;
    };

    const parent = findParentWithChildren(NAV.hubs, pathname);
    const siblings = parent?.children || [];
    
    const currentIndex = siblings.findIndex(item => item.path === pathname);
    const previous = currentIndex > 0 ? siblings[currentIndex - 1] : undefined;
    const next = currentIndex < siblings.length - 1 ? siblings[currentIndex + 1] : undefined;
    
    const progress = {
      currentIndex,
      total: siblings.length,
      percentage: siblings.length > 0 ? Math.round(((currentIndex + 1) / siblings.length) * 100) : 0
    };

    return {
      current,
      previous,
      next,
      progress,
      siblings
    };
  }, [pathname]);
};

/**
 * Hook for getting section navigation within the current hub
 */
export const useHubNavigation = () => {
  const { pathname } = useLocation();

  return useMemo(() => {
    // Extract hub from path (e.g., /components/dc-motor -> components)
    const pathParts = pathname.split('/').filter(Boolean);
    const hubId = pathParts[0];
    
    const hub = NAV.hubs.find(h => h.id === hubId);
    const hubPath = `/${hubId}`;
    
    // For components hub, also get current component
    let currentComponent: NavNode | undefined;
    if (hubId === 'components' && pathParts.length >= 2) {
      const componentId = pathParts[1];
      currentComponent = hub?.children?.find(c => c.id === componentId);
    }

    return {
      hub,
      hubPath,
      currentComponent,
      isInHub: !!hub,
      components: hub?.children || []
    };
  }, [pathname]);
};