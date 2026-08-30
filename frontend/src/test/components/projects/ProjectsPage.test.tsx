import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ProjectsPage } from '../../../pages/ProjectsPage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

// Mock the API calls
vi.mock('@/api/projects.ts', () => ({
  fetchProjects: vi.fn(() => Promise.resolve({
    items: [
      {
        id: 1,
        project_code: 'PRJ-TEST',
        project_name: 'Test Project',
        agency: 'Test Agency',
        ministry: null,
        sector: 'Test Sector',
        state: 'TS',
        report_month: '2024-02',
        approval_date: null,
        original_completion_date: null,
        revised_completion_date: null,
        original_cost: null,
        revised_cost: null,
        cumulative_expenditure: null,
        physical_progress: 50.0,
      }
    ],
    total: 1,
    page: 1,
    page_size: 25,
    total_pages: 1,
  })),
  fetchFilterOptions: vi.fn(() => Promise.resolve({
    sectors: [], agencies: [], states: [], report_months: [],
  })),
}));

vi.mock('@/api/system.ts', () => ({
  fetchDatasetInfo: vi.fn(() => Promise.resolve({
    status: 'ACTIVE',
    covered_months: ['2023-01', '2024-02'],
    row_count: 100,
    unique_projects_count: 50,
    canonical_sha256: 'abc'
  })),
}));

describe('ProjectsPage', () => {
  beforeEach(() => {
    queryClient.clear();
  });

  it('renders page layout and fetches data', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ProjectsPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Initial loading or loaded state
    expect(screen.getByText('IRIS / PROJECTS / DISCOVERY')).toBeInTheDocument();

    // Check system info renders
    await waitFor(() => {
      expect(screen.getByText('50 UNIQUE PROJECTS')).toBeInTheDocument();
      expect(screen.getByText('100 OBSERVATIONS')).toBeInTheDocument();
      expect(screen.getByText('2023-01 → 2024-02')).toBeInTheDocument();
    });

    // Check project data renders
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
      expect(screen.getByText('1 MATCHING PROJECTS')).toBeInTheDocument();
    });
  });
});
