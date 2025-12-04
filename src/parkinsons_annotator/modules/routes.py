"""
Routes for UI, search, upload, and shutdown.

These creates the user interface and generates variables from the search and input sections which can
be used within the rest of the program.
The visuals and interactive elements of the interface are stored in a html file.
"""

import os
import signal
from flask import Blueprint, render_template, request, jsonify, current_app
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from parkinsons_annotator.modules.database_search import database_list, SearchFieldEmptyError, NoMatchingRecordsError
from parkinsons_annotator.modules.data_extraction import (dataframes,
                                                          load_single_file,
                                                          fill_variant_notation,
                                                          enrich_hgvs,
                                                          enrich_clinvar,
                                                          insert_dataframe_to_db)
from parkinsons_annotator.modules.db import get_db_session, close_db_session
from parkinsons_annotator.logger import logger
from parkinsons_annotator.utils.data_checks import compare_uploaded_vs_existing

route_blueprint = Blueprint('routes', __name__)

@route_blueprint.route('/', methods=['GET'])
def index():
    """This function opens the html file which contains the interface informtion"""
    # return render_template("interface_package.html")
    return render_template("interface_package.html")

@route_blueprint.route('/about', methods=['GET'])
def about():
    return render_template("info.html")

@route_blueprint.route('/search', methods=['POST'])
def search():
    """Handle search queries from the interface."""
    data = request.get_json()
    search_value = data.get('query', '').lower().strip()
    search_type = data.get('category', '').lower().strip()
    search_cat = data.get('searchCat', '').lower().strip()

    logger.info(f"User searched for: {search_value}, category: {search_type}")

    # Call the database search function
    try:
        results = database_list(search_type=search_type, search_value=search_value, search_cat=search_cat)
    except SearchFieldEmptyError:
        return jsonify({"message": "Missing search fields"}), 400
    except NoMatchingRecordsError:
        return jsonify({"message": "No matching records found"}), 404
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return jsonify({"message": "Internal server error"}), 500

    if search_type == 'variant':
        variant_object = results[0][0]
        patient_list = [row[1] for row in results]

        return jsonify({
            # Create an outer dictionary with variant: variant_info and patients: patient_list
            "variant": {
                # Create an inner dictionary for the variant with variant info fields
                "HGVS notation": variant_object.hgvs,
                "Genomic notation": variant_object.vcf_form,
                "ClinVar variant ID": variant_object.clinvar_id,
                "Gene symbol": variant_object.gene_symbol,
                "cDNA change": variant_object.cdna_change,
                "ClinVar accession": variant_object.clinvar_accession,
                "ClinVar consensus classification": variant_object.classification,
                "Number of submitted records": variant_object.num_records,
                "Review status": variant_object.review_status,
                "Associated condition": variant_object.associated_condition,
                "ClinVar record URL": variant_object.clinvar_url,
            },
            "patients": patient_list
            }), 200
    else:
        # All other searches are a basic list of tuples/values (containing no objects) which jsonify can handle
        return jsonify({"results": results}), 200

@route_blueprint.route('/upload', methods=['POST'])
def upload_file():
    """Handle a single file upload, enrich variant data, and insert into the database."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file part in the request", 400

    # Get file from form
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Ensure upload folder exists
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    # Save file to upload directory
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)
    logger.info(f"Uploaded file saved to: {filepath}")

    # Get database session
    session = get_db_session()

    # Run data extraction and insertion
    try:
        # Clear cache of previous dataframes
        dataframes.clear()
        # Load uploaded file
        load_single_file(filepath)
        # Enrich + insert for ONLY this patient
        for patient_name, df in dataframes.items():
            # Ensure patient does not already exist in DB with same variants
            result = compare_uploaded_vs_existing(patient_name, df, session)

            if result["exists"] and result["identical"]:
                logger.info(f"Upload for '{patient_name}' skipped — identical variants.")
                return f"Patient '{patient_name}' already exists with identical variants. Ignoring upload request"

            # Get notation/HGVS/ClinVar annotation then insert into DB
            df = (df
                  .pipe(fill_variant_notation)
                  .pipe(enrich_hgvs, session=session)
                  .pipe(enrich_clinvar, session=session)
                  )
            insert_dataframe_to_db(patient_name, df, session)
        # Commit any changes to DB
        session.commit()
        logger.info(f"File '{file.filename}' uploaded and processed successfully!")
        return f"File '{file.filename}' uploaded and processed successfully!", 200

    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        if session:
            session.rollback()  # rollback on error
        return f"Upload failed: {e}", 500

    finally:
        if session:
            close_db_session()  # ensures session is closed