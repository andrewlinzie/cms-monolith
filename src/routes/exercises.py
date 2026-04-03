from fastapi import APIRouter
from src.models.schemas import Exercise
from src.services.exercise_service import list_exercises, create_exercise

router = APIRouter(prefix="/admin/exercises", tags=["exercises"])


@router.get("", response_model=list[Exercise])
def get_exercises():
    return list_exercises()


@router.post("", response_model=Exercise)
def post_exercise(exercise: Exercise):
    return create_exercise(exercise)