import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProjectPagination } from '../../../components/projects/ProjectPagination';

describe('ProjectPagination', () => {
  it('renders correctly with given props', () => {
    render(
      <ProjectPagination 
        page={2} 
        pageSize={25} 
        total={4738} 
        totalPages={190} 
        onPageChange={() => {}} 
      />
    );

    // Should show correct item range
    expect(screen.getByText('SHOWING 26–50 OF 4,738 PROJECTS')).toBeInTheDocument();
  });

  it('does not render if total is 0', () => {
    const { container } = render(
      <ProjectPagination 
        page={1} 
        pageSize={25} 
        total={0} 
        totalPages={0} 
        onPageChange={() => {}} 
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('calls onPageChange when previous/next are clicked', () => {
    const onPageChange = vi.fn();
    render(
      <ProjectPagination 
        page={2} 
        pageSize={25} 
        total={100} 
        totalPages={4} 
        onPageChange={onPageChange} 
      />
    );

    fireEvent.click(screen.getByText('PREVIOUS'));
    expect(onPageChange).toHaveBeenCalledWith(1);

    fireEvent.click(screen.getByText('NEXT'));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('disables previous button on page 1', () => {
    render(
      <ProjectPagination 
        page={1} 
        pageSize={25} 
        total={100} 
        totalPages={4} 
        onPageChange={() => {}} 
      />
    );
    expect(screen.getByText('PREVIOUS')).toBeDisabled();
  });

  it('disables next button on last page', () => {
    render(
      <ProjectPagination 
        page={4} 
        pageSize={25} 
        total={100} 
        totalPages={4} 
        onPageChange={() => {}} 
      />
    );
    expect(screen.getByText('NEXT')).toBeDisabled();
  });
});
