<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import 'bootstrap/dist/css/bootstrap.min.css';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(async () => {
		await import('bootstrap');
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="container py-4">
	{@render children()}
</div>
