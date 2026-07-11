<script lang="ts">
	import type { PageData } from './$types';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import TermTooltip from '$lib/components/layout/TermTooltip.svelte';
	import { sortableHeader } from '$lib/actions/sortableHeader';
	import { teamColorVar, teamTextColor, flagCode, badgeTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';
	import { toggleComparison, isSelected, getComparisonIds, MAX_COMPARISON } from '$lib/stores/comparison.svelte';

	let { data }: { data: PageData } = $props();

	interface PlayerEntry {
		id: number;
		name: string;
		position: string | null;
		jersey_number: number | null;
		team: { id: number; name: string; short_code: string; color: string; slug: string };
	}
	interface PlayerStatEntry {
		appearances: number;
		goals: number;
		yellow_cards: number;
		red_cards: number;
		minutes_played: number;
		passes_attempted?: number | null;
		passes_completed?: number | null;
		take_ons?: number | null;
		ball_progressions?: number | null;
		attempts_at_goal?: number | null;
		tackles_made?: number | null;
		tackles_won?: number | null;
		blocks?: number | null;
		interceptions?: number | null;
		clearances?: number | null;
		duels_won_aerial?: number | null;
		duels_won_physical?: number | null;
		possession_regains?: number | null;
		pressing_direct?: number | null;
		total_offers?: number | null;
		offers_received?: number | null;
		total_distance_m?: number | null;
		high_speed_runs?: number | null;
		sprints?: number | null;
		top_speed_kmh?: number | null;
		// computed / derived
		goals_per_shot?: number | null;
		goals_per_game?: number | null;
		pass_completion_pct?: number | null;
		km_per_game?: number | null;
		sprints_per_game?: number | null;
	}

	function computeDerived(s: PlayerStatEntry): PlayerStatEntry {
		const shots = s.attempts_at_goal ?? 0;
		const goals_per_shot = shots >= 1
			? Math.round((s.goals / shots) * 100) / 100
			: null;
		const pa = s.passes_attempted ?? 0;
		const pass_completion_pct = pa >= 1
			? Math.round(((s.passes_completed ?? 0) / pa) * 100)
			: null;
		const apps = s.appearances > 0 ? s.appearances : 1;
		const km_per_game = s.total_distance_m != null
			? Math.round(s.total_distance_m / 1000 / apps * 10) / 10
			: null;
		const sprints_per_game = s.sprints != null
			? Math.round(s.sprints / apps * 10) / 10
			: null;
		const goals_per_game = s.appearances > 0
			? Math.round(s.goals / s.appearances * 100) / 100
			: null;
		return { ...s, goals_per_shot, goals_per_game, pass_completion_pct, km_per_game, sprints_per_game };
	}

	interface GkRankEntry {
		gk_name: string;
		player_id: number | null;
		team: { id: number; name: string; short_code: string; color: string; slug: string };
		matches: number;
		total_attempts_faced: number | null;
		avg_save_pct: number | null;
		total_goal_interventions: number | null;
		total_aerial_interventions: number | null;
		total_crosses_faced: number | null;
		total_involvements: number | null;
		total_distributions: number | null;
	}

	const players: PlayerEntry[] = $derived(data.players ?? []);
	const playerStats: Record<string, PlayerStatEntry> = $derived(data.playerStats ?? {});
	const goalkeepers: GkRankEntry[] = $derived(data.goalkeepers ?? []);

	// Enrich players with stats + computed derived fields
	const enriched = $derived(
		players.map((p) => {
			const raw = playerStats[String(p.id)] ?? null;
			return { ...p, stats: raw ? computeDerived(raw) : null };
		})
	);

	const POSITION_ORDER: Record<string, number> = { GK: 0, DF: 1, MF: 2, FW: 3 };
	const posColor: Record<string, string> = {
		GK: 'var(--c-lime-ink)', DF: 'var(--c-teal-ink)', MF: 'var(--c-blue-ink)', FW: 'var(--c-red-ink)'
	};
	const posLabel: Record<string, string> = { GK: 'GK', DF: 'DF', MF: 'MF', FW: 'FW' };

	// ── Ranking tables ────────────────────────────────────────────────────────
	const topScorers = $derived(
		enriched
			.filter((p) => (p.stats?.goals ?? 0) > 0)
			.sort((a, b) => (b.stats?.goals ?? 0) - (a.stats?.goals ?? 0))
	);

	const topDefenders = $derived(
		enriched
			.filter((p) => p.position === 'DF' || p.position === 'MF')
			.filter((p) => (p.stats?.possession_regains ?? 0) > 0)
			.sort((a, b) => (b.stats?.possession_regains ?? 0) - (a.stats?.possession_regains ?? 0))
	);

	const topMidfielders = $derived(
		enriched
			.filter((p) => p.position === 'MF')
			.filter((p) => (p.stats?.passes_attempted ?? 0) >= 20)
			.sort((a, b) => (b.stats?.pass_completion_pct ?? 0) - (a.stats?.pass_completion_pct ?? 0))
	);

	const topForwards = $derived(
		enriched
			.filter((p) => p.position === 'FW')
			.filter((p) => (p.stats?.attempts_at_goal ?? 0) >= 1)
			.sort((a, b) => (b.stats?.goals_per_shot ?? 0) - (a.stats?.goals_per_shot ?? 0))
	);

	const physicalLeaders = $derived(
		enriched
			.filter((p) => (p.stats?.km_per_game ?? 0) > 0)
			.sort((a, b) => (b.stats?.km_per_game ?? 0) - (a.stats?.km_per_game ?? 0))
	);

	const disciplined = $derived(
		enriched
			.map((p) => ({
				...p,
				discipline_total: (p.stats?.yellow_cards ?? 0) + (p.stats?.red_cards ?? 0)
			}))
			.filter((p) => p.discipline_total > 0)
			.sort((a, b) => b.discipline_total - a.discipline_total)
	);

	// ── Active ranking tab ────────────────────────────────────────────────────
	type Tab = 'scorers' | 'defenders' | 'midfielders' | 'forwards' | 'physical' | 'goalkeepers' | 'discipline';
	let activeTab: Tab = $state('scorers');

	// defined in the script block so no `as const` assertion sits in template markup
	const RANKING_TABS = $derived([
		{ key: 'scorers',     label: $t.players.tabTopGoals },
		{ key: 'defenders',   label: $t.players.tabTopDefenders },
		{ key: 'midfielders', label: $t.players.tabTopMidfielders },
		{ key: 'forwards',    label: $t.players.tabTopForwards },
		{ key: 'physical',    label: $t.players.tabPhysical },
		{ key: 'goalkeepers', label: $t.players.goalkeepers },
		{ key: 'discipline',  label: $t.players.tabDiscipline },
	] as const);

	// ── Per-tab sort state ────────────────────────────────────────────────────
	let scorersSort = $state('goals');              let scorersDir = $state<1|-1>(-1);
	let defendersSort = $state('possession_regains'); let defendersDir = $state<1|-1>(-1);
	let midfieldersSort = $state('pass_completion_pct'); let midfieldersDir = $state<1|-1>(-1);
	let forwardsSort = $state('goals_per_shot');    let forwardsDir = $state<1|-1>(-1);
	let physicalSort = $state('km_per_game');       let physicalDir = $state<1|-1>(-1);
	let gkSort = $state('matches');                 let gkDir = $state<1|-1>(-1);
	let disciplineSort = $state('discipline_total'); let disciplineDir = $state<1|-1>(-1);

	function mkSort(getKey: () => string, setKey: (k: string) => void, getDir: () => 1|-1, setDir: (d: 1|-1) => void) {
		return (col: string) => {
			if (getKey() === col) setDir(getDir() === -1 ? 1 : -1);
			else { setKey(col); setDir(-1); }
		};
	}
	const sortScorers    = mkSort(() => scorersSort,    (k) => scorersSort = k,    () => scorersDir,    (d) => scorersDir = d);
	const sortDefenders  = mkSort(() => defendersSort,  (k) => defendersSort = k,  () => defendersDir,  (d) => defendersDir = d);
	const sortMids       = mkSort(() => midfieldersSort,(k) => midfieldersSort = k,() => midfieldersDir,(d) => midfieldersDir = d);
	const sortForwards   = mkSort(() => forwardsSort,   (k) => forwardsSort = k,   () => forwardsDir,   (d) => forwardsDir = d);
	const sortPhysical   = mkSort(() => physicalSort,   (k) => physicalSort = k,   () => physicalDir,   (d) => physicalDir = d);
	const sortGk         = mkSort(() => gkSort,         (k) => gkSort = k,         () => gkDir,         (d) => gkDir = d);
	const sortDiscipline = mkSort(() => disciplineSort, (k) => disciplineSort = k, () => disciplineDir, (d) => disciplineDir = d);

	function reSort<T extends { stats: PlayerStatEntry | null }>(arr: T[], key: string, dir: 1|-1): T[] {
		return [...arr].sort((a, b) => {
			const av = (a.stats as unknown as Record<string, unknown>)?.[key] as number ?? -Infinity;
			const bv = (b.stats as unknown as Record<string, unknown>)?.[key] as number ?? -Infinity;
			return dir * (av - bv);
		});
	}

	const sortedScorers    = $derived(reSort(topScorers,    scorersSort,    scorersDir));
	const sortedDefenders  = $derived(reSort(topDefenders,  defendersSort,  defendersDir));
	const sortedMidfielders= $derived(reSort(topMidfielders,midfieldersSort,midfieldersDir));
	const sortedForwards   = $derived(reSort(topForwards,   forwardsSort,   forwardsDir));
	const sortedPhysical   = $derived(reSort(physicalLeaders,physicalSort,  physicalDir));

	const sortedDiscipline = $derived(
		[...disciplined].sort((a, b) => {
			const key = disciplineSort;
			const av = key === 'discipline_total'
				? a.discipline_total
				: ((a.stats as unknown as Record<string, unknown>)?.[key] as number ?? -Infinity);
			const bv = key === 'discipline_total'
				? b.discipline_total
				: ((b.stats as unknown as Record<string, unknown>)?.[key] as number ?? -Infinity);
			return disciplineDir * (av - bv);
		})
	);

	function reSortGk(arr: GkRankEntry[], key: string, dir: 1|-1): GkRankEntry[] {
		return [...arr].sort((a, b) => {
			const av = (a as unknown as Record<string, unknown>)[key] as number ?? -Infinity;
			const bv = (b as unknown as Record<string, unknown>)[key] as number ?? -Infinity;
			return dir * (av - bv);
		});
	}
	const sortedGk = $derived(reSortGk(goalkeepers, gkSort, gkDir));

	function sh(sort: string, key: string, dir: 1|-1, label: string): string {
		return `${label}${sort === key ? (dir === -1 ? ' ↓' : ' ↑') : ''}`;
	}

	const cmpIds = $derived(getComparisonIds());
	const cmpFull = $derived(cmpIds.length >= MAX_COMPARISON);

	// ── Browse section ────────────────────────────────────────────────────────
	let filterTeam = $state('');
	let filterPos = $state('');
	let searchQuery = $state('');

	const teams = $derived(
		[...new Map(players.map((p) => [p.team.id, p.team])).values()].sort((a, b) =>
			a.name.localeCompare(b.name)
		)
	);

	const filtered = $derived(
		enriched
			.filter((p) => {
				if (filterTeam && p.team.id !== Number(filterTeam)) return false;
				if (filterPos && p.position !== filterPos) return false;
				if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
				return true;
			})
			.sort((a, b) => {
				const pa = POSITION_ORDER[a.position ?? ''] ?? 9;
				const pb = POSITION_ORDER[b.position ?? ''] ?? 9;
				if (pa !== pb) return pa - pb;
				return (a.jersey_number ?? 99) - (b.jersey_number ?? 99);
			})
	);

	const grouped = $derived(
		filtered.reduce<Record<string, typeof filtered>>((acc, p) => {
			const key = p.team.name;
			(acc[key] ??= []).push(p);
			return acc;
		}, {})
	);

	const groupKeys = $derived(Object.keys(grouped).sort());

	const f = (v: number | null | undefined, suffix = '') => v != null ? `${v}${suffix}` : '—';
	const fkm = (v: number | null | undefined) => v != null ? (v / 1000).toFixed(1) : '—';
</script>

<svelte:head>
	<title>Players — EFI Data Engine</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label={$t.players.label} />
		<h1 class="page-title">{$t.players.rankingTitle}</h1>
		<p class="page-sub">{players.length} {$t.players.rankingSubtitle}</p>
		<div class="stage-pill-group" role="group" aria-label={$t.stage.ariaLabel}>
			<a href="?" class="stage-pill" class:stage-pill--active={!data.stage} aria-current={!data.stage ? 'true' : undefined}>{$t.stage.all}</a>
			<a href="?stage=group" class="stage-pill" class:stage-pill--active={data.stage === 'group'} aria-current={data.stage === 'group' ? 'true' : undefined}>{$t.stage.group}</a>
			<a href="?stage=knockout" class="stage-pill" class:stage-pill--active={data.stage === 'knockout'} aria-current={data.stage === 'knockout' ? 'true' : undefined}>{$t.stage.knockout}</a>
		</div>
	</header>

	<!-- ── RANKINGS ──────────────────────────────────────────────────────── -->
	<section class="rankings-section">
		<div class="tab-nav" role="tablist">
			{#each RANKING_TABS as tab}
				<button
					class="tab-btn"
					class:tab-btn--active={activeTab === tab.key}
					role="tab"
					aria-selected={activeTab === tab.key}
					onclick={() => activeTab = tab.key}
				>{tab.label}</button>
			{/each}
		</div>

		<div class="ranking-table-wrap">
			{#if activeTab === 'scorers'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title="Select for comparison"></th>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('goals')}>{sh(scorersSort,'goals',scorersDir,$t.players.colGoals)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('goals_per_game')}>{sh(scorersSort,'goals_per_game',scorersDir,$t.players.colGoalsPerGame)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('attempts_at_goal')}>{sh(scorersSort,'attempts_at_goal',scorersDir,$t.players.colShots)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('goals_per_shot')}>{sh(scorersSort,'goals_per_shot',scorersDir,$t.players.colGoalsPerShot)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('take_ons')}><TermTooltip term="Take-ons" definition="Attempts to dribble past an opponent while retaining possession.">{sh(scorersSort,'take_ons',scorersDir,$t.players.colTakeOns)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortScorers('appearances')}>{sh(scorersSort,'appearances',scorersDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedScorers.slice(0, 20) as p, i}
							<tr class:cmp-selected={isSelected(p.id)}>
								<td class="cmp-col">
									<button class="cmp-check" class:cmp-check--on={isSelected(p.id)}
										disabled={!isSelected(p.id) && cmpFull}
										onclick={() => toggleComparison(p.id, 'players')}
										aria-label="{isSelected(p.id) ? 'Remove' : 'Add'} {p.name} from comparison"
									>
									{#if isSelected(p.id)}<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{:else}+{/if}
								</button>
								</td>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num goals-num">{p.stats?.goals ?? 0}</td>
								<td class="num">{p.stats?.goals_per_game != null ? p.stats.goals_per_game : '—'}</td>
								<td class="num">{f(p.stats?.attempts_at_goal)}</td>
								<td class="num">{p.stats?.goals_per_shot != null ? p.stats.goals_per_shot.toFixed(2) : '—'}</td>
								<td class="num">{f(p.stats?.take_ons)}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'defenders'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title="Select for comparison"></th>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('possession_regains')}>{sh(defendersSort,'possession_regains',defendersDir,$t.players.colBallRecoveries)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('tackles_won')}><TermTooltip term="Tackles Won" definition="Successfully dispossessing an opponent by winning the ball cleanly.">{sh(defendersSort,'tackles_won',defendersDir,$t.players.colTklWon)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('interceptions')}><TermTooltip term="Interceptions" definition="Intercepting a pass intended for an opponent, cutting off the attacking play.">{sh(defendersSort,'interceptions',defendersDir,$t.players.colInterceptions)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('clearances')}>{sh(defendersSort,'clearances',defendersDir,$t.players.colClearances)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('blocks')}>{sh(defendersSort,'blocks',defendersDir,$t.players.colBlocks)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDefenders('appearances')}>{sh(defendersSort,'appearances',defendersDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedDefenders.slice(0, 20) as p, i}
							<tr class:cmp-selected={isSelected(p.id)}>
								<td class="cmp-col">
									<button class="cmp-check" class:cmp-check--on={isSelected(p.id)}
										disabled={!isSelected(p.id) && cmpFull}
										onclick={() => toggleComparison(p.id, 'players')}
										aria-label="{isSelected(p.id) ? 'Remove' : 'Add'} {p.name} from comparison"
									>
									{#if isSelected(p.id)}<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{:else}+{/if}
								</button>
								</td>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{f(p.stats?.possession_regains)}</td>
								<td class="num">{f(p.stats?.tackles_won)}</td>
								<td class="num">{f(p.stats?.interceptions)}</td>
								<td class="num">{f(p.stats?.clearances)}</td>
								<td class="num">{f(p.stats?.blocks)}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'midfielders'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title="Select for comparison"></th>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('pass_completion_pct')}>{sh(midfieldersSort,'pass_completion_pct',midfieldersDir,$t.players.colPassQuote)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('passes_attempted')}><TermTooltip term="Passes Attempted" definition="Total passes attempted, including incomplete passes.">{sh(midfieldersSort,'passes_attempted',midfieldersDir,$t.players.colPassesAtt)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('ball_progressions')}><TermTooltip term="Ball Progressions" definition="Carrying or driving the ball forward into attacking areas.">{sh(midfieldersSort,'ball_progressions',midfieldersDir,$t.players.colBallProgs)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('take_ons')}><TermTooltip term="Take-ons" definition="Attempts to dribble past an opponent while retaining possession.">{sh(midfieldersSort,'take_ons',midfieldersDir,$t.players.colTakeOns)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('pressing_direct')}>{sh(midfieldersSort,'pressing_direct',midfieldersDir,$t.players.colPressing)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortMids('appearances')}>{sh(midfieldersSort,'appearances',midfieldersDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedMidfielders.slice(0, 20) as p, i}
							<tr class:cmp-selected={isSelected(p.id)}>
								<td class="cmp-col">
									<button class="cmp-check" class:cmp-check--on={isSelected(p.id)}
										disabled={!isSelected(p.id) && cmpFull}
										onclick={() => toggleComparison(p.id, 'players')}
										aria-label="{isSelected(p.id) ? 'Remove' : 'Add'} {p.name} from comparison"
									>
									{#if isSelected(p.id)}<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{:else}+{/if}
								</button>
								</td>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{p.stats?.pass_completion_pct != null ? `${p.stats.pass_completion_pct}%` : '—'}</td>
								<td class="num">{f(p.stats?.passes_attempted)}</td>
								<td class="num">{f(p.stats?.ball_progressions)}</td>
								<td class="num">{f(p.stats?.take_ons)}</td>
								<td class="num">{f(p.stats?.pressing_direct)}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'forwards'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title="Select for comparison"></th>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('goals_per_shot')}>{sh(forwardsSort,'goals_per_shot',forwardsDir,$t.players.colGoalsPerShot)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('goals')}>{sh(forwardsSort,'goals',forwardsDir,$t.players.colGoals)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('attempts_at_goal')}>{sh(forwardsSort,'attempts_at_goal',forwardsDir,$t.players.colShots)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('take_ons')}><TermTooltip term="Take-ons" definition="Attempts to dribble past an opponent while retaining possession.">{sh(forwardsSort,'take_ons',forwardsDir,$t.players.colTakeOns)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('total_offers')}><TermTooltip term="Offers" definition="Off-ball offering runs — movement toward the ball to create passing options for teammates.">{sh(forwardsSort,'total_offers',forwardsDir,$t.players.colOffers)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortForwards('appearances')}>{sh(forwardsSort,'appearances',forwardsDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedForwards.slice(0, 20) as p, i}
							<tr class:cmp-selected={isSelected(p.id)}>
								<td class="cmp-col">
									<button class="cmp-check" class:cmp-check--on={isSelected(p.id)}
										disabled={!isSelected(p.id) && cmpFull}
										onclick={() => toggleComparison(p.id, 'players')}
										aria-label="{isSelected(p.id) ? 'Remove' : 'Add'} {p.name} from comparison"
									>
									{#if isSelected(p.id)}<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{:else}+{/if}
								</button>
								</td>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{p.stats?.goals_per_shot != null ? p.stats.goals_per_shot.toFixed(2) : '—'}</td>
								<td class="num goals-num">{p.stats?.goals ?? 0}</td>
								<td class="num">{f(p.stats?.attempts_at_goal)}</td>
								<td class="num">{f(p.stats?.take_ons)}</td>
								<td class="num">{f(p.stats?.total_offers)}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'physical'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title="Select for comparison"></th>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('km_per_game')}>{sh(physicalSort,'km_per_game',physicalDir,$t.players.colKmPerGame)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('sprints_per_game')}>{sh(physicalSort,'sprints_per_game',physicalDir,$t.players.colSprintsPerGame)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('total_distance_m')}>{sh(physicalSort,'total_distance_m',physicalDir,$t.players.colDistance)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('sprints')}>{sh(physicalSort,'sprints',physicalDir,$t.players.colSprints)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('high_speed_runs')}><TermTooltip term="HS Runs" definition="High-speed runs — sprints above the high-speed threshold (≈25 km/h).">{sh(physicalSort,'high_speed_runs',physicalDir,$t.players.colHsRuns)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('top_speed_kmh')}>{sh(physicalSort,'top_speed_kmh',physicalDir,$t.players.colTopSpeed)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortPhysical('appearances')}>{sh(physicalSort,'appearances',physicalDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedPhysical.slice(0, 20) as p, i}
							<tr class:cmp-selected={isSelected(p.id)}>
								<td class="cmp-col">
									<button class="cmp-check" class:cmp-check--on={isSelected(p.id)}
										disabled={!isSelected(p.id) && cmpFull}
										onclick={() => toggleComparison(p.id, 'players')}
										aria-label="{isSelected(p.id) ? 'Remove' : 'Add'} {p.name} from comparison"
									>
									{#if isSelected(p.id)}<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>{:else}+{/if}
								</button>
								</td>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{p.stats?.km_per_game != null ? `${p.stats.km_per_game} km` : '—'}</td>
								<td class="num">{p.stats?.sprints_per_game != null ? p.stats.sprints_per_game : '—'}</td>
								<td class="num">{fkm(p.stats?.total_distance_m)}</td>
								<td class="num">{f(p.stats?.sprints)}</td>
								<td class="num">{f(p.stats?.high_speed_runs)}</td>
								<td class="num">{p.stats?.top_speed_kmh != null ? `${p.stats.top_speed_kmh} km/h` : '—'}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'goalkeepers'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="rank-col">#</th>
							<th>{$t.players.posGK}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('matches')}>{sh(gkSort,'matches',gkDir,$t.players.colApps)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('total_attempts_faced')}>{sh(gkSort,'total_attempts_faced',gkDir,$t.players.colGkAttempts)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('avg_save_pct')}>{sh(gkSort,'avg_save_pct',gkDir,$t.players.colGkSavePct)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('total_goal_interventions')}><TermTooltip term="Goal Interventions" definition="Goalkeeper actions preventing a goal: saves, punch clearances, and claims.">{sh(gkSort,'total_goal_interventions',gkDir,$t.players.colGoalInt)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('total_aerial_interventions')}><TermTooltip term="Aerial Interventions" definition="Winning aerial duels to claim crosses or clear dangerous balls.">{sh(gkSort,'total_aerial_interventions',gkDir,$t.players.colGkAerialInt)}</TermTooltip></th>
							<th class="num sortable" use:sortableHeader onclick={() => sortGk('total_crosses_faced')}>{sh(gkSort,'total_crosses_faced',gkDir,$t.players.colGkCrossesFaced)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedGk.slice(0, 20) as gk, i}
							<tr>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									{#if gk.player_id}
										<a href="/players/{gk.player_id}" class="player-link">
											<span class="player-link__pos" style="color: var(--c-lime-ink);">GK</span>
											{gk.gk_name}
										</a>
									{:else}
										<span class="player-link">
											<span class="player-link__pos" style="color: var(--c-lime-ink);">GK</span>
											{gk.gk_name}
										</span>
									{/if}
								</td>
								<td>
									<a href="/teams/{gk.team.id}" class="team-link">
										<span class="fi fi-{flagCode(gk.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{gk.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{gk.matches}</td>
								<td class="num">{gk.total_attempts_faced ?? '—'}</td>
								<td class="num">{gk.avg_save_pct != null ? `${gk.avg_save_pct}%` : '—'}</td>
								<td class="num">{gk.total_goal_interventions ?? '—'}</td>
								<td class="num">{gk.total_aerial_interventions ?? '—'}</td>
								<td class="num">{gk.total_crosses_faced ?? '—'}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else if activeTab === 'discipline'}
				<table class="rank-table">
					<thead>
						<tr>
							<th class="rank-col">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDiscipline('discipline_total')}>{sh(disciplineSort,'discipline_total',disciplineDir,$t.players.colCards)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDiscipline('yellow_cards')}>{sh(disciplineSort,'yellow_cards',disciplineDir,$t.players.colYellow)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDiscipline('red_cards')}>{sh(disciplineSort,'red_cards',disciplineDir,$t.players.colRed)}</th>
							<th class="num sortable" use:sortableHeader onclick={() => sortDiscipline('appearances')}>{sh(disciplineSort,'appearances',disciplineDir,$t.players.colApps)}</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedDiscipline.slice(0, 20) as p, i}
							<tr>
								<td class="rank-col rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.id}" class="player-link">
										<span class="player-link__pos" style="color: {posColor[p.position ?? ''] ?? 'var(--muted)'};">{posLabel[p.position ?? ''] ?? '—'}</span>
										{p.name}
									</a>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="team-link">
										<span class="fi fi-{flagCode(p.team.short_code)}" style="width:18px;height:12px;border-radius:2px;" aria-hidden="true"></span>
										{p.team.short_code}
									</a>
								</td>
								<td class="num highlight-col">{p.discipline_total}</td>
								<td class="num" style="color: var(--c-yellow-ink);">{p.stats?.yellow_cards ?? 0}</td>
								<td class="num" style="color: var(--c-red);">{p.stats?.red_cards ?? 0}</td>
								<td class="num muted">{p.stats?.appearances ?? 0}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	</section>

	<!-- ── BROWSE ALL PLAYERS ─────────────────────────────────────────────── -->
	<section class="browse-section">
		<div class="section-divider"></div>
		<div class="browse-body">
			<SectionLabel label={$t.players.sectionBrowse} />

			<div class="filters">
				<input
					class="filter-input"
					type="search"
					placeholder={$t.players.searchPlaceholder}
					bind:value={searchQuery}
					aria-label="Search players"
				/>
				<select class="filter-select" bind:value={filterTeam} aria-label="Filter by team">
					<option value="">{$t.players.allTeams}</option>
					{#each teams as team (team.id)}
						<option value={team.id}>{team.name}</option>
					{/each}
				</select>
				<select class="filter-select" bind:value={filterPos} aria-label="Filter by position">
					<option value="">{$t.players.allPositions}</option>
					<option value="GK">{$t.players.goalkeepers}</option>
					<option value="DF">{$t.players.defenders}</option>
					<option value="MF">{$t.players.midfielders}</option>
					<option value="FW">{$t.players.forwards}</option>
				</select>
				{#if filterTeam || filterPos || searchQuery}
					<button
						class="filter-clear"
						onclick={() => { filterTeam = ''; filterPos = ''; searchQuery = ''; }}
					>{$t.players.clearFilters}</button>
				{/if}
				{#if filterTeam || filterPos || searchQuery}
					<span class="filter-count">{filtered.length} {$t.players.players}</span>
				{/if}
			</div>

			{#if !filterTeam && !filterPos && !searchQuery}
				<div class="browse-prompt">
					<p class="browse-prompt__text">{$t.players.browsePlaceholder}</p>
				</div>
			{:else if filtered.length === 0}
				<div class="empty">
					<p class="empty__text">{$t.players.browseNoResults}</p>
				</div>
			{:else}
				{#each groupKeys as teamName}
					{@const teamPlayers = grouped[teamName]}
					{@const team = teamPlayers[0].team}
					<section class="team-section">
						<div class="team-header">
							{#if flagCode(team.short_code)}
								<span class="fi fi-{flagCode(team.short_code)} team-flag" aria-hidden="true"></span>
							{/if}
							<span class="team-badge" style="background: {teamColorVar(team.color)}; color: {badgeTextColor(team.color)};">{team.short_code}</span>
							<a href="/teams/{team.id}" class="team-name-link">{teamName}</a>
							<span class="team-count">{teamPlayers.length} players</span>
						</div>
						<div class="player-grid">
							{#each teamPlayers as p (p.id)}
								<a href="/players/{p.id}" class="player-card">
									<span class="player-number">#{p.jersey_number ?? '—'}</span>
									<div class="player-info">
										<span class="player-name">{p.name}</span>
										<span class="player-pos" data-pos={p.position ?? ''}>{posLabel[p.position ?? ''] ?? p.position ?? '—'}</span>
									</div>
									{#if p.stats}
										<div class="player-stats">
											{#if p.stats.goals > 0}
												<span class="pstat pstat--goal">⚽ {p.stats.goals}</span>
											{/if}
											{#if p.stats.yellow_cards > 0}
												<span class="pstat pstat--yellow">🟨 {p.stats.yellow_cards}</span>
											{/if}
											{#if p.stats.red_cards > 0}
												<span class="pstat pstat--red">🟥 {p.stats.red_cards}</span>
											{/if}
											{#if p.stats.minutes_played > 0}
											<span class="pstat pstat--apps">{p.stats.appearances}g</span>
										{/if}
										</div>
									{/if}
								</a>
							{/each}
						</div>
					</section>
				{/each}
			{/if}
		</div>
	</section>
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
	}

	/* ── Page header ─────────────────────────────────────────────────── */
	.page-header {
		padding: 40px var(--sp-8) var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}
	.page-title {
		font-size: var(--fs-hero);
		font-weight: 800;
		line-height: 1.05;
		color: var(--ink);
	}
	.page-sub {
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
	}

	/* ── Stage filter ────────────────────────────────────────────────── */
	.stage-pill-group {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
		width: fit-content;
		flex-wrap: wrap;
	}
	.stage-pill {
		padding: 4px var(--sp-4);
		border: none;
		border-radius: var(--r-pill);
		background: transparent;
		font-size: var(--fs-meta);
		font-weight: 600;
		font-family: inherit;
		color: var(--muted);
		text-decoration: none;
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}
	.stage-pill:hover { background: color-mix(in srgb, var(--ink) 10%, transparent); color: var(--ink); }
	.stage-pill--active {
		background: var(--accent);
		color: var(--accent-fg);
	}

	/* ── Rankings section ────────────────────────────────────────────── */
	.rankings-section {
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}

	/* ── Tab nav ─────────────────────────────────────────────────────── */
	.tab-nav {
		display: flex;
		gap: 0;
		overflow-x: auto;
		scrollbar-width: none;
		border-bottom: 1px solid var(--border);
		padding: 0 var(--sp-8);
	}
	.tab-nav::-webkit-scrollbar { display: none; }
	.tab-btn {
		padding: var(--sp-3) var(--sp-5);
		background: none;
		border: none;
		border-bottom: 3px solid transparent;
		font-size: var(--fs-ui);
		font-weight: 600;
		font-family: inherit;
		color: var(--muted);
		cursor: pointer;
		white-space: nowrap;
		margin-bottom: -1px;
		transition: color 0.15s, border-color 0.15s;
	}
	.tab-btn:hover { color: var(--ink); }
	.tab-btn--active {
		color: var(--accent);
		border-bottom-color: var(--accent);
	}

	/* ── Ranking table ───────────────────────────────────────────────── */
	.ranking-table-wrap {
		overflow-x: auto;
		padding: 0 var(--sp-8);
	}
	.rank-table {
		width: 100%;
		min-width: 600px;
		border-collapse: collapse;
		font-size: var(--fs-ui);
	}
	.rank-table thead th {
		text-align: left;
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		padding: var(--sp-2) var(--sp-3);
		border-bottom: 2px solid var(--border);
	}
	.rank-table thead th.num { text-align: right; }
	.rank-table thead th.sortable {
		cursor: pointer;
		user-select: none;
		white-space: nowrap;
	}
	.rank-table thead th.sortable:hover { color: var(--accent); }
	.rank-table tbody tr { border-bottom: 1px solid var(--border-soft); }
	.rank-table tbody tr:last-child { border-bottom: none; }
	.rank-table tbody tr:hover { background: var(--border-soft); }
	.rank-table td {
		padding: var(--sp-2) var(--sp-3);
		color: var(--ink);
		vertical-align: middle;
	}
	.rank-col {
		width: 40px;
	}
	.cmp-col { width: 32px; padding-left: var(--sp-2) !important; padding-right: 0 !important; }
	.cmp-check {
		width: 22px; height: 22px;
		border: 2px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		font-size: 13px; font-weight: 800;
		cursor: pointer;
		display: inline-flex; align-items: center; justify-content: center;
		padding: 0;
		transition: border-color 0.15s, background 0.15s, color 0.15s;
		font-family: inherit; line-height: 1;
	}
	.cmp-check:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
	.cmp-check--on { border-color: var(--accent); background: var(--accent); color: var(--accent-fg); }
	.cmp-check:disabled { opacity: 0.35; cursor: not-allowed; }
	.cmp-selected { background: color-mix(in srgb, var(--accent) 5%, transparent) !important; }
	.rank-num {
		font-size: var(--fs-meta);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
	}
	.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
		font-weight: 500;
	}
	.highlight-col {
		font-weight: 800;
		color: var(--ink);
	}
	.goals-num {
		font-weight: 900;
		color: var(--accent);
	}
	.muted { color: var(--muted); }

	/* ── Player link ─────────────────────────────────────────────────── */
	.player-link {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
	}
	.player-link:hover { color: var(--accent); text-decoration: underline; }
	.player-link__pos {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		flex-shrink: 0;
		min-width: 24px;
	}

	/* ── Team link ───────────────────────────────────────────────────── */
	.team-link {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		font-weight: 700;
		color: var(--muted);
		text-decoration: none;
		font-size: var(--fs-ui);
	}
	.team-link:hover { color: var(--ink); }

	/* ── Browse section ──────────────────────────────────────────────── */
	.section-divider { height: 1px; background: var(--border); }
	.browse-body {
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-8);
	}

	/* ── Filters ─────────────────────────────────────────────────────── */
	.filters {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		flex-wrap: wrap;
	}
	.filter-input,
	.filter-select {
		height: 38px;
		padding: 0 var(--sp-3);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: var(--surface);
		color: var(--ink);
		font-size: var(--fs-ui);
		font-family: inherit;
	}
	.filter-input { min-width: 220px; }
	.filter-select { min-width: 160px; }
	.filter-clear {
		height: 38px;
		padding: 0 var(--sp-4);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		font-size: var(--fs-ui);
		font-family: inherit;
		cursor: pointer;
	}
	.filter-clear:hover { color: var(--ink); border-color: var(--ink); }
	.filter-count {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		margin-left: auto;
	}

	/* ── Browse prompt (no filter active) ───────────────────────────── */
	.browse-prompt {
		padding: var(--sp-10) 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.browse-prompt__text {
		font-size: var(--fs-h2);
		font-weight: 300;
		color: var(--muted);
		text-align: center;
	}

	/* ── Empty ───────────────────────────────────────────────────────── */
	.empty { padding: var(--sp-10) 0; }
	.empty__text { font-size: var(--fs-h2); font-weight: 300; color: var(--muted); }

	/* ── Team section ────────────────────────────────────────────────── */
	.team-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.team-header {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
	}
	.team-flag {
		width: 36px;
		height: 24px;
		border-radius: 3px;
		flex-shrink: 0;
		box-shadow: 0 1px 3px rgba(0,0,0,0.15);
	}
	.team-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 3px 8px;
		border-radius: var(--r-sm);
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}
	.team-name-link {
		font-size: var(--fs-h2);
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
	}
	.team-name-link:hover { color: var(--accent); }
	.team-count {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	/* ── Player grid ─────────────────────────────────────────────────── */
	.player-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: var(--sp-3);
	}

	/* ── Player card ─────────────────────────────────────────────────── */
	.player-card {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		padding: 10px 14px;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		flex-wrap: wrap;
		text-decoration: none;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.player-card:hover {
		border-color: var(--accent);
		box-shadow: 0 2px 8px rgba(0,0,0,0.08);
	}
	.player-number {
		font-size: var(--fs-label);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		min-width: 28px;
		flex-shrink: 0;
	}
	.player-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
		min-width: 0;
	}
	.player-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.player-pos {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}
	[data-pos='GK'] { color: var(--c-lime-ink); }
	[data-pos='DF'] { color: var(--c-teal-ink); }
	[data-pos='MF'] { color: var(--c-blue-ink); }
	[data-pos='FW'] { color: var(--c-red-ink); }

	/* ── Player stats chips ──────────────────────────────────────────── */
	.player-stats {
		display: flex;
		gap: var(--sp-2);
		align-items: center;
		margin-inline-start: auto;
		flex-shrink: 0;
	}
	.pstat {
		font-size: 11px;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		padding: 1px 5px;
		border-radius: 3px;
		background: color-mix(in srgb, var(--muted) 10%, transparent);
		color: var(--muted);
	}
	.pstat--goal { background: color-mix(in srgb, var(--accent) 15%, transparent); color: var(--accent); }
	.pstat--yellow { background: color-mix(in srgb, var(--c-yellow) 15%, transparent); color: var(--c-yellow-ink); }
	.pstat--red { background: color-mix(in srgb, var(--c-red) 15%, transparent); color: var(--c-red); }

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.page-header, .browse-body {
			padding-left: var(--sp-4);
			padding-right: var(--sp-4);
		}
		.tab-nav { padding: 0 var(--sp-4); }
		.ranking-table-wrap { padding: 0 var(--sp-4); }
		.page-title { font-size: 2.25rem; }
		.filters { flex-direction: column; align-items: stretch; }
		.filter-input, .filter-select { width: 100%; }
		.filter-count { margin-left: 0; }
		.player-grid { grid-template-columns: repeat(2, 1fr); }
	}
	@media (max-width: 400px) {
		.player-grid { grid-template-columns: 1fr; }
	}
</style>
