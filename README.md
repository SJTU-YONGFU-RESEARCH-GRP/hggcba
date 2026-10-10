# hggcba

**Hierarchical Group-Generate Carry-Bypass Adder**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green?logo=creativecommons&logoColor=white)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab.svg)](https://www.python.org/downloads/)

This repository contains the HGGCBA design: a parameterized Verilog adder and a Python model of the same block group-generate / propagate-bypass carry policy.

Each block of `BLOCK_SIZE` bits computes a block-propagate term `P_k` and a group-generate term `G_k`. The carry into the next block is

```text
C_{k+1} = G_k | (P_k & C_k)
```

Sum bits inside the block use local ripple recursion from the incoming carry. The Python model and the RTL are checked against integer addition.

## Layout

```text
hggcba/
├── rtl/hierarchical_gb_adder.v
├── tb/tb_hierarchical_gb_adder.v
├── src/hggcba/model_hierarchical_gb_adder.py
└── tests/test_model_hierarchical_gb_adder.py
```

## Python model

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## RTL simulation

```bash
iverilog -g2012 -o /tmp/tb_hggcba \
  rtl/hierarchical_gb_adder.v tb/tb_hierarchical_gb_adder.v
vvp /tmp/tb_hggcba
```

## Citation

This work has been accepted by APCCAS 2026. If you use this repository in academic work, please cite the paper below. Proceedings pages and a DOI are not yet assigned.

```bibtex
@inproceedings{Wang2026APCCAS,
  author    = {Wang, Chao and Du, Haochen and Cheah, Kian Kit and Hou, Yuting and Li, Yongfu},
  title     = {Hierarchical Group-Generate Carry-Bypass Adder: A Physically Scalable and Efficient Topology for Ultra-Wide Datapaths},
  booktitle = {IEEE Asia Pacific Conference on Circuits and Systems (APCCAS)},
  year      = {2026},
  address   = {Fukuoka, Japan},
  month     = oct,
  note      = {accepted; open implementation: \url{https://github.com/SJTU-YONGFU-RESEARCH-GRP/hggcba}}
}
```

```bibtex
@software{hggcba,
  title   = {hggcba: Hierarchical Group-Generate Carry-Bypass Adder},
  author  = {Wang, Chao and Du, Haochen and Cheah, Kian Kit and Hou, Yuting and Li, Yongfu},
  year    = {2026},
  url     = {https://github.com/SJTU-YONGFU-RESEARCH-GRP/hggcba},
  license = {CC-BY-4.0}
}
```

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
