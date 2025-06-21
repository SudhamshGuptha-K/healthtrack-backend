from fpdf import FPDF
import re

# -------------------------
# Reference Ranges
# -------------------------
reference_ranges = {
    "vitamin d": {
        "unit": "ng/mL",
        "ranges": {
            "deficient": (0, 20),
            "insufficient": (20, 30),
            "sufficient": (30, 100)
        },
        "advice": {
            "deficient": "Get 15–20 min sunlight daily, take Vitamin D3 supplement, eat eggs/fish.",
            "insufficient": "Get more sunlight and consider dietary sources.",
            "sufficient": "Maintain current levels."
        }
    },
    "hemoglobin a1c": {
        "unit": "%",
        "ranges": {
            "non-diabetic": (0, 5.7),
            "prediabetic": (5.7, 6.4),
            "diabetic": (6.5, 15)
        },
        "advice": {
            "prediabetic": "Reduce sugar, walk 20 min daily, avoid junk food.",
            "diabetic": "Consult doctor. Strict sugar control, regular exercise, low-carb diet.",
            "non-diabetic": "Maintain current lifestyle."
        }
    },
    "iron": {
        "unit": "µg/dL",
        "ranges": {
            "low": (0, 70),
            "normal": (70, 180)
        },
        "advice": {
            "low": "Eat iron-rich foods like spinach, nuts, red meat. Add Vitamin C for absorption.",
            "normal": "Iron levels are fine. Maintain with balanced diet."
        }
    },
    "tsh": {
        "unit": "µIU/mL",
        "ranges": {
            "low": (0, 0.35),
            "normal": (0.35, 5.5),
            "high": (5.5, 100)
        },
        "advice": {
            "low": "Possible hyperthyroidism. Consider retesting. Avoid self-medicating.",
            "normal": "TSH is normal. No action needed.",
            "high": "Possible hypothyroidism. Consult an endocrinologist."
        }
    },
    "egfr": {
        "unit": "mL/min/1.73m2",
        "ranges": {
            "normal": (90, 130),
            "mild decrease": (60, 90),
            "moderate decrease": (30, 60),
            "severe decrease": (15, 30),
            "kidney failure": (0, 15)
        },
        "advice": {
            "normal": "Your kidney function is healthy.",
            "mild decrease": "Stay hydrated, avoid excessive salt or painkillers.",
            "moderate decrease": "Kidney care recommended. Consult a nephrologist.",
            "severe decrease": "Serious concern. Seek specialist advice immediately.",
            "kidney failure": "Critical. Immediate medical attention required."
        }
    },
    "uric acid": {
        "unit": "mg/dL",
        "ranges": {
            "low": (0, 3.5),
            "normal": (3.5, 7.2),
            "high": (7.2, 15)
        },
        "advice": {
            "low": "Usually not a concern. Monitor if you feel fatigue or low energy.",
            "normal": "Good uric acid balance.",
            "high": "Reduce red meat, alcohol, sugary foods. Stay hydrated."
        }
    },
    "glucose": {
        "unit": "mg/dL",
        "ranges": {
            "normal": (70, 100),
            "prediabetic": (100, 125),
            "diabetic": (126, 300)
        },
        "advice": {
            "normal": "Blood sugar is normal. Keep up good lifestyle.",
            "prediabetic": "Reduce sugar/carbs, increase physical activity, track diet.",
            "diabetic": "Strict sugar control, regular exercise, consult doctor."
        }
    },
    "alt": {
        "unit": "U/L",
        "ranges": {
            "normal": (0, 40),
            "high": (40, 100)
        },
        "advice": {
            "normal": "ALT is normal. Liver is healthy.",
            "high": "May indicate liver stress. Avoid alcohol, oily food, and consult doctor."
        }
    },
    "ast": {
        "unit": "U/L",
        "ranges": {
            "normal": (0, 40),
            "high": (40, 100)
        },
        "advice": {
            "normal": "AST is normal. Liver & muscles healthy.",
            "high": "Could mean liver or muscle stress. Avoid heavy exercise & alcohol."
        }
    },
    "ldl": {
        "unit": "mg/dL",
        "ranges": {
            "optimal": (0, 100),
            "above optimal": (100, 130),
            "borderline high": (130, 160),
            "high": (160, 190),
            "very high": (190, 300)
        },
        "advice": {
            "optimal": "LDL is good. Maintain with diet & exercise.",
            "above optimal": "Slightly high. Cut back on fried/oily food.",
            "borderline high": "Limit fat, add exercise, track weekly.",
            "high": "Risk of heart issues. Consult doctor & start heart-healthy routine.",
            "very high": "Critical. Immediate medical attention required."
        }
    },
    "vitamin b12": {
        "unit": "pg/mL",
        "ranges": {
            "low": (0, 200),
            "normal": (200, 911)
        },
        "advice": {
            "low": "Take B12-rich foods (milk, eggs, meat) or consult doctor for injections.",
            "normal": "B12 levels are fine. Maintain diet."
        }
    },
    "folate": {
        "unit": "ng/mL",
        "ranges": {
            "deficient": (0, 3.4),
            "indeterminate": (3.4, 5.3),
            "normal": (5.4, 20)
        },
        "advice": {
            "deficient": "Eat green leafy veggies, lentils, take folic acid supplements.",
            "indeterminate": "Slightly low. Improve diet and retest in 2 weeks.",
            "normal": "Normal folate level. Maintain."
        }
    },
    "calcium": {
        "unit": "mg/dL",
        "ranges": {
            "low": (0, 8.1),
            "normal": (8.1, 10.4),
            "high": (10.5, 15)
        },
        "advice": {
            "low": "May affect bones. Eat dairy, leafy greens, or take calcium supplements.",
            "normal": "Normal calcium level.",
            "high": "Avoid calcium supplements. Consider retesting."
        }
    },
    "crp": {
        "unit": "mg/L",
        "ranges": {
            "normal": (0, 6),
            "high": (6, 100)
        },
        "advice": {
            "normal": "No signs of inflammation.",
            "high": "Body may have infection or inflammation. Track symptoms or consult doctor."
        }
    }
}

# -------------------------
# Extract lab values from text
# -------------------------
def extract_values(report_text):
    pattern = r"([\w\s\-]+):\s*([\d.]+)\s*([\w/%\u00b5]+)"
    matches = re.findall(pattern, report_text.lower())

    cleaned_data = {}
    for test, value, unit in matches:
        clean_test = test.strip().replace(":", "").lower()
        clean_test = clean_test.replace("–", "-").replace("  ", " ").strip()
        cleaned_data[clean_test] = {
            "value": float(value),
            "unit": unit
        }

    return cleaned_data

# -------------------------
# Analyze the cleaned values
# -------------------------
def analyze(values):
    results = {}
    for test_name, data in values.items():
        ref = reference_ranges.get(test_name)
        if not ref:
            continue

        val = data["value"]
        unit = data["unit"]
        for label, (low, high) in ref["ranges"].items():
            if low <= val < high:
                results[test_name] = {
                    "value": val,
                    "unit": unit,
                    "status": label.title(),
                    "advice": ref["advice"][label]
                }
                break
    return results

# -------------------------
# Wrapper function for backend use
# -------------------------
def analyze_report(report_text):
    cleaned = extract_values(report_text)
    return analyze(cleaned)

# -------------------------
# Generate PDF Report
# -------------------------
def export_to_pdf(results, filename="healthtrack_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="HealthTrack AI - Personalized Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for test, data in results.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"{test.title()}", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"Value: {data['value']} {data['unit']}", ln=True)
        pdf.cell(0, 10, txt=f"Status: {data['status']}", ln=True)

        # ✅ Encode to latin-1 safely to avoid Unicode crash
        safe_advice = data['advice'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=f"Advice: {safe_advice}", align='L')
        pdf.ln(5)

    pdf.output(filename)
    print(f"✅ PDF exported: {filename}")



