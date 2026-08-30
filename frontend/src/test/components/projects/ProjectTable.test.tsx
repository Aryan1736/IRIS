import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProjectTable } from '../../../components/projects/ProjectTable';
import { BrowserRouter } from 'react-router-dom';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('ProjectTable', () => {
  const mockProjects = [
    {
      id: 1,
      project_code: 'PRJ-2023-UTX',
      project_name: 'Urban Transit Expansion',
      agency: 'Metro Auth',
      ministry: null,
      sector: 'Transport',
      state: 'NY',
      report_month: '2024-02',
      approval_date: null,
      original_completion_date: null,
      revised_completion_date: null,
      original_cost: null,
      revised_cost: null,
      cumulative_expenditure: null,
      physical_progress: 45.5,
    },
    {
      id: 2,
      project_code: 'PRJ-2022-NGM',
      project_name: 'Northern Grid',
      agency: null,
      ministry: null,
      sector: 'Energy',
      state: null,
      report_month: '2024-01',
      approval_date: null,
      original_completion_date: null,
      revised_completion_date: null,
      original_cost: null,
      revised_cost: null,
      cumulative_expenditure: null,
      physical_progress: null, // Null physical progress
    },
  ];

  it('renders table headers', () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={[]} />
      </BrowserRouter>
    );

    expect(screen.getByText('PROJECT')).toBeInTheDocument();
    expect(screen.getByText('PROJECT CODE')).toBeInTheDocument();
    expect(screen.getByText('SECTOR')).toBeInTheDocument();
    expect(screen.getByText('AGENCY')).toBeInTheDocument();
    expect(screen.getByText('STATE')).toBeInTheDocument();
    expect(screen.getByText('LATEST REPORT')).toBeInTheDocument();
    expect(screen.getByText('PHYSICAL PROGRESS')).toBeInTheDocument();
  });

  it('renders project data correctly', () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={mockProjects} />
      </BrowserRouter>
    );

    expect(screen.getByText('Urban Transit Expansion')).toBeInTheDocument();
    expect(screen.getByText('PRJ-2023-UTX')).toBeInTheDocument();
    expect(screen.getByText('Transport')).toBeInTheDocument();
    expect(screen.getByText('NY')).toBeInTheDocument();
    expect(screen.getByText('45.5%')).toBeInTheDocument(); // Formats progress
    
    expect(screen.getByText('Northern Grid')).toBeInTheDocument();
    expect(screen.getByText('PRJ-2022-NGM')).toBeInTheDocument();
    expect(screen.getByText('Energy')).toBeInTheDocument();
    
    // Check "—" fallback for null physical progress
    const fallbacks = screen.getAllByText('—');
    expect(fallbacks.length).toBeGreaterThan(0);
  });

  it('navigates to project detail on row click', () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={mockProjects} />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText('Urban Transit Expansion'));
    expect(mockNavigate).toHaveBeenCalledWith('/projects/PRJ-2023-UTX');
  });

  it('displays empty state when no projects provided', () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={[]} />
      </BrowserRouter>
    );
    expect(screen.getByText('NO PROJECTS FOUND MATCHING FILTERS.')).toBeInTheDocument();
  });
});
