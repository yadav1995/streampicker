import uuid
import random
import string
import threading
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider
from app.schemas import TitleResponse
from app.services.catalog_service import format_title_response

class WatchPartyRoom:
    def __init__(self, room_code: str, host_name: str, host_subscriptions: List[str]):
        self.room_code = room_code
        self.host_name = host_name
        self.participants: Dict[str, List[str]] = {host_name: host_subscriptions}  # name -> subscriptions
        self.votes: Dict[str, Dict[str, int]] = {}  # title_id -> {user_name: vote_value (+1 / -1)}
        self.candidate_title_ids: List[str] = []

class RoomManager:
    def __init__(self):
        self._rooms: Dict[str, WatchPartyRoom] = {}
        self._lock = threading.Lock()

    def generate_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def create_room(self, host_name: str, host_subscriptions: List[str], db: Session) -> Dict[str, Any]:
        with self._lock:
            code = self.generate_code()
            room = WatchPartyRoom(code, host_name, host_subscriptions)
            
            # Select 8 candidate titles based on host's subs
            titles = db.query(Title).join(Title.providers).filter(
                TitleProvider.provider_id.in_(host_subscriptions),
                Title.rating_imdb >= 7.0
            ).distinct().limit(8).all()
            
            if not titles:
                titles = db.query(Title).limit(8).all()

            room.candidate_title_ids = [t.id for t in titles]
            self._rooms[code] = room

            return {
                "room_code": code,
                "host_name": host_name,
                "participants_count": 1,
                "candidate_titles_count": len(room.candidate_title_ids)
            }

    def join_room(self, room_code: str, user_name: str, subscriptions: List[str]) -> Optional[Dict[str, Any]]:
        with self._lock:
            room = self._rooms.get(room_code.upper())
            if not room:
                return None
            room.participants[user_name] = subscriptions
            return {
                "room_code": room.room_code,
                "participants": list(room.participants.keys()),
                "total_participants": len(room.participants)
            }

    def cast_vote(self, room_code: str, user_name: str, title_id: str, vote: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            room = self._rooms.get(room_code.upper())
            if not room:
                return None
            if title_id not in room.votes:
                room.votes[title_id] = {}
            room.votes[title_id][user_name] = vote
            
            total_score = sum(room.votes[title_id].values())
            return {
                "title_id": title_id,
                "total_score": total_score,
                "voter_count": len(room.votes[title_id])
            }

    def get_room_state(self, room_code: str, db: Session) -> Optional[Dict[str, Any]]:
        with self._lock:
            room = self._rooms.get(room_code.upper())
            if not room:
                return None

            # Merge all participants' subscriptions
            combined_subs = set()
            for subs in room.participants.values():
                combined_subs.update(subs)

            candidates_data = []
            for tid in room.candidate_title_ids:
                t = db.query(Title).filter(Title.id == tid).first()
                if t:
                    score = sum(room.votes.get(tid, {}).values())
                    voters = room.votes.get(tid, {})
                    formatted = format_title_response(t, combined_subs, {})
                    candidates_data.append({
                        "title": formatted.model_dump(),
                        "score": score,
                        "votes": voters
                    })

            # Sort by highest score
            candidates_data.sort(key=lambda x: x["score"], reverse=True)
            winner = candidates_data[0] if candidates_data else None

            return {
                "room_code": room.room_code,
                "host_name": room.host_name,
                "participants": list(room.participants.keys()),
                "combined_subscriptions": list(combined_subs),
                "candidates": candidates_data,
                "winning_title": winner["title"] if winner and winner["score"] > 0 else (candidates_data[0]["title"] if candidates_data else None)
            }

room_manager = RoomManager()
