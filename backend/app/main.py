from flask import Flask
import configparser

from backend.app.routes import create_app
from routes.ocr import ocr_bp
from routes.file_manager import file_manager_bp



if __name__ == '__main__':
    create_app().run()
