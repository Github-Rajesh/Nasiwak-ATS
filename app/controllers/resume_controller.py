from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file, current_app
from pathlib import Path
import zipfile
import csv
import io
import tempfile
import os
from app.services.resume_parser import ResumeParserFactory
from app.services.matching_service import ResumeMatchingService
from app.services.ai_matching_service import AIResumeMatchingService
from app.services.file_service import FileService
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.services.candidate_persistence_service import CandidatePersistenceService
from app.models.job_description import JobDescription
from app.utils.decorators import login_required
from app.utils.exceptions import ResumeParsingError, MatchingServiceError, FileServiceError, DuplicateDetectionError, CandidatePersistenceError
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
        
        # Try to load existing candidates from database first
        persistence_service = CandidatePersistenceService()
        resume_paths = [str(f) for f in resume_files]
        existing_candidates = persistence_service.load_candidates_by_resume_paths(resume_paths)
        
        # Parse any new resume files that aren't in the database
        existing_paths = {c.resume_path for c in existing_candidates if c.resume_path}
        new_resume_files = [f for f in resume_files if str(f) not in existing_paths]
        
        new_candidates = []
        if new_resume_files:
            new_candidates = _parse_resume_files(new_resume_files)
            print(f"DEBUG: Parsed {len(new_candidates)} new candidates")
        
        # Combine existing and new candidates
        candidates = existing_candidates + new_candidates
        print(f"DEBUG: Total candidates: {len(candidates)} (existing: {len(existing_candidates)}, new: {len(new_candidates)})")
        
        if not candidates:
            flash('No resumes could be parsed successfully', 'error')
            return redirect(url_for('main.index'))
        
        # Detect and remove duplicates
        try:
            duplicate_service = DuplicateDetectionService()
            duplicates = duplicate_service.detect_duplicates(candidates)
            
            if duplicates:
                logger.info(f"Found {len(duplicates)} duplicate pairs")
                candidates = duplicate_service.remove_duplicates(candidates, duplicates)
                flash(f'Removed {len(duplicates)} duplicate resumes. Processing {len(candidates)} unique candidates.', 'info')
            else:
                logger.info("No duplicates found")
                
        except DuplicateDetectionError as e:
            logger.warning(f"Duplicate detection failed: {e}")
            flash('Duplicate detection failed, proceeding with all resumes', 'warning')

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
        
        # Save candidates to database for future consistency
        try:
            persistence_service.save_candidates(ranked_candidates)
            logger.info("Successfully saved candidates to database")
        except CandidatePersistenceError as e:
            logger.warning(f"Failed to save candidates to database: {e}")
            # Continue without failing the request
        
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

@resume_bp.route('/bulk_download', methods=['POST'])
@login_required
def bulk_download_resumes():
    """Download all resumes as a ZIP file"""
    try:
        # Get the candidates data from the session or request
        candidates_data = request.get_json()
        if not candidates_data or 'candidates' not in candidates_data:
            flash('No candidates data provided', 'error')
            return redirect(url_for('main.index'))
        
        candidates = candidates_data['candidates']
        if not candidates:
            flash('No candidates to download', 'error')
            return redirect(url_for('main.index'))
        
        # Create a temporary ZIP file
        temp_zip = io.BytesIO()
        
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            file_service = FileService()
            
            for candidate in candidates:
                if candidate.get('resume_path'):
                    resume_filename = candidate['resume_path']
                    resume_path = file_service.upload_folder / resume_filename
                    
                    if resume_path.exists():
                        # Add file to ZIP with a clean name
                        clean_name = f"{candidate.get('name', 'Unknown')}_{resume_filename}"
                        zip_file.write(resume_path, clean_name)
                    else:
                        logger.warning(f"Resume file not found: {resume_path}")
        
        temp_zip.seek(0)
        
        return send_file(
            temp_zip,
            as_attachment=True,
            download_name='resumes_bulk_download.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Error creating bulk download: {e}")
        flash('Failed to create bulk download', 'error')
        return redirect(url_for('main.index'))

@resume_bp.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    """Export candidates data as CSV"""
    try:
        # Get the candidates data from the session or request
        candidates_data = request.get_json()
        if not candidates_data or 'candidates' not in candidates_data:
            flash('No candidates data provided', 'error')
            return redirect(url_for('main.index'))
        
        candidates = candidates_data['candidates']
        if not candidates:
            flash('No candidates to export', 'error')
            return redirect(url_for('main.index'))
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Rank', 'Name', 'Email', 'Phone', 'Skills', 'Score', 
            'AI Analysis', 'Strengths', 'Concerns', 'Resume File'
        ])
        
        # Write candidate data
        for candidate in candidates:
            # Format lists as comma-separated strings
            skills_str = ', '.join(candidate.get('skills', []))
            strengths_str = ', '.join(candidate.get('ai_strengths', []))
            concerns_str = ', '.join(candidate.get('ai_concerns', []))
            
            writer.writerow([
                candidate.get('rank', ''),
                candidate.get('name', ''),
                candidate.get('email', ''),
                candidate.get('phone', ''),
                skills_str,
                candidate.get('score', ''),
                candidate.get('ai_analysis', ''),
                strengths_str,
                concerns_str,
                candidate.get('resume_path', '')
            ])
        
        output.seek(0)
        
        # Create response with CSV content
        response = current_app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=candidates_analysis.csv'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        flash('Failed to export CSV', 'error')
        return redirect(url_for('main.index'))