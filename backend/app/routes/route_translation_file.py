import configparser
from flask import Blueprint, request, jsonify, send_file
import os

from backend.app.routes import ocr_bp
from backend.app.services.service_ocr import multi_reader

@ocr_bp.route('/translate_file', methods=['POST'])
def tranlate_file():
    return None