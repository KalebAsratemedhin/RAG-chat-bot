import { baseApi } from './baseApi';

// Types
export interface Question {
  id: number;
  title: string;
  content: string;
  author_id: number;
  created_at: string;
  updated_at: string;
  is_solved: boolean;
  vote_score: number;
  answer_count: number;
  user_vote?: 'upvote' | 'downvote' | null;
}

export interface QuestionDetail extends Question {
  author_email: string;
  answers: AnswerDetail[];
}

export interface Answer {
  id: number;
  question_id: number;
  content: string;
  author_id: number;
  created_at: string;
  updated_at: string;
  is_accepted: boolean;
  vote_score: number;
  user_vote?: 'upvote' | 'downvote' | null;
}

export interface AnswerDetail extends Answer {
  author_email: string;
}

export interface QuestionCreate {
  title: string;
  content: string;
}

export interface QuestionUpdate {
  title?: string;
  content?: string;
  is_solved?: boolean;
}

export interface AnswerCreate {
  question_id: number;
  content: string;
}

export interface AnswerUpdate {
  content?: string;
}

export interface VoteCreate {
  votable_type: 'question' | 'answer';
  votable_id: number;
  vote_type: 'upvote' | 'downvote';
}

export interface VoteResponse {
  message: string;
  vote: string | null;
  score: number;
}

// Questions API endpoints
export const questionsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Questions
    getQuestions: builder.query<
      Question[],
      { skip?: number; limit?: number; is_solved?: boolean; author_id?: number }
    >({
      query: (params) => ({
        url: '/questions/',
        method: 'GET',
        params,
      }),
      providesTags: ['Question'],
    }),
    getQuestion: builder.query<QuestionDetail, number>({
      query: (id) => ({
        url: `/questions/${id}`,
        method: 'GET',
      }),
      providesTags: (result, error, id) => [{ type: 'Question', id }],
    }),
    createQuestion: builder.mutation<Question, QuestionCreate>({
      query: (body) => ({
        url: '/questions/',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Question'],
    }),
    updateQuestion: builder.mutation<Question, { id: number; data: QuestionUpdate }>({
      query: ({ id, data }) => ({
        url: `/questions/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Question', id }, 'Question'],
    }),
    deleteQuestion: builder.mutation<void, number>({
      query: (id) => ({
        url: `/questions/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Question'],
    }),
    // Answers
    createAnswer: builder.mutation<Answer, AnswerCreate>({
      query: (body) => ({
        url: `/questions/${body.question_id}/answers`,
        method: 'POST',
        body: { content: body.content },
      }),
      invalidatesTags: (result, error, { question_id }) => [
        { type: 'Question', id: question_id },
        'Question',
      ],
    }),
    updateAnswer: builder.mutation<Answer, { id: number; data: AnswerUpdate }>({
      query: ({ id, data }) => ({
        url: `/questions/answers/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Question'],
    }),
    deleteAnswer: builder.mutation<void, number>({
      query: (id) => ({
        url: `/questions/answers/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Question'],
    }),
    acceptAnswer: builder.mutation<Answer, number>({
      query: (id) => ({
        url: `/questions/answers/${id}/accept`,
        method: 'POST',
      }),
      invalidatesTags: ['Question'],
    }),
    // Votes
    createVote: builder.mutation<VoteResponse, VoteCreate>({
      query: (body) => ({
        url: '/questions/votes',
        method: 'POST',
        body,
      }),
      invalidatesTags: (result, error, { votable_id, votable_type }) => [
        { type: 'Question', id: votable_type === 'question' ? votable_id : undefined },
        'Question',
      ],
    }),
  }),
  overrideExisting: false,
});

// Export hooks
export const {
  useGetQuestionsQuery,
  useGetQuestionQuery,
  useCreateQuestionMutation,
  useUpdateQuestionMutation,
  useDeleteQuestionMutation,
  useCreateAnswerMutation,
  useUpdateAnswerMutation,
  useDeleteAnswerMutation,
  useAcceptAnswerMutation,
  useCreateVoteMutation,
} = questionsApi;