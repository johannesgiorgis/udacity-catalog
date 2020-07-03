"""
Main
"""

from fastapi import FastAPI

import udacity

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/udacity")
def get_udacity():
    return udacity.get_udacity_catalog_list()
