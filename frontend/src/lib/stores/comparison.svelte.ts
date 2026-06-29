export type ComparisonType = 'teams' | 'players';
export const MAX_COMPARISON = 5;

let _ids = $state<number[]>([]);
let _type = $state<ComparisonType | null>(null);

export function getComparisonIds(): number[] {
	return _ids;
}

export function getComparisonType(): ComparisonType | null {
	return _type;
}

export function isSelected(id: number): boolean {
	return _ids.includes(id);
}

export function toggleComparison(id: number, type: ComparisonType): void {
	if (_type !== null && _type !== type) {
		_ids = [id];
		_type = type;
		return;
	}
	_type = type;
	const idx = _ids.indexOf(id);
	if (idx >= 0) {
		_ids = _ids.filter((x) => x !== id);
		if (_ids.length === 0) _type = null;
	} else if (_ids.length < MAX_COMPARISON) {
		_ids = [..._ids, id];
	}
}

export function clearComparison(): void {
	_ids = [];
	_type = null;
}

export function compareUrl(): string {
	if (_ids.length < 2 || !_type) return '/compare';
	return `/compare?type=${_type}&ids=${_ids.join(',')}`;
}
