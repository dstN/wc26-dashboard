import { describe, it, expect, beforeEach, vi } from "vitest";

// Mock document for node environment
const mockDocEl = {
  getAttribute: vi.fn(),
  setAttribute: vi.fn(),
};

vi.stubGlobal("document", {
  documentElement: mockDocEl,
});

vi.stubGlobal("localStorage", {
  getItem: vi.fn(),
  setItem: vi.fn(),
});

describe("theme module", () => {
  beforeEach(() => {
    vi.resetModules();
    mockDocEl.getAttribute.mockReturnValue("light");
    vi.mocked(localStorage.setItem).mockReset();
    vi.mocked(document.documentElement.setAttribute).mockReset();
  });

  it("reads initial theme from data-theme attribute", async () => {
    mockDocEl.getAttribute.mockReturnValue("dark");
    const { getTheme } = await import("./theme.svelte");
    expect(getTheme()).toBe("dark");
  });

  it("toggleTheme switches light to dark", async () => {
    mockDocEl.getAttribute.mockReturnValue("light");
    const { toggleTheme, getTheme } = await import("./theme.svelte");
    toggleTheme();
    expect(document.documentElement.setAttribute).toHaveBeenCalledWith("data-theme", "dark");
    expect(localStorage.setItem).toHaveBeenCalledWith("efi-theme", "dark");
  });

  it("toggleTheme switches dark to light", async () => {
    mockDocEl.getAttribute.mockReturnValue("dark");
    const { toggleTheme } = await import("./theme.svelte");
    toggleTheme();
    expect(document.documentElement.setAttribute).toHaveBeenCalledWith("data-theme", "light");
  });
});
