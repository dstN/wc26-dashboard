import { describe, it, expect } from "vitest";
import { render } from "@testing-library/svelte";
import PossessionBar from "./PossessionBar.svelte";

const teamA = { id: 1, name: "Germany", short_code: "GER", slug: "germany", color: "red", group: "E" };
const teamB = { id: 2, name: "Curaçao", short_code: "CUW", slug: "curacao", color: "blue", group: "E" };

const stats = {
  possession_team_a: 57.8,
  possession_in_contest: 6.9,
  possession_team_b: 35.3,
  goals_a: 7,
  goals_b: 1,
  xg_a: 3.1,
  xg_b: 0.4,
  ball_recovery_time_avg: 4.2,
};

describe("PossessionBar", () => {
  it("renders three percentage values", () => {
    const { getByText } = render(PossessionBar, { props: { stats, team_a: teamA, team_b: teamB } });
    expect(getByText("57.8%")).toBeTruthy();
    expect(getByText("6.9%")).toBeTruthy();
    expect(getByText("35.3%")).toBeTruthy();
  });

  it("includes team names in aria-label", () => {
    const { container } = render(PossessionBar, { props: { stats, team_a: teamA, team_b: teamB } });
    const figure = container.querySelector("[role='img']");
    expect(figure?.getAttribute("aria-label")).toContain("Germany");
    expect(figure?.getAttribute("aria-label")).toContain("Curaçao");
  });

  it("renders all three bar segments", () => {
    const { container } = render(PossessionBar, { props: { stats, team_a: teamA, team_b: teamB } });
    const segs = container.querySelectorAll(".possession__seg");
    expect(segs.length).toBe(3);
  });
});
