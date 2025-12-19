'use client';

import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, Trash2, Edit2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { VoteButtons } from './vote-buttons';
import { useDeleteAnswerMutation, useAcceptAnswerMutation } from '@/lib/api/questionsApi';
import { useMeQuery } from '@/lib/api';
import type { AnswerDetail } from '@/lib/api/questionsApi';
import { useState } from 'react';

interface AnswerCardProps {
  answer: AnswerDetail;
  questionAuthorId: number;
  onUpdate?: () => void;
}

export function AnswerCard({ answer, questionAuthorId, onUpdate }: AnswerCardProps) {
  const { data: currentUser } = useMeQuery();
  const [deleteAnswer, { isLoading: isDeleting }] = useDeleteAnswerMutation();
  const [acceptAnswer, { isLoading: isAccepting }] = useAcceptAnswerMutation();

  const isAuthor = currentUser?.id === answer.author_id;
  const isQuestionAuthor = currentUser?.id === questionAuthorId;

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this answer?')) return;
    try {
      await deleteAnswer(answer.id).unwrap();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to delete answer:', error);
    }
  };

  const handleAccept = async () => {
    try {
      await acceptAnswer(answer.id).unwrap();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to accept answer:', error);
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${answer.is_accepted ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800' : ''}`}>
      <div className="flex items-start gap-4">
        <VoteButtons
          votableType="answer"
          votableId={answer.id}
          score={answer.vote_score}
          userVote={answer.user_vote}
          disabled={false}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{answer.author_email}</span>
              {answer.is_accepted && (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              )}
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(answer.created_at), { addSuffix: true })}
              </span>
            </div>
            <div className="flex items-center gap-1">
              {isQuestionAuthor && !answer.is_accepted && (
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={handleAccept}
                  disabled={isAccepting}
                  title="Accept answer"
                >
                  <CheckCircle2 className="h-4 w-4" />
                </Button>
              )}
              {isAuthor && (
                <>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    title="Delete answer"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </>
              )}
            </div>
          </div>
          <p className="text-sm whitespace-pre-wrap">{answer.content}</p>
        </div>
      </div>
    </div>
  );
}