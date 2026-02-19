<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import type { QuizQuestion, QuizStartResponse, QuizSubmitResponse } from '$lib/types';

	let questions: QuizQuestion[] = [];
	let loading = true;
	let error: string | null = null;

	let currentIndex = 0;
	let selectedAnswers: Record<number, number> = {};

	let result: QuizSubmitResponse | null = null;

	// --- Params ---
	const categoryId = page.url.searchParams.get('category');
	const limit = page.url.searchParams.get('limit') ?? '10';

	// --- Fetch quiz ---
	onMount(async () => {
		try {
			const data = await api<QuizStartResponse>(
				`/quiz/start?category_id=${categoryId}&limit=${limit}`
			);

			questions = data.questions;
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	// --- Select answer ---
	function selectAnswer(questionId: number, answerId: number) {
		selectedAnswers[questionId] = answerId;
	}

	// --- Navigation ---
	function next() {
		if (currentIndex < questions.length - 1) {
			currentIndex++;
		}
	}

	function prev() {
		if (currentIndex > 0) {
			currentIndex--;
		}
	}

	// --- Submit ---
	async function submitQuiz() {
		const payload = {
			answers: Object.values(selectedAnswers).map((id) => ({
				answer_id: id
			}))
		};

		result = await api<QuizSubmitResponse>('/quiz/submit', {
			method: 'POST',
			body: JSON.stringify(payload)
		});
	}
</script>

<div class="container py-4">
	<h1 class="mb-4">Trivia Quiz</h1>

	{#if loading}
		<div class="alert alert-info">Loading quiz...</div>
	{/if}

	{#if error}
		<div class="alert alert-danger">{error}</div>
	{/if}

	{#if !loading && !result && questions.length}
		<!-- Progress -->
		<div class="mb-3">
			Question {currentIndex + 1} of {questions.length}
		</div>

		<!-- Question Card -->
		<div class="card shadow-sm mb-3">
			<div class="card-body">
				<h5 class="card-title">
					{questions[currentIndex].text}
				</h5>

				<div class="list-group mt-3">
					{#each questions[currentIndex].choices as c}
						<button
							class="list-group-item list-group-item-action
                {selectedAnswers[questions[currentIndex].id] === c.id ? 'active' : ''}"
							on:click={() => selectAnswer(questions[currentIndex].id, c.id)}
						>
							{c.text}
						</button>
					{/each}
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<div class="d-flex justify-content-between">
			<button class="btn btn-secondary" on:click={prev} disabled={currentIndex === 0}>
				Previous
			</button>

			{#if currentIndex < questions.length - 1}
				<button class="btn btn-primary" on:click={next}> Next </button>
			{:else}
				<button class="btn btn-success" on:click={submitQuiz}> Submit Quiz </button>
			{/if}
		</div>
	{/if}

	<!-- Results -->
	{#if result}
		<div class="card shadow-sm mt-4">
			<div class="card-body text-center">
				<h2>Quiz Complete 🎉</h2>

				<p class="fs-4">
					Score: {result.score} / {result.total}
				</p>

				<p class="fs-5">
					Percentage: {result.percentage}%
				</p>

				<a href="/" class="btn btn-primary mt-3"> Back to Categories </a>
			</div>
		</div>
	{/if}
</div>
