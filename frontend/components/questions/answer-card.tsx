'use client';

import { formatDistanceToNow, parseISO } from 'date-fns';
import { CheckCircle2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { VoteButtons } from './vote-buttons';
import { useDeleteAnswerMutation, useAcceptAnswerMutation } from '@/lib/api/questionsApi';
import { useMeQuery } from '@/lib/api';
import type { AnswerDetail } from '@/lib/api/questionsApi';
import Image from 'next/image';

interface AnswerCardProps {
  answer: AnswerDetail;
  questionAuthorId: number;
  onUpdate?: () => void;
}

// Generate avatar URL from email (using a service like Gravatar or a simple hash)
function getAvatarUrl(email: string): string {
  // Option 1: Use Gravatar
  // const hash = email.toLowerCase().trim();
  // return `https://www.gravatar.com/avatar/${hash}?d=identicon&s=40`;
  
  // Option 2: Use a placeholder service
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`;
}

// Get display name from email
function getDisplayName(email: string): string {
  return email.split('@')[0].split('.')[0];
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

  // Parse date correctly - handle both ISO strings and Date objects
  const createdAt = typeof answer.created_at === 'string' 
    ? parseISO(answer.created_at) 
    : new Date(answer.created_at);
  
  const timeAgo = formatDistanceToNow(createdAt, { addSuffix: true });

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
              {/* Avatar */}
              <div className="relative w-8 h-8 rounded-full overflow-hidden bg-muted shrink-0">
                <img
                  src={getAvatarUrl(answer.author_email)}
                  alt={getDisplayName(answer.author_email)}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback to initials if image fails
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const parent = target.parentElement;
                    if (parent && !parent.querySelector('.fallback-initials')) {
                      const initials = document.createElement('div');
                      initials.className = 'fallback-initials w-full h-full flex items-center justify-center text-xs font-medium bg-primary text-primary-foreground';
                      initials.textContent = getDisplayName(answer.author_email).charAt(0).toUpperCase();
                      parent.appendChild(initials);
                    }
                  }}
                />
              </div>
              {/* Author name */}
              <span className="text-sm font-medium">{getDisplayName(answer.author_email)}</span>
              {answer.is_accepted && (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              )}
              <span className="text-xs text-muted-foreground">
                {timeAgo}
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
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={handleDelete}
                  disabled={isDeleting}
                  title="Delete answer"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          <p className="text-sm whitespace-pre-wrap">{answer.content}</p>
        </div>
      </div>
    </div>
  );
}