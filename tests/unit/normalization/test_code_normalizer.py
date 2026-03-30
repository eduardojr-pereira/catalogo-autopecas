import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.processing.normalization.code_normalizer import (
    normalize_code,
    codes_are_equal,
)


# ------------------------------------------------------
# TESTE 1
# Normalização de código com hífen
# ------------------------------------------------------
def test_normalize_code_with_hyphen():
    """
    Verifica se o normalizador remove hífens corretamente.
    """

    result = normalize_code("15400-RTA-003")

    assert result == "15400RTA003"


# ------------------------------------------------------
# TESTE 2
# Normalização de código com espaços
# ------------------------------------------------------
def test_normalize_code_with_spaces():
    """
    Verifica se o normalizador remove espaços corretamente.
    """

    result = normalize_code("15400 RTA 003")

    assert result == "15400RTA003"


# ------------------------------------------------------
# TESTE 3
# Normalização de código em minúsculas
# ------------------------------------------------------
def test_normalize_code_lowercase():
    """
    Verifica se o normalizador converte letras minúsculas
    para maiúsculas.
    """

    result = normalize_code("oc-1196")

    assert result == "OC1196"


# ------------------------------------------------------
# TESTE 4
# Normalização com espaços no início e no fim
# ------------------------------------------------------
def test_normalize_code_with_outer_spaces():
    """
    Verifica se o normalizador remove espaços externos.
    """

    result = normalize_code("  15400-RTA-003  ")

    assert result == "15400RTA003"


# ------------------------------------------------------
# TESTE 5
# Comparação entre códigos equivalentes
# ------------------------------------------------------
def test_codes_are_equal_true():
    """
    Verifica se dois códigos iguais em formatos diferentes
    são reconhecidos como equivalentes.
    """

    result = codes_are_equal("OC-1196", "oc1196")

    assert result is True


# ------------------------------------------------------
# TESTE 6
# Comparação entre códigos diferentes
# ------------------------------------------------------
def test_codes_are_equal_false():
    """
    Verifica se dois códigos realmente diferentes
    não são considerados iguais.
    """

    result = codes_are_equal("OC-1196", "OC-1197")

    assert result is False


# ------------------------------------------------------
# TESTE 7
# Entrada nula
# ------------------------------------------------------
def test_normalize_code_none():
    """
    Verifica o comportamento quando o código é None.
    """

    result = normalize_code(None)

    assert result is None