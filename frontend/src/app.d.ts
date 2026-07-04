// See https://kit.svelte.dev/docs/types#app
declare global {
	namespace App {
		interface Locals {}
		interface PageData {}
		interface Error {
			message: string;
		}
		interface Platform {}
	}
}

export {};
