export type Category = {
  id: number;
  name: string;
};

export interface Answer {
  id: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: number;
  text: string;
  answers: Answer[];
}

export interface QuizChoice {
  id: number;
  text: string;
}

export interface QuizQuestion {
  id: number;
  text: string;
  choices: QuizChoice[];
}

export interface QuizStartResponse {
  questions: QuizQuestion[];
}

export interface QuizSubmitRequest {
  answers: {
    answer_id: number;
  }[];
}

export interface QuizSubmitResponse {
  score: number;
  total: number;
  percentage: number;
}
