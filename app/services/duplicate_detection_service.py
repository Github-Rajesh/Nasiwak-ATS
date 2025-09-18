from typing import List, Dict, Any, Tuple
import hashlib
import logging
from pathlib import Path
from app.models.candidate import Candidate
from app.utils.exceptions import DuplicateDetectionError

logger = logging.getLogger(__name__)

class DuplicateDetectionService:
    """Service for detecting and managing duplicate resumes"""
    
    def __init__(self):
        self.similarity_threshold = 0.85  # Threshold for considering resumes as duplicates
    
    def detect_duplicates(self, candidates: List[Candidate]) -> List[Tuple[Candidate, Candidate, float]]:
        """
        Detect duplicate candidates based on multiple criteria
        Returns list of tuples: (candidate1, candidate2, similarity_score)
        """
        try:
            logger.info(f"Detecting duplicates among {len(candidates)} candidates")
            
            duplicates = []
            
            for i in range(len(candidates)):
                for j in range(i + 1, len(candidates)):
                    candidate1 = candidates[i]
                    candidate2 = candidates[j]
                    
                    similarity = self._calculate_similarity(candidate1, candidate2)
                    
                    if similarity >= self.similarity_threshold:
                        duplicates.append((candidate1, candidate2, similarity))
                        logger.info(f"Found duplicate: {candidate1.display_name} <-> {candidate2.display_name} (similarity: {similarity:.3f})")
            
            logger.info(f"Found {len(duplicates)} duplicate pairs")
            return duplicates
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            raise DuplicateDetectionError(f"Failed to detect duplicates: {e}")
    
    def _calculate_similarity(self, candidate1: Candidate, candidate2: Candidate) -> float:
        """Calculate similarity between two candidates"""
        try:
            # Check file hash similarity (exact duplicates)
            if self._are_files_identical(candidate1, candidate2):
                return 1.0
            
            # Check content similarity
            content_similarity = self._calculate_content_similarity(candidate1, candidate2)
            
            # Check contact info similarity
            contact_similarity = self._calculate_contact_similarity(candidate1, candidate2)
            
            # Check skills similarity
            skills_similarity = self._calculate_skills_similarity(candidate1, candidate2)
            
            # Weighted average of different similarity measures
            total_similarity = (
                content_similarity * 0.4 +
                contact_similarity * 0.3 +
                skills_similarity * 0.3
            )
            
            return total_similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _are_files_identical(self, candidate1: Candidate, candidate2: Candidate) -> bool:
        """Check if resume files are identical using hash comparison"""
        try:
            if not candidate1.resume_path or not candidate2.resume_path:
                return False
            
            if not candidate1.resume_path.exists() or not candidate2.resume_path.exists():
                return False
            
            # Calculate file hashes
            hash1 = self._calculate_file_hash(candidate1.resume_path)
            hash2 = self._calculate_file_hash(candidate2.resume_path)
            
            return hash1 == hash2
            
        except Exception as e:
            logger.error(f"Error checking file identity: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def _calculate_content_similarity(self, candidate1: Candidate, candidate2: Candidate) -> float:
        """Calculate similarity based on resume text content"""
        try:
            text1 = candidate1.resume_text or ""
            text2 = candidate2.resume_text or ""
            
            if not text1 or not text2:
                return 0.0
            
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    def _calculate_contact_similarity(self, candidate1: Candidate, candidate2: Candidate) -> float:
        """Calculate similarity based on contact information"""
        try:
            similarity = 0.0
            matches = 0
            total_checks = 0
            
            # Email similarity
            if candidate1.email and candidate2.email:
                total_checks += 1
                if candidate1.email.lower() == candidate2.email.lower():
                    matches += 1
                    similarity += 1.0
            
            # Phone similarity
            if candidate1.phone and candidate2.phone:
                total_checks += 1
                phone1 = self._normalize_phone(candidate1.phone)
                phone2 = self._normalize_phone(candidate2.phone)
                if phone1 == phone2:
                    matches += 1
                    similarity += 1.0
            
            # Name similarity
            if candidate1.name and candidate2.name:
                total_checks += 1
                name1 = candidate1.name.lower().strip()
                name2 = candidate2.name.lower().strip()
                if name1 == name2:
                    matches += 1
                    similarity += 1.0
            
            return similarity / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating contact similarity: {e}")
            return 0.0
    
    def _calculate_skills_similarity(self, candidate1: Candidate, candidate2: Candidate) -> float:
        """Calculate similarity based on skills"""
        try:
            skills1 = set(skill.lower() for skill in candidate1.skills)
            skills2 = set(skill.lower() for skill in candidate2.skills)
            
            if not skills1 or not skills2:
                return 0.0
            
            intersection = len(skills1.intersection(skills2))
            union = len(skills1.union(skills2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating skills similarity: {e}")
            return 0.0
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        try:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, phone))
            return digits
        except Exception as e:
            logger.error(f"Error normalizing phone: {e}")
            return phone
    
    def remove_duplicates(self, candidates: List[Candidate], 
                         duplicates: List[Tuple[Candidate, Candidate, float]]) -> List[Candidate]:
        """
        Remove duplicate candidates, keeping the one with higher score or better data
        """
        try:
            logger.info(f"Removing duplicates from {len(candidates)} candidates")
            
            # Create a set of candidates to remove
            candidates_to_remove = set()
            
            for candidate1, candidate2, similarity in duplicates:
                # Decide which candidate to keep
                candidate_to_remove = self._choose_candidate_to_remove(candidate1, candidate2)
                candidates_to_remove.add(candidate_to_remove.id)
                logger.info(f"Marking for removal: {candidate_to_remove.display_name}")
            
            # Filter out duplicates
            filtered_candidates = [
                candidate for candidate in candidates 
                if candidate.id not in candidates_to_remove
            ]
            
            logger.info(f"Removed {len(candidates) - len(filtered_candidates)} duplicates")
            return filtered_candidates
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            raise DuplicateDetectionError(f"Failed to remove duplicates: {e}")
    
    def _choose_candidate_to_remove(self, candidate1: Candidate, candidate2: Candidate) -> Candidate:
        """Choose which candidate to remove based on data quality and score"""
        try:
            # Prefer candidate with higher score
            if candidate1.score is not None and candidate2.score is not None:
                if candidate1.score > candidate2.score:
                    return candidate2
                elif candidate2.score > candidate1.score:
                    return candidate1
            
            # Prefer candidate with more complete data
            data_completeness1 = self._calculate_data_completeness(candidate1)
            data_completeness2 = self._calculate_data_completeness(candidate2)
            
            if data_completeness1 > data_completeness2:
                return candidate2
            elif data_completeness2 > data_completeness1:
                return candidate1
            
            # If all else is equal, prefer the first one (arbitrary choice)
            return candidate2
            
        except Exception as e:
            logger.error(f"Error choosing candidate to remove: {e}")
            return candidate2
    
    def _calculate_data_completeness(self, candidate: Candidate) -> float:
        """Calculate how complete the candidate's data is"""
        try:
            completeness = 0.0
            total_fields = 6  # name, email, phone, skills, education, experience
            
            if candidate.name:
                completeness += 1
            if candidate.email:
                completeness += 1
            if candidate.phone:
                completeness += 1
            if candidate.skills:
                completeness += 1
            if candidate.education:
                completeness += 1
            if candidate.experience:
                completeness += 1
            
            return completeness / total_fields
            
        except Exception as e:
            logger.error(f"Error calculating data completeness: {e}")
            return 0.0
