from app.extensions import db
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
import json
from pathlib import Path

class CandidateModel(db.Model):
    __tablename__ = 'candidates'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    skills = Column(Text)  # JSON string
    education = Column(Text)  # JSON string
    experience = Column(Text)  # JSON string
    competencies = Column(Text)  # JSON string
    resume_path = Column(String(255))
    resume_text = Column(Text)
    score = Column(Float)
    rank = Column(Integer)
    # AI Analysis fields
    ai_analysis = Column(Text)
    ai_strengths = Column(Text)  # JSON string
    ai_concerns = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    def to_candidate(self):
        """Convert database model to Candidate dataclass"""
        from app.models.candidate import Candidate
        
        return Candidate(
            id=self.id,
            name=self.name,
            email=self.email,
            phone=self.phone,
            skills=json.loads(self.skills) if self.skills else [],
            education=json.loads(self.education) if self.education else [],
            experience=json.loads(self.experience) if self.experience else [],
            competencies=json.loads(self.competencies) if self.competencies else {},
            resume_path=Path(self.resume_path) if self.resume_path else None,
            resume_text=self.resume_text,
            score=self.score,
            rank=self.rank,
            ai_analysis=self.ai_analysis,
            ai_strengths=json.loads(self.ai_strengths) if self.ai_strengths else [],
            ai_concerns=json.loads(self.ai_concerns) if self.ai_concerns else []
        )
    
    @classmethod
    def from_candidate(cls, candidate):
        """Create database model from Candidate dataclass"""
        return cls(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            skills=json.dumps(candidate.skills),
            education=json.dumps(candidate.education),
            experience=json.dumps(candidate.experience),
            competencies=json.dumps(candidate.competencies),
            resume_path=str(candidate.resume_path) if candidate.resume_path else None,
            resume_text=candidate.resume_text,
            score=candidate.score,
            rank=candidate.rank,
            ai_analysis=candidate.ai_analysis,
            ai_strengths=json.dumps(candidate.ai_strengths),
            ai_concerns=json.dumps(candidate.ai_concerns)
        )

class JobDescriptionModel(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = Column(String(36), primary_key=True)
    title = Column(String(200))
    description = Column(Text)
    requirements = Column(Text)  # JSON string
    skills = Column(Text)  # JSON string
    file_path = Column(String(255))
    processed_text = Column(Text)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    def to_job_description(self):
        """Convert database model to JobDescription dataclass"""
        from app.models.job_description import JobDescription
        
        return JobDescription(
            id=self.id,
            title=self.title,
            description=self.description,
            requirements=json.loads(self.requirements) if self.requirements else [],
            skills=json.loads(self.skills) if self.skills else [],
            file_path=Path(self.file_path) if self.file_path else None,
            processed_text=self.processed_text
        )