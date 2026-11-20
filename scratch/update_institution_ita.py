import os
import glob

replacements = [
    ("UNIVERSIDAD AUTÓNOMA DE TLAXCALA", "TECNOLÓGICO NACIONAL DE MÉXICO — INSTITUTO TECNOLÓGICO DE APIZACO"),
    ("Universidad Autónoma de Tlaxcala (UATx)", "Instituto Tecnológico de Apizaco (TecNM Campus Apizaco)"),
    ("Universidad Autónoma de Tlaxcala", "Instituto Tecnológico de Apizaco (TecNM)"),
    ("FACULTAD DE CIENCIAS BÁSICAS, INGENIERÍA Y TECNOLOGÍA", "DEPARTAMENTO DE SISTEMAS Y COMPUTACIÓN"),
    ("Facultad de Ciencias Básicas, Ingeniería y Tecnología", "Departamento de Sistemas y Computación"),
    ("Campus San Luis Apizaquito / Tlaxcala, Tlax., México", "Apizaco, Tlaxcala, México"),
    ("r.almendra@alumnos.uatx.mx", "r.almendra@apizaco.tecnm.mx"),
    ("rodrigo.almendra.uatx@gmail.com", "rodrigo.almendra.ita@gmail.com"),
    ("PAC_DEMO_UATX", "PAC_DEMO_ITA"),
    ("1-ARTSPACE-DEMO-UATX-EQ3", "1-ARTSPACE-DEMO-ITA-EQ3"),
    ("artspace-demo-unidad4-ingenieria-uatx", "artspace-demo-unidad4-ingenieria-ita"),
    ("UATx", "Instituto Tecnológico de Apizaco"),
    ("UATX", "ITA"),
    ("uatx", "ita")
]

target_files = (
    glob.glob("pagina/*.md") +
    glob.glob("pagina/*.py") +
    glob.glob("templates/*.html") +
    glob.glob("gallery/*.py") +
    glob.glob("artspace_project/*.py") +
    ["demo_flujo_completo.py", "test_auth_suite.py"]
)

updated_count = 0
for filepath in target_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content
    for old_str, new_str in replacements:
        new_content = new_content.replace(old_str, new_str)
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✓ Actualizado: {filepath}")
        updated_count += 1

print(f"\nTotal de archivos actualizados al Instituto Tecnológico de Apizaco: {updated_count}")

