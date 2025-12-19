'use client';

import { ChevronUp, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCreateVoteMutation } from '@/lib/api/questionsApi';
import { useState } from 'react';

interface VoteButtonsProps {
  votableType: 'question' | 'answer';
  votableId: number;
  score: number;
  userVote?: 'upvote' | 'downvote' | null;
  disabled?: boolean;
}

export function VoteButtons({
  votableType,
  votableId,
  score,
  userVote,
  disabled = false,
}: VoteButtonsProps) {
  const [createVote, { isLoading }] = useCreateVoteMutation();
  const [localScore, setLocalScore] = useState(score);
  const [localVote, setLocalVote] = useState(userVote);

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    if (disabled || isLoading) return;

    const previousVote = localVote;
    const previousScore = localScore;

    // Optimistic update
    let newScore = previousScore;
    if (previousVote === voteType) {
      // Toggle off
      setLocalVote(null);
      setLocalScore(previousScore + (voteType === 'upvote' ? -1 : 1));
      newScore = previousScore + (voteType === 'upvote' ? -1 : 1);
    } else if (previousVote) {
      // Switch vote
      setLocalVote(voteType);
      setLocalScore(previousScore + (voteType === 'upvote' ? 2 : -2));
      newScore = previousScore + (voteType === 'upvote' ? 2 : -2);
    } else {
      // New vote
      setLocalVote(voteType);
      setLocalScore(previousScore + (voteType === 'upvote' ? 1 : -1));
      newScore = previousScore + (voteType === 'upvote' ? 1 : -1);
    }

    try {
      await createVote({
        votable_type: votableType,
        votable_id: votableId,
        vote_type: voteType,
      }).unwrap();
    } catch (error) {
      // Revert on error
      setLocalVote(previousVote);
      setLocalScore(previousScore);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          handleVote('upvote');
        }}
        disabled={disabled || isLoading}
        className={localVote === 'upvote' ? 'text-primary' : ''}
      >
        <ChevronUp className="h-5 w-5" />
      </Button>
      <span className="text-sm font-medium min-w-[2ch] text-center">
        {localScore}
      </span>
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          handleVote('downvote');
        }}
        disabled={disabled || isLoading}
        className={localVote === 'downvote' ? 'text-primary' : ''}
      >
        <ChevronDown className="h-5 w-5" />
      </Button>
    </div>
  );
}