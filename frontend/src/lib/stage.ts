// matches.group_letter is 'A'-'L' (single char) for the group stage, or one
// of R32/R16/QF/SF/3RD/FIN (2-3 chars) for knockout rounds — mirrors the
// backend convention in stage_filter.py.
export function isKnockoutGroup(groupLetter: string | null | undefined): boolean {
	return !!groupLetter && groupLetter.length > 1;
}

export type StageFilter = 'all' | 'group' | 'knockout';
