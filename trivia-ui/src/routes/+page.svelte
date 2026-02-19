<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import type { Category } from '$lib/types';

	let categories: Category[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			categories = await api<Category[]>('/categories');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
		} finally {
			loading = false;
		}
	});
</script>

<div class="container py-4">
	<h1 class="mb-4">Trivia Categories</h1>

	{#if loading}
		<div class="alert alert-info">Loading...</div>
	{/if}

	{#if error}
		<div class="alert alert-danger">{error}</div>
	{/if}

	{#if !loading && categories.length === 0}
		<div class="alert alert-warning">No categories available.</div>
	{/if}

	<div class="row">
		{#each categories as c}
			<div class="col-md-4 mb-3">
				<div class="card shadow-sm h-100">
					<div class="card-body d-flex flex-column">
						<h5 class="card-title">{c.name}</h5>

						<button class="btn btn-primary mt-auto" on:click={() => goto(`/quiz?category=${c.id}`)}>
							Start Quiz
						</button>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>
