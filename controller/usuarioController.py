from app import app, usuarios
from flask import render_template, request, redirect

@app.route('/', methods=['GET', 'POST'])
def login():
    pass