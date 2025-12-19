'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useCreateQuestionMutation } from '@/lib/api/questionsApi';
import { useRouter } from 'next/navigation';

interface QuestionFormProps {
  onSuccess?: () => void;
}

export function QuestionForm({ onSuccess }: QuestionFormProps) {
  const router = useRouter();
  const [createQuestion, { isLoading }] = useCreateQuestionMutation();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || isLoading) return;

    try {
      const question = await createQuestion({
        title: title.trim(),
        content: content.trim(),
      }).unwrap();
      setTitle('');
      setContent('');
      if (onSuccess) {
        onSuccess();
      } else {
        router.push(`/questions/${question.id}`);
      }
    } catch (error) {
      console.error('Failed to create question:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Input
          placeholder="What's your question?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          minLength={5}
          maxLength={255}
        />
      </div>
      <div>
        <Textarea
          placeholder="Provide details about your question..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          minLength={10}
          rows={6}
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={isLoading || !title.trim() || !content.trim()}>
          {isLoading ? 'Posting...' : 'Post Question'}
        </Button>
      </div>
    </form>
  );
}