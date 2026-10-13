import sys
import unittest

def test_enterprise_cases():
    test_cases = [
        {
            "name": "Caso 1: Contrato Laboral / Prestación de Servicios",
            "text": "En Santiago, don Daniel Alejandro Trigo Tabilo, de profesión ingeniero civil, estado civil soltero, de 21 años, RUT 21.453.124-0, domiciliado en PASAJE MANUEL RODRIGUEZ 1490, comuna de Maipú, teléfono +56912345678, correo dtrigo@empresa.cl, honorarios de $1.500.000 pesos en la cuenta corriente 12345678 del Banco Santander.",
            "expected_entities": [
                "RUT", "DIRECCION", "EDAD", "ESTADO_CIVIL", "CARGO_O_PROFESION",
                "CORREO_ELECTRONICO", "TELEFONO", "MONTO_FINANCIERO", "CUENTA_BANCARIA",
                "ENTIDAD_BANCARIA", "PERSONA"
            ]
        },
        {
            "name": "Caso 2: Poder Notarial y Representación Legal",
            "text": "Don Carlos Alberto Mendoza Silva, en su calidad de gerente general y representante legal de Inversiones Norte SpA, con pasaporte n° AB876543 y domicilio en Avenida Providencia 2340 depto 502, Providencia.",
            "expected_entities": [
                "DOCUMENTO_IDENTIDAD", "DIRECCION", "CARGO_O_PROFESION", "EMPRESA", "PERSONA"
            ]
        },
        {
            "name": "Caso 3: Ficha Clínica y Datos Personales",
            "text": "Paciente María José Gómez, de 34 años de edad, estado civil casada, con residencia en Calle Los Olivos 450, cel 987654321 y rut 16.789.012-K.",
            "expected_entities": [
                "RUT", "DIRECCION", "EDAD", "ESTADO_CIVIL", "TELEFONO", "PERSONA"
            ]
        },
        {
            "name": "Caso 4: Cláusula de Pago y Transferencia Bancaria",
            "text": "El pago por la suma de $850.000 se realizará mediante transferencia a la cuenta vista 9876543210 del Banco de Chile a nombre de Juan Pérez, rut 12.345.678-9.",
            "expected_entities": [
                "RUT", "CUENTA_BANCARIA", "MONTO_FINANCIERO", "ENTIDAD_BANCARIA", "PERSONA"
            ]
        },
        {
            "name": "Caso 5: Cédula de Identidad con Rótulo Documental (Sin Solapamientos)",
            "text": "Comparece don Esteban Morales, con Cédula de Identidad N° 15.342.119-4, domiciliado en calle Las Lilas 890, comuna de Ñuñoa.",
            "expected_entities": [
                "PERSONA", "RUT", "DIRECCION"
            ]
        }
    ]

    print("=" * 70)
    print("EJECUTANDO SUITE DE TESTS: RECONOCIMIENTO EMPRESARIAL EN ESPAÑOL")
    print("=" * 70)

    try:
        from main import analyzer, anonymizer
        from enterprise_recognizers import refine_and_translate_entities
    except Exception as e:
        print(f"Error al importar el analizador: {e}")
        return

    all_passed = True
    for case in test_cases:
        print(f"\n[TEST] {case['name']}")
        print(f"Texto original:\n  \"{case['text']}\"")
        
        raw_results = analyzer.analyze(text=case["text"], language="es")
        results = refine_and_translate_entities(raw_results, case["text"])
        anonymized = anonymizer.anonymize(text=case["text"], analyzer_results=results)
        
        detected_types = {r.entity_type for r in results}
        
        print(f"Texto anonimizado:\n  \"{anonymized.text}\"")
        print(f"Entidades detectadas en español: {sorted(list(detected_types))}")
        
        # Validar si las entidades clave fueron detectadas
        missing = [ent for ent in case["expected_entities"] if ent not in detected_types]
        if missing:
            print(f"  ⚠️  Advertencia: No se detectaron las siguientes entidades esperadas: {missing}")
            all_passed = False
        else:
            print("  ✅ Todas las entidades clave esperadas fueron detectadas con éxito.")

    print("\n" + "=" * 70)
    if all_passed:
        print("RESULTADO: TODOS LOS TESTS PASARON EXITOSAMENTE.")
    else:
        print("RESULTADO: ALGUNOS CASOS REQUIEREN REVISIÓN.")
    print("=" * 70)

if __name__ == "__main__":
    test_enterprise_cases()
