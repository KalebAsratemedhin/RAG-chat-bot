'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useCreateAnswerMutation } from '@/lib/api/questionsApi';

interface AnswerFormProps {
  questionId: number;
  onSuccess?: () => void;
}

export function AnswerForm({ questionId, onSuccess }: AnswerFormProps) {
  const [createAnswer, { isLoading }] = useCreateAnswerMutation();
  const [content, setContent] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || isLoading) return;

    try {
      await createAnswer({
        question_id: questionId,
        content: content.trim(),
      }).unwrap();
      setContent('');
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to create answer:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        placeholder="Write your answer..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
        minLength={10}
        rows={4}
      />
      <div className="flex justify-end">
        <Button type="submit" disabled={isLoading || !content.trim()}>
          {isLoading ? 'Posting...' : 'Post Answer'}
        </Button>
      </div>
    </form>
  );
}