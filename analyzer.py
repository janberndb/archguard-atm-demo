#!/usr/bin/env python3
import json, pathlib, ast, os, xml.etree.ElementTree as ET, sys

# --- Modell laden von JSON statt YAML ---
model = json.load(open("architecture.json"))
layers_rules = {k:v['allowed'] for k,v in model['logical']['layers'].items()}
comp_map = {c['folder']: c['layer'] for c in model['development']['components']}

def layer_of(path):
    rel = str(path).replace('\\','/')
    for pattern, layer in comp_map.items():
        if pathlib.Path(rel).match(pattern):
            return layer
    return "Unknown"

deps, violations = [], []
for py in pathlib.Path("atm").rglob("*.py"):
    tree = ast.parse(open(py).read())
    imports = [n.names[0].name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import)]
    src_layer = layer_of(py)
    for imp in imports:
        tgt_path = py.with_name(imp + ".py")
        tgt_layer = layer_of(tgt_path)
        deps.append((src_layer, tgt_layer, py.name, imp))
        if tgt_layer not in layers_rules.get(src_layer, []):
            violations.append((src_layer, tgt_layer, py.name, imp))

print(f"[ArchGuard] Analysierte {len(deps)} Import-Kanten")
if violations:
    print(f"[ArchGuard] ❌ {len(violations)} Verstöße gefunden:")
    for v in violations:
        print(f"   ✗ {v[2]} ({v[0]}) → {v[3]} ({v[1]})")
    exit_code = 1
else:
    print("[ArchGuard] ✅ Keine Verstöße gefunden.")
    exit_code = 0

os.makedirs("tests-results", exist_ok=True)
suite = ET.Element("testsuite", name="ArchGuard", tests=str(len(deps)), failures=str(len(violations)))
for d in deps:
    case = ET.SubElement(suite,"testcase", classname=d[0], name=f"{d[2]} -> {d[3]}")
    if d in violations:
        fail = ET.SubElement(case,"failure", message="Layer breach")
        fail.text = f"{d[2]} imports {d[3]} ({d[0]}→{d[1]} not allowed)"
ET.ElementTree(suite).write("tests-results/archguard.xml")

html = ["<h2>ArchGuard Report</h2>","<pre>"]
for d in deps:
    mark = "✗" if d in violations else "✓"
    html.append(f"{mark} {d[2]} → {d[3]} ({d[0]}→{d[1]})")
html += ["</pre>","<h3>Dependency graph</h3>","<pre class='mermaid'>graph LR"]
for d in deps:
    html.append(f"  {d[2]}[{d[2]}\n({d[0]})] --> {d[3]}[{d[3]}\n({d[1]})]")
html.append("</pre>")
open("archguard_report.html","w").write("\n".join(html))

sys.exit(exit_code)
