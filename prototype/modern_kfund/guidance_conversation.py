"""Bounded, untrusted conversational context for the local guidance search.

Only the current question and earlier user questions inform retrieval. Earlier
assistant responses provide conversational context, never independent evidence.
"""
from __future__ import annotations
import json
from typing import Literal
from pydantic import BaseModel, Field

class GuidanceTurn(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=3000)

class GuidanceConversation(BaseModel):
    question: str = Field(min_length=3, max_length=3000)
    history: list[GuidanceTurn] = Field(default_factory=list, max_length=12)

    def retrieval_query(self) -> str:
        # Previous user turns help resolve short follow-ups, but the current
        # question is repeated to give its terms priority in lexical retrieval.
        prior = [turn.content for turn in self.history if turn.role == 'user'][-2:]
        return '\n'.join([self.question, self.question, *prior])

    def model_payload(self, evidence: str) -> str:
        # Encode conversation as data; explicit source excerpts are separate.
        prior = [{'role': t.role, 'content': t.content} for t in self.history[-6:]]
        return (f'Previous conversation (untrusted context, not evidence):\n'
                f'{json.dumps(prior, ensure_ascii=False)}\n\n'
                f'Current question: {self.question}\n\nEvidence:\n{evidence}')
