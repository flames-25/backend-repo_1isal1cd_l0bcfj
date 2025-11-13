import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Product, CaseStudy, IndustrySolution, RFQ, Certification

app = FastAPI(title="B2B Oil & Gas Supplier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Oil & Gas Supplier Backend Ready"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Seed helper for demo content if collections are empty
@app.post("/seed")
def seed_demo_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Only seed if empty
    prod_count = db["product"].count_documents({})
    case_count = db["casestudy"].count_documents({})
    sol_count = db["industrysolution"].count_documents({})

    if prod_count == 0:
        create_document("product", Product(
            slug="cryogenic-solenoid-valve-csv200",
            name="Cryogenic Solenoid Valve CSV-200",
            category="Valves",
            description="High-reliability cryogenic solenoid valve for LNG applications down to -196°C.",
            image_url="https://images.unsplash.com/photo-1581091215367-59ab6d7c1b5b?q=80&w=1200&auto=format&fit=crop",
            spec_pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            certifications=[
                Certification(name="ISO 9001:2015", pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"),
                Certification(name="API 6D", pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
            ],
            tags=["cryogenic", "valve", "LNG", "solenoid"]
        ))
        create_document("product", Product(
            slug="downhole-pressure-sensor-dps50",
            name="Downhole Pressure Sensor DPS-50",
            category="Sensors",
            description="High-accuracy downhole pressure sensor rated up to 20k psi for drilling ops.",
            image_url="https://images.unsplash.com/photo-1606229365485-931b9043d692?q=80&w=1200&auto=format&fit=crop",
            spec_pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            certifications=[
                Certification(name="ISO 14001", pdf_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
            ],
            tags=["sensor", "downhole", "pressure"]
        ))

    if sol_count == 0:
        create_document("industrysolution", IndustrySolution(
            slug="upstream-drilling-automation",
            title="Upstream Drilling Automation",
            segment="upstream",
            problem="Inconsistent pressure readings lead to NPT and safety risks.",
            solution="Deploy DPS-50 sensors with real-time telemetry to improve decision-making and reduce NPT.",
            related_products=["downhole-pressure-sensor-dps50"],
        ))
        create_document("industrysolution", IndustrySolution(
            slug="midstream-lng-cryogenic-handling",
            title="Midstream LNG Cryogenic Handling",
            segment="midstream",
            problem="Valve leakage at cryogenic temperatures causes loss and hazards.",
            solution="Implement CSV-200 with certified sealing for -196°C service.",
            related_products=["cryogenic-solenoid-valve-csv200"],
        ))

    if case_count == 0:
        create_document("casestudy", CaseStudy(
            slug="lng-terminal-leak-reduction",
            title="LNG Terminal Leak Reduction",
            client="Nordic LNG Co.",
            location="Norway",
            challenge="Frequent valve seat leaks during peak winter operations.",
            solution="Retrofitted 120 units of CSV-200 with improved seal design.",
            outcome="Leak incidents reduced by 87% within first quarter; improved throughput by 6%.",
            products_used=["cryogenic-solenoid-valve-csv200"],
            image_url="https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop"
        ))

    return {"status": "ok"}


# Public listing endpoints
@app.get("/products")
def list_products():
    if db is None:
        return []
    docs = get_documents("product")
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


@app.get("/products/{slug}")
def get_product(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["product"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    doc["_id"] = str(doc.get("_id"))
    return doc


@app.get("/solutions")
def list_solutions(segment: Optional[str] = None):
    if db is None:
        return []
    filter_q = {"segment": segment} if segment else {}
    docs = list(db["industrysolution"].find(filter_q))
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


@app.get("/case-studies")
def list_case_studies():
    if db is None:
        return []
    docs = list(db["casestudy"].find({}))
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# RFQ submission endpoint
@app.post("/rfq")
def submit_rfq(payload: RFQ):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    rfq_id = create_document("rfq", payload)
    return {"status": "received", "id": rfq_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
