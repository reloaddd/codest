from celery import Celery
from app.database import localSession
from app import models, engine
import redis
import json

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@celery_app.task
def submission_task(submission_id):
    db=localSession()
    try:
        submission=db.query(models.Submission).filter(models.Submission.id==submission_id).first()
        test_cases=db.query(models.TestCase).filter(models.TestCase.problem_id==submission.problem_id).all()
        if not test_cases:
            submission.status = "System Error: No test cases found"
        else:
            submission.status = engine.grade_submission(submission.code,submission.language, test_cases)
        db.commit()

        #publish msg to redis channel
        message = json.dumps({
            "submission_id": submission_id,
            "status": submission.status
        })
        redis_client.publish("submission_updates", message)
        if submission.status == "Accepted":
            user = db.query(models.User).filter(models.User.id == submission.user_id).first()
            if user:
                # Add 1 to the user's score in the 'global_leaderboard' sorted set
                redis_client.zincrby("global_leaderboard", 1, user.username)

            problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).with_for_update().first()
            if problem:
                problem.solved_count += 1
                db.commit()
        return submission.status
    finally:
        db.close()