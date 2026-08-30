import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App smoke test", () => {
  it("renders the initial IRIS header", () => {
    render(<App />);
    expect(screen.getByText(/IRIS — Infrastructure Risk Intelligence System/i)).toBeInTheDocument();
  });
});
