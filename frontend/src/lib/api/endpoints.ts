import { apiFetch } from './client';
import type { DashboardData, MatchStats, TeamSpatial, Phase, LineBreak, FinalThirdEntry } from '$lib/types/efi';

export async function getDashboard(fetchFn?: typeof fetch): Promise<DashboardData> {
	return apiFetch<DashboardData>('/api/v1/dashboard?is_featured=1', fetchFn);
}

export async function getMatchPossession(id: number, fetchFn?: typeof fetch): Promise<MatchStats> {
	return apiFetch<MatchStats>(`/api/v1/matches/${id}/possession`, fetchFn);
}

export async function getMatchSpatial(
	id: number,
	fetchFn?: typeof fetch
): Promise<{ team_a: TeamSpatial[]; team_b: TeamSpatial[] }> {
	return apiFetch(`/api/v1/matches/${id}/spatial`, fetchFn);
}

export async function getMatchPhases(
	id: number,
	fetchFn?: typeof fetch
): Promise<{ team_a: Phase[]; team_b: Phase[] }> {
	return apiFetch(`/api/v1/matches/${id}/phases`, fetchFn);
}

export async function getMatchLineBreaks(
	id: number,
	fetchFn?: typeof fetch
): Promise<{ team_a: LineBreak[]; team_b: LineBreak[] }> {
	return apiFetch(`/api/v1/matches/${id}/line-breaks`, fetchFn);
}

export async function getMatchFinalThird(
	id: number,
	fetchFn?: typeof fetch
): Promise<{ team_a: FinalThirdEntry[]; team_b: FinalThirdEntry[] }> {
	return apiFetch(`/api/v1/matches/${id}/final-third`, fetchFn);
}
