import unittest
from pathlib import Path
from collections import Counter
from analisis_unificado import (
    _procesar_linea_buffer,
    analizar_logs,
    guardar_errores_csv,
    mostrar_estadisticas_estados,
    graficar_estadisticas_estados,
    guardar_estadisticas_estados_csv
)

class TestAnalisisUnificado(unittest.TestCase):

    def test_procesar_linea_buffer_err(self):
        buffer = ["01/01/2024 12:00:00.000 | a | b | c | ERR | CAJA1 | MOD1 | FLUJO1 | Mensaje de error"]
        total_estados = Counter()
        errores = []
        _procesar_linea_buffer(buffer, total_estados, errores)
        self.assertEqual(total_estados['ERR'], 1)
        self.assertEqual(len(errores), 1)
        self.assertIn("Mensaje de error", errores[0])

    def test_procesar_linea_buffer_inf(self):
        buffer = ["01/01/2024 12:00:00.000 | a | b | c | INF | CAJA1 | MOD1 | FLUJO1 | Mensaje info"]
        total_estados = Counter()
        errores = []
        _procesar_linea_buffer(buffer, total_estados, errores)
        self.assertEqual(total_estados['INF'], 1)
        self.assertEqual(len(errores), 0)

    def test_analizar_logs_empty(self):
        # Crea un archivo temporal vacío
        temp_log = Path("temp_test.log")
        temp_log.write_text("")
        estados, errores = analizar_logs([temp_log])
        self.assertEqual(sum(estados.values()), 0)
        self.assertEqual(len(errores), 0)
        temp_log.unlink()

    def test_guardar_errores_csv(self):
        errores = [
            "01/01/2024 12:00:00.000 | a | b | c | ERR | CAJA1 | MOD1 | FLUJO1 | Mensaje de error"
        ]
        carpeta = Path("resultados_test")
        carpeta.mkdir(exist_ok=True)
        archivo = guardar_errores_csv(errores, carpeta)
        self.assertTrue(archivo.exists())
        contenido = archivo.read_text(encoding="utf-8")
        self.assertIn("Mensaje de error", contenido)
        archivo.unlink()
        carpeta.rmdir()

if __name__ == '__main__':
    unittest.main()