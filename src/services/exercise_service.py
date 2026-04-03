from src.data.seed_data import exercises
from src.models.schemas import Exercise


def list_exercises():
    return exercises


def create_exercise(exercise: Exercise):
    exercises.append(exercise.model_dump())
    return exercise