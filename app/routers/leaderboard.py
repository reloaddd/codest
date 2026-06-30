from fastapi import APIRouter
import redis

router=APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"]
)

@router.get("/")
def get_leaderboard():
    redis_client=redis.Redis(host="localhost", port=6379,db=0, decode_responses=True)
    raw_leaderboard = redis_client.zrevrange("global_leaderboard",0,-1,withscores=True)
    formatted_leaderboard=[]
    for rank,(username,score) in enumerate(raw_leaderboard):
        formatted_leaderboard.append({
            "rank":rank+1,
            "username":username,
            "score":int(score)
        })
    return formatted_leaderboard