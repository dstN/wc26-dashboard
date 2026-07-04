import { describe, it, expect } from "vitest";
import { render } from "@testing-library/svelte";
import StatTable from "./StatTable.svelte";

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

describe("StatTable", () => {
  it("renders a table with aria-label", () => {
    const { container } = render(StatTable, { props: { stats, team_a: teamA, team_b: teamB } });
    const table = container.querySelector("table");
    expect(table?.getAttribute("aria-label")).toBeTruthy();
  });

  it("shows team names in header", () => {
    const { getByText } = render(StatTable, { props: { stats, team_a: teamA, team_b: teamB } });
    expect(getByText("Germany")).toBeTruthy();
    expect(getByText("Curaçao")).toBeTruthy();
  });

  it("shows Goals row with correct values", () => {
    const { getByText, getAllByText } = render(StatTable, {
      props: { stats, team_a: teamA, team_b: teamB },
    });
    expect(getByText("Goals")).toBeTruthy();
    expect(getAllByText("7").length).toBeGreaterThan(0);
    expect(getAllByText("1").length).toBeGreaterThan(0);
  });

  it("renders at least 7 rows", () => {
    const { container } = render(StatTable, { props: { stats, team_a: teamA, team_b: teamB } });
    const rows = container.querySelectorAll(".stat-table__row");
    expect(rows.length).toBeGreaterThanOrEqual(7);
  });
});
