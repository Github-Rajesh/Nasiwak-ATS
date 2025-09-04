from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
import PyPDF2
import docx2txt

@dataclass
class JobDescription:
    """Data model for job description information"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    file_path: Optional[Path] = None
    processed_text: Optional[str] = None
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'JobDescription':
        """Create JobDescription from file"""
        try:
            file_path = Path(file_path)
            text = ""
            
            if file_path.suffix.lower() == '.pdf':
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                text = docx2txt.process(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Extract title from filename or first line
            title = file_path.stem
            
            return cls(
                title=title,
                description=text.strip(),
                file_path=file_path,
                processed_text=text.strip()
            )
        except Exception as e:
            raise ValueError(f"Failed to load job description from {file_path}: {e}")
    
    @property
    def display_name(self) -> str:
        """Return display name or filename"""
        if self.title:
            return self.title
        if self.file_path:
            return self.file_path.stem
        return f"Job_{self.id[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job description to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'skills': self.skills,
            'file_path': str(self.file_path) if self.file_path else None
        }