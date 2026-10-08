import sys
import unittest

def test_enterprise_cases():
    test_cases = [
        {
            "name": "Caso 1: Contrato Laboral / Prestación de Servicios",
            "text": "En Santiago, don Daniel Alejandro Trigo Tabilo, de profesión ingeniero civil, estado civil soltero, de 21 años, RUT 21.453.124-0, domiciliado en PASAJE MANUEL RODRIGUEZ 1490, comuna de Maipú, teléfono +56912345678, correo dtrigo@empresa.cl, honorarios de $1.500.000 pesos en la cuenta corriente 12345678 del Banco Santander.",
            "expected_entities": ["CL_RUT", "LOCATION", "AGE", "MARITAL_STATUS", "PROFESSION", "EMAIL_ADDRESS", "PHONE_NUMBER", "FINANCIAL_AMOUNT", "IBAN_CODE"]
        },
        {
            "name": "Caso 2: Poder Notarial y Representación Legal",
            "text": "Don Carlos Alberto Mendoza Silva, en su calidad de gerente general y representante legal de Inversiones Norte SpA, con pasaporte n° AB876543 y domicilio en Avenida Providencia 2340 depto 502, Providencia.",
            "expected_entities": ["ID_DOCUMENT", "LOCATION", "PROFESSION"]
        },
        {
            "name": "Caso 3: Ficha Clínica y Datos Personales",
            "text": "Paciente María José Gómez, de 34 años de edad, estado civil casada, con residencia en Calle Los Olivos 450, cel 987654321 y rut 16.789.012-K.",
            "expected_entities": ["CL_RUT", "LOCATION", "AGE", "MARITAL_STATUS", "PHONE_NUMBER"]
        },
        {
            "name": "Caso 4: Cláusula de Pago y Transferencia Bancaria",
            "text": "El pago por la suma de $850.000 se realizará mediante transferencia a la cuenta vista 9876543210 del Banco de Chile a nombre de Juan Pérez, rut 12.345.678-9.",
            "expected_entities": ["CL_RUT", "IBAN_CODE", "FINANCIAL_AMOUNT"]
        }
    ]

    print("=" * 70)
    print("EJECUTANDO SUITE DE TESTS: RECONOCIMIENTO EMPRESARIAL EN ESPAÑOL")
    print("=" * 70)

    try:
        from main import analyzer, anonymizer
    except Exception as e:
        print(f"Error al importar el analizador: {e}")
        return

    all_passed = True
    for case in test_cases:
        print(f"\n[TEST] {case['name']}")
        print(f"Texto original:\n  \"{case['text']}\"")
        
        results = analyzer.analyze(text=case["text"], language="es")
        anonymized = anonymizer.anonymize(text=case["text"], analyzer_results=results)
        
        detected_types = {r.entity_type for r in results}
        
        print(f"Texto anonimizado:\n  \"{anonymized.text}\"")
        print(f"Entidades detectadas: {sorted(list(detected_types))}")
        
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
