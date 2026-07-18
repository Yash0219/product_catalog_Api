# E-Commerce Product Catalog Platform

A full-stack inventory management application featuring a decoupled backend API architecture and an interactive web control panel dashboard. The platform handles relational database interactions, inbound data validation, and structural constraint configurations.

Live Application Link: https://productcatalogapi-c4venhgccgbw8w3gevx4al.streamlit.app/

## Technical Architecture

* Backend Framework: FastAPI (Python)
* Frontend Framework: Streamlit
* ORM Layer: SQLAlchemy
* Database Engine: SQLite
* Deployment Infrastructure: Streamlit Cloud (Co-located Frontend and Backend Services)

## Key System Features

1. Relational Database Architecture: Mapped entities for Users, Categories, Products, and Reviews using foreign key configurations and bidirectional ORM relationships.
2. Server-Side Data Validation: Utilizes Pydantic schemas to validate data formats and types before interacting with the database layer, ensuring data integrity.
3. Relational Deletion Safeguards: Implements constraint handling on delete operations to prevent the removal of parent records (e.g., categories or users) that contain active children (products or reviews).

## Project Directory Layout

PROD_CATALOG_API/
├── database.py       # SQLite connection configuration and session lifecycles
├── models.py         # SQLAlchemy relational database tables mapping
├── schemas.py        # Pydantic validation structures for data transit
├── main.py           # FastAPI REST api endpoints and request handlers
├── app.py            # Streamlit dashboard interface and background server engine
└── requirements.txt  # Python environment dependency manifest

## Local Installation and Setup

Follow these steps to set up and run the platform locally:

1. Clone the repository:
   git clone https://github.com/Yash0219/product_catalog_Api.git
   cd product_catalog_Api

2. Initialize and activate a virtual environment:
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

3. Install required dependencies:
   pip install -r requirements.txt

4. Start the application:
   streamlit run app.py

The script will automatically initialize the local backend API server on port 8000 and render the visual interface dashboard in your browser.
