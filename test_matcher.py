import unittest
from datetime import date

from matcher import classify, contains_term, normalize, score_job
from profile_parser import estimate_years, parse_profile

SKILLS = [
    {"name": "Oracle EBS", "weight": 3, "aliases": ["oracle ebs", "e-business suite"]},
    {"name": "SAP", "weight": 1, "aliases": ["sap"]},
]


class MatcherTest(unittest.TestCase):

    def test_coincide_palabra_completa(self):
        texto = normalize("Experto en SAP y Oracle E-Business Suite")
        self.assertTrue(contains_term(texto, "sap"))
        self.assertTrue(contains_term(texto, "e-business suite"))
        self.assertFalse(contains_term(normalize("Homo sapiens"), "sap"))

    def test_puntaje_ponderado(self):
        resultado = score_job("Consultor de Oracle EBS", SKILLS)
        self.assertEqual(resultado["score"], 75)
        self.assertEqual(resultado["matched"], ["Oracle EBS"])
        self.assertEqual(resultado["missing"], ["SAP"])

    def test_clasificacion_por_umbral(self):
        self.assertEqual(classify({"A": {"score": 60}, "B": {"score": 20}}, 40), "A")
        self.assertEqual(classify({"A": {"score": 60}, "B": {"score": 45}}, 40), "Both")
        self.assertEqual(classify({"A": {"score": 30}, "B": {"score": 20}}, 40), "Neither")


class ProfileParserTest(unittest.TestCase):

    def test_datos_del_perfil(self):
        texto = "Ana Gómez\nBusiness Analyst\nUruguay\n\nEXPERIENCE\nAnalyst\nJan 2018 - Dec 2020\nLead\nJan 2021 - Present\n"
        perfil = parse_profile(texto, today=date(2026, 1, 1))
        self.assertEqual(perfil["name"], "Ana Gómez")
        self.assertEqual(perfil["headline"], "Business Analyst")
        self.assertEqual(perfil["location"], "Uruguay")
        self.assertEqual(perfil["years"], 8.0)

    def test_sin_fechas(self):
        self.assertIsNone(estimate_years("Perfil sin fechas"))


if __name__ == "__main__":
    unittest.main()
