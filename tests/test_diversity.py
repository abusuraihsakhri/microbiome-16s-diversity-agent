"""Regression tests for actual descriptive microbiome diversity metrics."""
import csv
import math
from pathlib import Path

import pytest
from microbiome_mind.diversity import read_count_table, analyse_counts
from diversity_cli import main


def test_known_alpha_beta_values(tmp_path):
    f = tmp_path / 'counts.csv'
    f.write_text('sample_id,A,B,C\ncontrol,5,5,0\nexposed,10,0,0\n', encoding='utf8')
    result = analyse_counts(read_count_table(f))
    assert result['alpha'][0]['shannon'] == pytest.approx(math.log(2))
    assert result['alpha'][0]['simpson'] == pytest.approx(0.5)
    assert result['alpha'][0]['evenness'] == pytest.approx(1)
    assert result['alpha'][0]['chao1'] == pytest.approx(2)
    assert result['beta'][0] == pytest.approx([0, 0.5])
    assert result['beta'][1] == pytest.approx([0.5, 0])
    assert result['sample_names'] == ['control', 'exposed']


def test_chao1_singletons_and_depth_normalized_beta(tmp_path):
    f = tmp_path / 'counts.csv'
    f.write_text('sample_id,A,B,C\na,1,1,2\nb,10,10,20\n', encoding='utf8')
    r = analyse_counts(read_count_table(f))
    assert r['alpha'][0]['chao1'] == pytest.approx(3.5)
    assert r['beta'][0][1] == pytest.approx(0)


@pytest.mark.parametrize('csvtext', [
    '', 'sample_id,A\n', 'feature,A\ns,1', 'sample_id,A,A\ns,1,2',
    'sample_id,A\ns,0', 'sample_id,A\ns,NaN', 'sample_id,A\ns,-1',
    'sample_id,A\ns,1.5', 'sample_id,A\ns,', 'sample_id,A\ns,2\ns,3',
    'sample_id,A\ns,1,2',
])
def test_bad_csv_rejected(tmp_path, csvtext):
    f = tmp_path / 'counts.csv'
    f.write_text(csvtext, encoding='utf8')
    with pytest.raises(ValueError):
        read_count_table(f)


def test_cli_exports(tmp_path):
    f = tmp_path / 'in.csv'
    f.write_text('sample_id,A,B\n"=1+1",1,2\ns2,3,4\n', encoding='utf8')
    a, b = tmp_path / 'alpha.csv', tmp_path / 'beta.csv'
    assert main([str(f), '--alpha', str(a), '--beta', str(b)]) == 0
    with a.open(newline='') as stream:
        row = list(csv.DictReader(stream))[0]
        assert row['sample_id'] == "'=1+1"
        assert float(row['shannon']) > 0
    with b.open(newline='') as stream:
        rows = list(csv.reader(stream))
        assert rows[1][1] == '0.0'
