from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file, current_app
from pathlib import Path
from app.services.resume_parser import ResumeParserFactory
from app.services.matching_service import ResumeMatchingService
from app.services.ai_matching_service import AIResumeMatchingService
from app.services.file_service import FileService
from app.models.job_description import JobDescription
from app.utils.decorators import login_required
from app.utils.exceptions import ResumeParsingError, MatchingServiceError, FileServiceError
import logging

logger = logging.getLogger(__name__)
resume_bp = Blueprint('resume', __name__)

def _parse_resume_files(resume_files):
    """Parse resume files and return candidates"""
    candidates = []
    parser_factory = ResumeParserFactory()
    print(f"DEBUG: Starting to parse {len(resume_files)} resume files")
    
    for i, file_path in enumerate(resume_files):
        try:
            print(f"DEBUG: Parsing file {i+1}/{len(resume_files)}: {file_path.name}")
            parser = parser_factory.get_parser(file_path.suffix)
            print(f"DEBUG: Got parser for {file_path.name}")
            candidate = parser.parse(file_path)
            print(f"DEBUG: Successfully parsed {file_path.name}")
            candidates.append(candidate)
            logger.info(f"Successfully parsed: {file_path.name}")
        except Exception as e:
            print(f"DEBUG: Failed to parse {file_path.name}: {e}")
            logger.error(f"Failed to parse {file_path.name}: {e}")
            continue
    
    print(f"DEBUG: Finished parsing. Got {len(candidates)} candidates")
    return candidates

@resume_bp.route('/process', methods=['POST'])
@login_required
def process_resumes():
    """Process resumes against selected job description"""
    print("DEBUG: Starting process_resumes function")
    try:
        job_description_file = request.form.get('job_description')
        print(f"DEBUG: Job description file: {job_description_file}")
        if not job_description_file:
            flash('Please select a job description', 'error')
            return redirect(url_for('main.index'))
        
        file_service = FileService()
        print("DEBUG: FileService created")
        
        # Load job description
        job_file_path = file_service.job_descriptions_folder / job_description_file
        print(f"DEBUG: Job file path: {job_file_path}")
        if not job_file_path.exists():
            flash('Selected job description not found', 'error')
            return redirect(url_for('main.index'))
        
        # Parse job description
        job_description = JobDescription.from_file(job_file_path)
        print(f"DEBUG: Job description loaded: {job_description.title}")
        
        # Get resume files
        resume_files = file_service.get_resume_files()
        print(f"DEBUG: Found {len(resume_files)} resume files")
        if not resume_files:
            flash('No resume files found. Please upload some resumes first.', 'error')
            return redirect(url_for('main.index'))
        
        candidates = _parse_resume_files(resume_files)
        print(f"DEBUG: Parsed {len(candidates)} candidates")
        
        if not candidates:
            flash('No resumes could be parsed successfully', 'error')
            return redirect(url_for('main.index'))

        # Match candidates using AI or traditional method
        use_ai = current_app.config.get('USE_AI_MATCHING', False)
        openai_key = current_app.config.get('OPENAI_API_KEY')
        print(f"DEBUG: use_ai={use_ai}, has_openai_key={bool(openai_key)}")
        
        if use_ai and openai_key:
            print("DEBUG: Using AI-powered matching")
            logger.info("Using AI-powered matching")
            try:
                ai_matching_service = AIResumeMatchingService()
                print("DEBUG: Created AI matching service")
                print(f"DEBUG: Job description has processed_text: {hasattr(job_description, 'processed_text')}")
                print(f"DEBUG: Job description has description: {hasattr(job_description, 'description')}")
                print(f"DEBUG: Job description has content: {hasattr(job_description, 'content')}")
                if hasattr(job_description, 'processed_text'):
                    print(f"DEBUG: processed_text length: {len(job_description.processed_text) if job_description.processed_text else 0}")
                if hasattr(job_description, 'description'):
                    print(f"DEBUG: description length: {len(job_description.description) if job_description.description else 0}")
                ranked_candidates = ai_matching_service.match_candidates(job_description, candidates)
                print("DEBUG: AI matching completed successfully")
                flash('Results generated using AI analysis', 'info')
            except Exception as e:
                print(f"DEBUG: AI matching failed with error: {e}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
                logger.warning(f"AI matching failed, falling back to traditional: {e}")
                # Fallback to traditional matching
                matching_service = ResumeMatchingService(
                    top_candidates_count=20,
                    similarity_threshold=0.01
                )
                ranked_candidates = matching_service.match_candidates(job_description, candidates)
                flash('AI analysis unavailable, using traditional matching', 'warning')
        else:
            logger.info("Using traditional TF-IDF matching")
            matching_service = ResumeMatchingService(
                top_candidates_count=20,
                similarity_threshold=0.01
            )
            ranked_candidates = matching_service.match_candidates(job_description, candidates)
            if not openai_key:
                flash('Set OPENAI_API_KEY environment variable to enable AI analysis', 'info')
        
        logger.info(f"Successfully processed {len(ranked_candidates)} candidates")
        
        return render_template('results.html', 
                             candidates=ranked_candidates,
                             job_description=job_description)
        
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        logger.error(f"Error processing resumes: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        flash('Failed to process resumes. Please try again.', 'error')
        return redirect(url_for('main.index'))

@resume_bp.route('/download/<path:filename>')
@login_required
def download_resume(filename):
    """Download a resume file"""
    try:
        logger.info(f"Download request for file: {filename}")
        file_service = FileService()
        file_path = file_service.upload_folder / filename
        
        logger.info(f"Looking for file at: {file_path}")
        logger.info(f"Upload folder: {file_service.upload_folder}")
        logger.info(f"File exists: {file_path.exists()}")
        
        if not file_path.exists():
            # Also try with just the filename without any path components
            simple_filename = Path(filename).name
            file_path = file_service.upload_folder / simple_filename
            logger.info(f"Trying simple filename: {simple_filename} at {file_path}")
            
            if not file_path.exists():
                logger.error(f"File not found: {filename}")
                flash(f'File not found: {filename}', 'error')
                return redirect(url_for('main.index'))
        
        logger.info(f"Sending file: {file_path}")
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        flash(f'Failed to download file: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Upload new resume file"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('main.index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('main.index'))
        
        file_service = FileService()
        saved_path = file_service.save_uploaded_file(file)
        
        flash(f'Resume uploaded successfully: {saved_path.name}', 'success')
        return redirect(url_for('main.index'))
        
    except FileServiceError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        flash('Failed to upload resume', 'error')
        return redirect(url_for('main.index'))