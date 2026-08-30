import React from "react";

interface ProjectPaginationProps {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const ProjectPagination: React.FC<ProjectPaginationProps> = ({
  page,
  pageSize,
  total,
  totalPages,
  onPageChange,
}) => {
  if (total === 0) return null;

  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  // Pagination window generation
  const getPageNumbers = () => {
    const pages = [];
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (page <= 3) {
        pages.push(1, 2, 3, -1, totalPages);
      } else if (page >= totalPages - 2) {
        pages.push(1, -1, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, -1, page, -1, totalPages);
      }
    }
    return pages;
  };

  return (
    <div className="pagination-container">
      <div className="pagination-showing">
        SHOWING {start.toLocaleString()}–{end.toLocaleString()} OF {total.toLocaleString()} PROJECTS
      </div>
      <div className="pagination-controls">
        <button
          type="button"
          className="pagination-nav-btn"
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          PREVIOUS
        </button>
        <div className="pagination-pages">
          {getPageNumbers().map((p, idx) => {
            if (p === -1) {
              return (
                <span key={`ellipsis-${idx}`} className="pagination-ellipsis">
                  ...
                </span>
              );
            }
            return (
              <button
                key={p}
                type="button"
                className={`pagination-page-btn ${p === page ? "active" : "inactive"}`}
                onClick={() => onPageChange(p)}
              >
                {p.toString().padStart(2, "0")}
              </button>
            );
          })}
        </div>
        <button
          type="button"
          className="pagination-nav-btn"
          disabled={page === totalPages || totalPages === 0}
          onClick={() => onPageChange(page + 1)}
        >
          NEXT
        </button>
      </div>
    </div>
  );
};
