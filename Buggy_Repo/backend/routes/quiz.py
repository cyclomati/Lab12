from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random
from typing import List

router = APIRouter(tags=["quiz"])

# Pydantic models for request/response validation
class QuestionResponse(BaseModel):
    id: int
    text: str
    options: List[str]

class AnswerRequest(BaseModel):
    id: int
    answer: str
    score: int = 0

class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    score: int
    high_score: int

# Store questions in MongoDB (implementation would be in db.py)
questions = [
    {
        "id": 1,
        "text": "What command lists directory contents?",
        "options": ["ls", "cd", "rm", "pwd"],
        "correct": "ls",
        "points": 10
    },
    {
        "id": 2,
        "text": "Which command searches for text in files?",
        "options": ["find", "grep", "locate", "cat"],
        "correct": "grep",
        "points": 10
    },
    {
        "id": 3,
        "text": "What changes file permissions?",
        "options": ["chmod", "chown", "mv", "cp"],
        "correct": "chmod",
        "points": 15
    },
    {
        "id": 4,
        "text": "Which command displays the current directory?",
        "options": ["dir", "pwd", "path", "where"],
        "correct": "pwd",
        "points": 5
    },
    {
        "id": 5,
        "text": "What removes a file?",
        "options": ["rm", "del", "erase", "unlink"],
        "correct": "rm",
        "points": 5
    }
]

# In a real app, this would be stored in MongoDB
game_state = {"high_score": 0}

@router.get("/question", response_model=QuestionResponse, 
           summary="Get a random quiz question",
           description="Returns a random question from the Linux command quiz")
async def get_question():
    """Get a random quiz question"""
    question = random.choice(questions)
    return {
        "id": question["id"],
        "text": question["text"],
        "options": question["options"]
    }

@router.post("/answer", response_model=AnswerResponse,
            summary="Submit an answer",
            description="Submit an answer to a quiz question and get scoring feedback")
async def submit_answer(answer_data: AnswerRequest):
    """Submit an answer to a quiz question"""
    question = next((q for q in questions if q["id"] == answer_data.id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = answer_data.answer == question["correct"]
    new_score = answer_data.score
    
    if is_correct:
        new_score += question["points"]
        if new_score > game_state["high_score"]:
            game_state["high_score"] = new_score

    return {
        "is_correct": is_correct,
        "correct_answer": question["correct"],
        "score": new_score,
        "high_score": game_state["high_score"]
    }

@router.get("/highscore", 
           summary="Get current high score",
           description="Returns the current highest score achieved in the quiz")
async def get_highscore():
    """Get the current quiz high score"""
    return {"high_score": game_state["high_score"]}
