from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from processor import fetch_playlist_videos, process_video

app = FastAPI(title="Linux Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/playlist")
def get_playlist(id: str = Query(..., description="YouTube playlist ID")):
    try:
        videos = fetch_playlist_videos(id)
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ProcessRequest(BaseModel):
    video_ids: List[str]


@app.post("/api/process")
def process_videos(request: ProcessRequest):
    results = []
    for video_id in request.video_ids:
        try:
            note = process_video(video_id)
            results.append(note)
        except Exception as e:
            results.append({
                "video_id": video_id,
                "title": video_id,
                "command": "unknown",
                "all_commands": [],
                "transcript": "",
                "flags": [],
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "error": str(e),
            })
    return {"notes": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
