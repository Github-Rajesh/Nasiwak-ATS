from typing import List, Optional
import logging
from app.models.candidate import Candidate
from app.models.database import CandidateModel
from app.extensions import db
from app.utils.exceptions import CandidatePersistenceError

logger = logging.getLogger(__name__)

class CandidatePersistenceService:
    """Service for persisting and retrieving candidates from database"""
    
    def save_candidates(self, candidates: List[Candidate]) -> None:
        """Save candidates to database"""
        try:
            logger.info(f"Saving {len(candidates)} candidates to database")
            
            for candidate in candidates:
                # Check if candidate already exists
                existing_candidate = CandidateModel.query.filter_by(id=candidate.id).first()
                
                if existing_candidate:
                    # Update existing candidate
                    self._update_candidate_from_dataclass(existing_candidate, candidate)
                    logger.debug(f"Updated existing candidate: {candidate.display_name}")
                else:
                    # Create new candidate
                    candidate_model = CandidateModel.from_candidate(candidate)
                    db.session.add(candidate_model)
                    logger.debug(f"Added new candidate: {candidate.display_name}")
            
            db.session.commit()
            logger.info("Successfully saved candidates to database")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving candidates: {e}")
            raise CandidatePersistenceError(f"Failed to save candidates: {e}")
    
    def load_candidates_by_resume_paths(self, resume_paths: List[str]) -> List[Candidate]:
        """Load candidates from database by resume paths"""
        try:
            logger.info(f"Loading candidates for {len(resume_paths)} resume paths")
            
            candidates = []
            for resume_path in resume_paths:
                candidate_model = CandidateModel.query.filter_by(
                    resume_path=resume_path, 
                    is_active=True
                ).first()
                
                if candidate_model:
                    candidate = candidate_model.to_candidate()
                    candidates.append(candidate)
                    logger.debug(f"Loaded candidate from DB: {candidate.display_name}")
            
            logger.info(f"Loaded {len(candidates)} candidates from database")
            return candidates
            
        except Exception as e:
            logger.error(f"Error loading candidates: {e}")
            raise CandidatePersistenceError(f"Failed to load candidates: {e}")
    
    def _update_candidate_from_dataclass(self, model: CandidateModel, candidate: Candidate) -> None:
        """Update database model with data from candidate dataclass"""
        try:
            model.name = candidate.name
            model.email = candidate.email
            model.phone = candidate.phone
            model.skills = candidate.skills
            model.education = candidate.education
            model.experience = candidate.experience
            model.competencies = candidate.competencies
            model.resume_path = str(candidate.resume_path) if candidate.resume_path else None
            model.resume_text = candidate.resume_text
            model.score = candidate.score
            model.rank = candidate.rank
            model.ai_analysis = candidate.ai_analysis
            model.ai_strengths = candidate.ai_strengths
            model.ai_concerns = candidate.ai_concerns
            
        except Exception as e:
            logger.error(f"Error updating candidate model: {e}")
            raise CandidatePersistenceError(f"Failed to update candidate: {e}")
    
    def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Get a single candidate by ID"""
        try:
            candidate_model = CandidateModel.query.filter_by(
                id=candidate_id, 
                is_active=True
            ).first()
            
            if candidate_model:
                return candidate_model.to_candidate()
            return None
            
        except Exception as e:
            logger.error(f"Error getting candidate by ID: {e}")
            raise CandidatePersistenceError(f"Failed to get candidate: {e}")
    
    def delete_candidate(self, candidate_id: str) -> bool:
        """Soft delete a candidate by setting is_active to False"""
        try:
            candidate_model = CandidateModel.query.filter_by(id=candidate_id).first()
            
            if candidate_model:
                candidate_model.is_active = False
                db.session.commit()
                logger.info(f"Soft deleted candidate: {candidate_id}")
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting candidate: {e}")
            raise CandidatePersistenceError(f"Failed to delete candidate: {e}")
