import configparser
from flask import Blueprint, request, jsonify, send_file
import os

from backend.app.routes import ocr_bp
from backend.app.services.multi_ocr import multi_reader

@ocr_bp.route('/translate_text', methods=['POST'])
def tranlate_text():
    return None