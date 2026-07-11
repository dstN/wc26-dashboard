import type { Action } from 'svelte/action';

/**
 * Makes a click-only sortable `<th>` keyboard-operable without stripping its
 * native `columnheader` semantics: adds it to the tab order and maps
 * Enter/Space to the element's existing `onclick` sort handler (WCAG 2.1.1).
 *
 * Pair with `aria-sort` on the same `<th>` so assistive tech announces the
 * active sort direction (WCAG 4.1.2).
 */
export const sortableHeader: Action = (node) => {
	node.setAttribute('tabindex', '0');
	node.setAttribute('role', 'columnheader');

	const onKey = (e: KeyboardEvent) => {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			(node as HTMLElement).click();
		}
	};
	node.addEventListener('keydown', onKey);

	return {
		destroy() {
			node.removeEventListener('keydown', onKey);
		}
	};
};
