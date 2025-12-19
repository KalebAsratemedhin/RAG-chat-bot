'use client';

import { useParams } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { VoteButtons } from '@/components/questions/vote-buttons';
import { AnswerCard } from '@/components/questions/answer-card';
import { AnswerForm } from '@/components/questions/answer-form';
import { useGetQuestionQuery } from '@/lib/api/questionsApi';
import { AuthGuard } from '@/components/auth/auth-guard';
import { ChatHeader } from '@/components/chat/chat-header';

function QuestionDetailPage() {
  const params = useParams();
  const questionId = parseInt(params.id as string);
  const { data: question, isLoading, refetch } = useGetQuestionQuery(questionId);

  if (isLoading) {
    return (
      <div className="container max-w-4xl mx-auto py-6 px-4">
        <div className="text-center py-8 text-muted-foreground">Loading question...</div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="container max-w-4xl mx-auto py-6 px-4">
        <div className="text-center py-8 text-muted-foreground">Question not found</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <ChatHeader />
      <div className="container max-w-4xl mx-auto py-6 px-4">
      <Link href="/questions">
        <Button variant="ghost" size="sm" className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Questions
        </Button>
      </Link>

      <div className="border rounded-lg p-6 mb-6">
        <div className="flex items-start gap-4">
          <VoteButtons
            votableType="question"
            votableId={question.id}
            score={question.vote_score}
            userVote={question.user_vote}
            disabled={false}
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-2xl font-bold">{question.title}</h1>
              {question.is_solved && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <span>{question.author_email}</span>
              <span>•</span>
              <span>
                {formatDistanceToNow(new Date(question.created_at), { addSuffix: true })}
              </span>
            </div>
            <p className="text-base whitespace-pre-wrap mb-4">{question.content}</p>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">
          {question.answers.length} {question.answers.length === 1 ? 'Answer' : 'Answers'}
        </h2>
        <div className="space-y-4 mb-6">
          {question.answers.map((answer) => (
            <AnswerCard
              key={answer.id}
              answer={answer}
              questionAuthorId={question.author_id}
              onUpdate={refetch}
            />
          ))}
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Your Answer</h3>
        <AnswerForm questionId={question.id} onSuccess={refetch} />
      </div>
    </div>
    </div>
  );
}

export default function ProtectedQuestionDetailPage() {
  return (
    <AuthGuard>
      <QuestionDetailPage />
    </AuthGuard>
  );
}