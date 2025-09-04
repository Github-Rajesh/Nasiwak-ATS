from typing import List, Dict, Any, Optional
import logging
import json
import openai
from flask import current_app
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.utils.exceptions import MatchingServiceError

logger = logging.getLogger(__name__)

class AIResumeMatchingService:
    """AI-powered resume matching service using OpenAI GPT"""
    
    def __init__(self):
        self.api_key = current_app.config.get('OPENAI_API_KEY')
        self.model = current_app.config.get('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key:
            raise MatchingServiceError("OpenAI API key not configured")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def match_candidates(self, job_description: JobDescription, 
                        candidates: List[Candidate]) -> List[Candidate]:
        """
        Match candidates using AI analysis for human-like evaluation
        """
        try:
            logger.info(f"AI matching {len(candidates)} candidates against job: {job_description.display_name}")
            
            if not candidates:
                logger.warning("No candidates provided for AI matching")
                return []
            
            # Process candidates in batches to avoid token limits
            batch_size = 5  # Process 5 resumes at a time
            all_scored_candidates = []
            
            for i in range(0, len(candidates), batch_size):
                batch = candidates[i:i+batch_size]
                scored_batch = self._analyze_batch(job_description, batch)
                all_scored_candidates.extend(scored_batch)
            
            # Sort by AI score
            ranked_candidates = sorted(all_scored_candidates, 
                                     key=lambda x: x.score, reverse=True)
            
            # Assign ranks
            for rank, candidate in enumerate(ranked_candidates, 1):
                candidate.rank = rank
            
            logger.info(f"AI matching completed. Top score: {ranked_candidates[0].score:.3f}")
            return ranked_candidates
            
        except Exception as e:
            logger.error(f"Error in AI candidate matching: {e}")
            raise MatchingServiceError(f"Failed to perform AI matching: {e}")
    
    def _analyze_batch(self, job_description: JobDescription, 
                      candidates: List[Candidate]) -> List[Candidate]:
        """Analyze a batch of candidates using AI"""
        
        # Prepare the prompt
        prompt = self._create_analysis_prompt(job_description, candidates)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=2000
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, candidates)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # Fallback to basic scoring if AI fails
            for candidate in candidates:
                candidate.score = 0.5  # Neutral score
                candidate.ai_analysis = f"AI analysis unavailable: {str(e)}"
            return candidates
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis"""
        return """You are an expert HR recruiter and resume analyzer. Your task is to evaluate how well candidates match a job description with a human touch, considering:

1. **Technical Skills Match**: How well do the candidate's technical skills align with job requirements?
2. **Experience Relevance**: Is their experience relevant to the role and industry?
3. **Education Fit**: Does their educational background support the role?
4. **Career Progression**: Does their career show growth and relevant progression?
5. **Cultural Fit**: Based on their background, would they likely fit the role's requirements?
6. **Potential**: Even if not a perfect match, do they show potential to grow into the role?

Provide scores from 0.0 to 1.0 (where 1.0 is perfect match) and brief, human-readable explanations.
Be realistic but fair - consider both current skills and potential for growth."""
    
    def _create_analysis_prompt(self, job_description: JobDescription, 
                               candidates: List[Candidate]) -> str:
        """Create the analysis prompt for AI"""
        
        # Truncate job description if too long
        job_content = job_description.processed_text or job_description.description
        job_text = job_content[:2000] if len(job_content) > 2000 else job_content
        
        prompt = f"""Job Description:
{job_text}

Please analyze the following candidates and provide a JSON response with scores and brief explanations:

"""
        
        for i, candidate in enumerate(candidates):
            # Truncate resume text if too long
            resume_text = candidate.resume_text[:1500] if candidate.resume_text and len(candidate.resume_text) > 1500 else candidate.resume_text
            
            prompt += f"""
Candidate {i+1} ({candidate.display_name}):
Skills: {', '.join(candidate.skills[:10]) if candidate.skills else 'Not specified'}
Education: {', '.join(candidate.education[:3]) if candidate.education else 'Not specified'}
Experience: {', '.join(candidate.experience[:3]) if candidate.experience else 'Not specified'}
Resume Content: {resume_text or 'Content not available'}

---
"""
        
        prompt += """
Please respond with a JSON array where each object has:
{
  "candidate_index": 0,  // 0-based index
  "score": 0.85,         // Score from 0.0 to 1.0
  "explanation": "Strong match for backend development role. Has 5+ years Python/Django experience, relevant cloud skills, and good career progression. Minor gap in specific framework mentioned in JD.",
  "strengths": ["Python expertise", "Cloud experience", "Good career progression"],
  "concerns": ["Limited experience with specific framework", "No mention of team leadership"]
}

Respond ONLY with the JSON array, no additional text."""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, 
                          candidates: List[Candidate]) -> List[Candidate]:
        """Parse AI response and assign scores to candidates"""
        
        try:
            # Clean the response and parse JSON
            ai_response = ai_response.strip()
            if ai_response.startswith('```json'):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith('```'):
                ai_response = ai_response[3:-3]
            
            analysis_results = json.loads(ai_response)
            
            # Apply scores and analysis to candidates
            for result in analysis_results:
                candidate_index = result.get('candidate_index', 0)
                if 0 <= candidate_index < len(candidates):
                    candidate = candidates[candidate_index]
                    candidate.score = float(result.get('score', 0.5))
                    candidate.ai_analysis = result.get('explanation', 'No analysis available')
                    candidate.ai_strengths = result.get('strengths', [])
                    candidate.ai_concerns = result.get('concerns', [])
            
            # Ensure all candidates have scores
            for candidate in candidates:
                if not hasattr(candidate, 'score') or candidate.score is None:
                    candidate.score = 0.3  # Default score
                    candidate.ai_analysis = "Analysis incomplete"
            
            return candidates
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing AI response: {e}")
            logger.debug(f"AI response was: {ai_response}")
            
            # Fallback: assign default scores
            for i, candidate in enumerate(candidates):
                candidate.score = 0.4 + (i * 0.1) % 0.3  # Vary scores slightly
                candidate.ai_analysis = "AI analysis parsing failed - using fallback scoring"
            
            return candidates
    
    def get_detailed_analysis(self, job_description: JobDescription, 
                             candidate: Candidate) -> Dict[str, Any]:
        """Get detailed AI analysis for a single candidate"""
        
        try:
            job_content = job_description.processed_text or job_description.description
            prompt = f"""
Job Description:
{job_content[:2000]}

Candidate Details:
Name: {candidate.display_name}
Skills: {', '.join(candidate.skills) if candidate.skills else 'Not specified'}
Education: {', '.join(candidate.education) if candidate.education else 'Not specified'}
Experience: {', '.join(candidate.experience) if candidate.experience else 'Not specified'}

Resume Content:
{candidate.resume_text[:3000] if candidate.resume_text else 'Content not available'}

Please provide a detailed analysis including:
1. Overall match score (0.0 to 1.0)
2. Key strengths for this role
3. Areas of concern or gaps
4. Recommendations for interview focus
5. Growth potential assessment

Respond in JSON format with these fields: score, strengths, concerns, interview_focus, growth_potential, summary
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            return json.loads(ai_response.strip())
            
        except Exception as e:
            logger.error(f"Error getting detailed analysis: {e}")
            return {
                "score": candidate.score or 0.5,
                "strengths": ["Analysis unavailable"],
                "concerns": [f"AI analysis failed: {str(e)}"],
                "interview_focus": ["Technical skills assessment"],
                "growth_potential": "Unable to assess",
                "summary": "Detailed analysis unavailable due to technical issues"
            }
