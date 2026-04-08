"""Token cost calculation tests."""
import pytest
from app import calculate_token_cost, get_firm_config

def test_minimax_m2_7_1m_tokens():
    cost = calculate_token_cost(1_000_000, 1_000_000, 'minimax-m2.7')
    assert abs(cost - 0.535) < 0.001  # 0.107 + 0.428

def test_minimax_m2_7_small():
    cost = calculate_token_cost(100_000, 50_000, 'minimax-m2.7')
    assert abs(cost - 0.0321) < 0.0001  # 0.107*0.1 + 0.428*0.05

def test_claude_opus_4():
    cost = calculate_token_cost(1_000_000, 1_000_000, 'claude-opus-4')
    assert abs(cost - 87.50) < 0.01  # 12.50 + 75.00

def test_unknown_model_falls_back_to_default():
    cost = calculate_token_cost(1_000_000, 1_000_000, 'unknown-model-xyz')
    cfg = get_firm_config()
    default_in = cfg['token_cost_rates']['default']['input_per_m']
    default_out = cfg['token_cost_rates']['default']['output_per_m']
    expected = (1_000_000 / 1_000_000) * default_in + (1_000_000 / 1_000_000) * default_out
    assert abs(cost - expected) < 0.001

def test_zero_tokens():
    cost = calculate_token_cost(0, 0, 'minimax-m2.7')
    assert cost == 0.0

def test_rates_from_firm_config():
    """Rates should come from firm_config, not hardcoded."""
    cfg = get_firm_config()
    assert 'token_cost_rates' in cfg
    assert 'minimax-m2.7' in cfg['token_cost_rates']
    assert 'input_per_m' in cfg['token_cost_rates']['minimax-m2.7']
    assert 'output_per_m' in cfg['token_cost_rates']['minimax-m2.7']
