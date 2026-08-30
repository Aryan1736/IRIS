import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProjectSearch } from '../../../components/projects/ProjectSearch';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// Mock the API call
vi.mock('@/api/projects.ts', () => ({
  fetchFilterOptions: vi.fn(() => Promise.resolve({
    sectors: ['Transport', 'Energy'],
    agencies: ['Metro Auth', 'EPA'],
    states: ['NY', 'WA'],
    report_months: ['2024-01', '2024-02'],
  })),
}));

describe('ProjectSearch', () => {
  it('renders search input and filters', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{}} onFilterChange={() => {}} />
      </QueryClientProvider>
    );

    expect(screen.getByPlaceholderText(/Search project name/i)).toBeInTheDocument();
    expect(screen.getByText('SECTOR')).toBeInTheDocument();
    expect(screen.getByText('AGENCY')).toBeInTheDocument();
    expect(screen.getByText('STATE')).toBeInTheDocument();
  });

  it('calls onFilterChange when search input changes', async () => {
    const onFilterChange = vi.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{}} onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/Search project name/i), { target: { value: 'test' } });
    
    // Wait for debounce
    await waitFor(() => {
      expect(onFilterChange).toHaveBeenCalledWith({ search: 'test' });
    });
  });

  it('shows CLEAR FILTERS button when filters are active', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{ sector: 'Transport' }} onFilterChange={() => {}} />
      </QueryClientProvider>
    );
    expect(screen.getByText('CLEAR FILTERS')).toBeInTheDocument();
  });

  it('clears filters when CLEAR FILTERS is clicked', () => {
    const onFilterChange = vi.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{ sector: 'Transport' }} onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );
    
    fireEvent.click(screen.getByText('CLEAR FILTERS'));
    expect(onFilterChange).toHaveBeenCalledWith({});
  });
});
