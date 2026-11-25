import os
import sys
import json
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_BANK_FILE = os.path.join(BASE_DIR, "question_bank.json")
HISTORY_FILE = os.path.join(BASE_DIR, "quiz_history.json")
TODAY_FILE = os.path.join(BASE_DIR, "today_questions.json")

# Sample starter bank of high-yield Class 12 NCERT questions for CUET PCB
DEFAULT_BANK = [
    # --- BIOLOGY ---
    {
        "id": "BIO-001",
        "subject": "Biology",
        "chapter": "Sexual Reproduction in Flowering Plants",
        "question": "The filiform apparatus is a characteristic feature of which cell in the embryo sac?",
        "options": ["Antipodal cells", "Synergids", "Egg cell", "Central cell"],
        "correct_option_id": 1,
        "explanation": "Filiform apparatus is present at the micropylar end of synergids and guides entry of pollen tube (NCERT Class 12 Biology, Ch-1)."
    },
    {
        "id": "BIO-002",
        "subject": "Biology",
        "chapter": "Human Reproduction",
        "question": "Which hormone causes the rupture of Graafian follicle leading to ovulation?",
        "options": ["Progesterone", "FSH", "LH surge", "Estrogen"],
        "correct_option_id": 2,
        "explanation": "Rapid secretion of LH leading to maximum level (LH surge) induces rupture of Graafian follicle (NCERT Class 12 Biology, Ch-2)."
    },
    {
        "id": "BIO-003",
        "subject": "Biology",
        "chapter": "Principles of Inheritance & Variation",
        "question": "In ABO blood grouping, how many genotypes and phenotypes are possible in the human population?",
        "options": ["4 genotypes, 6 phenotypes", "6 genotypes, 4 phenotypes", "3 genotypes, 3 phenotypes", "6 genotypes, 6 phenotypes"],
        "correct_option_id": 1,
        "explanation": "Three alleles (IA, IB, i) produce 6 genotypes and 4 phenotypic blood groups: A, B, AB, and O (NCERT Class 12 Biology, Ch-4)."
    },
    {
        "id": "BIO-004",
        "subject": "Biology",
        "chapter": "Molecular Basis of Inheritance",
        "question": "Which enzyme catalyzes the transcription of hnRNA (precursor of mRNA) in eukaryotes?",
        "options": ["RNA Polymerase I", "RNA Polymerase II", "RNA Polymerase III", "DNA Ligase"],
        "correct_option_id": 1,
        "explanation": "RNA Polymerase II transcribes the precursor of mRNA (hnRNA) in eukaryotes (NCERT Class 12 Biology, Ch-5)."
    },
    {
        "id": "BIO-005",
        "subject": "Biology",
        "chapter": "Biotechnology: Principles & Processes",
        "question": "The specific sequence recognized by restriction endonuclease EcoRI is:",
        "options": ["5'-GAATTC-3'", "5'-GGATCC-3'", "5'-AAGCTT-3'", "5'-CTGCAG-3'"],
        "correct_option_id": 0,
        "explanation": "EcoRI recognizes the palindromic hexanucleotide sequence 5'-GAATTC-3' and cuts between G and A (NCERT Class 12 Biology, Ch-9)."
    },
    {
        "id": "BIO-006",
        "subject": "Biology",
        "chapter": "Ecology & Biodiversity",
        "question": "According to Robert May, what is the estimated global species diversity on Earth?",
        "options": ["1.7 million", "7 million", "20 to 50 million", "100 million"],
        "correct_option_id": 1,
        "explanation": "Robert May places the global species diversity at about 7 million (NCERT Class 12 Biology, Ch-12)."
    },

    # --- CHEMISTRY ---
    {
        "id": "CHEM-001",
        "subject": "Chemistry",
        "chapter": "Solutions",
        "question": "Which of the following colligative properties is most commonly used to determine molecular mass of polymers and proteins?",
        "options": ["Relative lowering of vapour pressure", "Osmotic pressure", "Elevation in boiling point", "Depression in freezing point"],
        "correct_option_id": 1,
        "explanation": "Osmotic pressure is measured at room temperature and biomolecules are unstable at high temperatures (NCERT Class 12 Chemistry, Ch-1)."
    },
    {
        "id": "CHEM-002",
        "subject": "Chemistry",
        "chapter": "Electrochemistry",
        "question": "The unit of molar conductivity (Λm) in SI units is:",
        "options": ["S m² mol⁻¹", "S m⁻¹ mol⁻¹", "S cm mol⁻¹", "ohm⁻¹ m⁻² mol"],
        "correct_option_id": 0,
        "explanation": "Molar conductivity has the SI units S m² mol⁻¹ (or S cm² mol⁻¹) (NCERT Class 12 Chemistry, Ch-2)."
    },
    {
        "id": "CHEM-003",
        "subject": "Chemistry",
        "chapter": "Chemical Kinetics",
        "question": "For a zero-order reaction A -> Products, the half-life (t₁/₂) is directly proportional to:",
        "options": ["Initial concentration [A]₀", "Square of [A]₀", "1 / [A]₀", "Independent of [A]₀"],
        "correct_option_id": 0,
        "explanation": "For zero-order, t₁/₂ = [A]₀ / (2k), so half-life is directly proportional to initial concentration (NCERT Class 12 Chemistry, Ch-3)."
    },
    {
        "id": "CHEM-004",
        "subject": "Chemistry",
        "chapter": "Coordination Compounds",
        "question": "According to Crystal Field Theory, in an octahedral complex, the eg orbitals have energy:",
        "options": ["Lower than average by 0.4 Δo", "Higher than average by 0.6 Δo", "Equal to t2g orbitals", "Higher by 1.2 Δo"],
        "correct_option_id": 1,
        "explanation": "In octahedral crystal field splitting, eg orbitals (dx²-y², dz²) are raised in energy by +0.6 Δo (NCERT Class 12 Chemistry, Ch-5)."
    },
    {
        "id": "CHEM-005",
        "subject": "Chemistry",
        "chapter": "Haloalkanes and Haloarenes",
        "question": "The SN1 mechanism of substitution reaction is accompanied by:",
        "options": ["Complete inversion of configuration", "Complete retention of configuration", "Racemization", "No stereochemical change"],
        "correct_option_id": 2,
        "explanation": "SN1 involves a planar carbocation intermediate allowing attack from both sides, yielding racemization (NCERT Class 12 Chemistry, Ch-6)."
    },

    # --- PHYSICS ---
    {
        "id": "PHY-001",
        "subject": "Physics",
        "chapter": "Electric Charges and Fields",
        "question": "The electric flux through a closed Gaussian surface enclosing an electric dipole of dipole moment p is:",
        "options": ["p / ε₀", "2p / ε₀", "Zero", "p / (4πε₀)"],
        "correct_option_id": 2,
        "explanation": "Net enclosed charge for a dipole is (+q - q) = 0. By Gauss's Law, total electric flux = q_net / ε₀ = 0 (NCERT Class 12 Physics, Ch-1)."
    },
    {
        "id": "PHY-002",
        "subject": "Physics",
        "chapter": "Current Electricity",
        "question": "On increasing temperature, the resistivity of a typical semiconductor:",
        "options": ["Increases linearly", "Decreases exponentially", "Remains constant", "First increases then decreases"],
        "correct_option_id": 1,
        "explanation": "In semiconductors, charge carrier density (n) increases exponentially with temperature, decreasing resistivity (NCERT Class 12 Physics, Ch-3)."
    },
    {
        "id": "PHY-003",
        "subject": "Physics",
        "chapter": "Moving Charges and Magnetism",
        "question": "A charged particle moves perpendicular to a uniform magnetic field. Which quantity remains constant?",
        "options": ["Velocity only", "Speed and Kinetic Energy", "Momentum only", "Acceleration"],
        "correct_option_id": 1,
        "explanation": "Magnetic force is perpendicular to velocity (F = q(v x B)), so work done is zero. Speed and kinetic energy remain constant (NCERT Class 12 Physics, Ch-4)."
    },
    {
        "id": "PHY-004",
        "subject": "Physics",
        "chapter": "Ray Optics & Optical Instruments",
        "question": "When a light ray travels from a denser medium to a rarer medium at an angle of incidence greater than the critical angle, the phenomenon is:",
        "options": ["Total internal reflection", "Diffraction", "Polarization", "Dispersion"],
        "correct_option_id": 0,
        "explanation": "When i > ic travelling denser to rarer, the entire light reflects back into the denser medium (TIR) (NCERT Class 12 Physics, Ch-9)."
    },
    {
        "id": "PHY-005",
        "subject": "Physics",
        "chapter": "Dual Nature of Radiation & Matter",
        "question": "The de Broglie wavelength of an electron accelerated through potential difference V is approximately:",
        "options": ["12.27 / √V Å", "1.227 / V Å", "122.7 / √V Å", "0.1227 / √V Å"],
        "correct_option_id": 0,
        "explanation": "λ = h / √(2m e V) ≈ 1.227 / √V nm = 12.27 / √V Å (NCERT Class 12 Physics, Ch-11)."
    }
]

def load_bank():
    if os.path.exists(QUESTIONS_BANK_FILE):
        try:
            with open(QUESTIONS_BANK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Save default bank
    with open(QUESTIONS_BANK_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_BANK, f, indent=2, ensure_ascii=False)
    return DEFAULT_BANK

def select_10_questions():
    bank = load_bank()
    
    # Separate by subject
    phys = [q for q in bank if q.get("subject") == "Physics"]
    chem = [q for q in bank if q.get("subject") == "Chemistry"]
    bio = [q for q in bank if q.get("subject") == "Biology"]

    # Load history to minimize repeats
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    recent_ids = set(history[-30:])

    def pick_n(pool, n):
        non_recent = [q for q in pool if q["id"] not in recent_ids]
        if len(non_recent) >= n:
            chosen = random.sample(non_recent, n)
        else:
            chosen = list(non_recent)
            remaining = [q for q in pool if q not in chosen]
            if remaining:
                chosen += random.sample(remaining, min(n - len(chosen), len(remaining)))
        return chosen

    # Pick 3 Physics, 3 Chemistry, 4 Biology = 10 questions
    chosen_phys = pick_n(phys, 3)
    chosen_chem = pick_n(chem, 3)
    chosen_bio = pick_n(bio, 4)

    selected = chosen_phys + chosen_chem + chosen_bio
    random.shuffle(selected)

    # Save today's selected questions
    with open(TODAY_FILE, "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2, ensure_ascii=False)

    # Update history
    new_ids = [q["id"] for q in selected]
    history.extend(new_ids)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-100:], f, indent=2)

    return selected

def main():
    selected = select_10_questions()
    print(f"Selected {len(selected)} PCB questions for today.")

    # Import send_quiz and post
    import send_quiz
    send_quiz.post_quiz(TODAY_FILE)

if __name__ == "__main__":
    main()
