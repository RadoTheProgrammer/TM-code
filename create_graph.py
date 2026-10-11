import math
import re
from pathlib import Path

import pandas as pd

from utils import settings_data


ENVIE_COLORS = {1: "green", 2: "blue", 3: "red"}


def dot_quote(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def format_limit(value):
    if pd.isna(value):
        return "not set"
    number = float(value)
    return str(int(number)) if number.is_integer() else str(number)


def parse_envies(value, context):
    if pd.isna(value):
        raise ValueError(f"Missing envies for {context}")

    envies = {int(match) for match in re.findall(r"\d+", str(value))}
    if not envies or not envies.issubset(ENVIE_COLORS):
        raise ValueError(f"Invalid envies {value!r} for {context}; expected values 1, 2, or 3")
    return sorted(envies)


def format_tm_label(tm_id, tm):
    title = tm.get("Titre", tm.get("Maître c", tm.get("Maitre c", "")))
    title = "" if pd.isna(title) else str(title).strip()
    minimum = format_limit(tm.get("Nombre minimal travaux", float("nan")))
    maximum = format_limit(tm.get("Nombre maximal travaux", float("nan")))
    label = f"TM {tm_id}"
    if title:
        label += f"\n{title}"
    return f"{label}\nMin: {minimum} | Max: {maximum}"


def create_dot():
    grid = pd.read_csv(settings_data["GRID_FILE"], index_col=0)
    grid.index = grid.index.astype(str)
    grid.columns = grid.columns.astype(str)

    tms = pd.read_csv(settings_data["TM_FILE"], index_col=0)
    tms.index = tms.index.astype(str)

    duos = pd.read_csv(settings_data["DUO_FILE"], dtype=str)
    tm_ids = list(dict.fromkeys([*grid.columns, *tms.index]))
    students = list(dict.fromkeys(grid.index.astype(str)))

    duo_records = {}
    for row_number, duo in duos.iterrows():
        members = [member.strip() for member in duo["Eleves"].split(" + ")]
        if len(members) != 2 or not all(members):
            raise ValueError(f"Invalid duo on CSV row {row_number + 2}: {duo['Eleves']!r}")

        key = tuple(sorted(members))
        if key not in duo_records:
            duo_records[key] = {"members": members, "choices": {}}

        tm_id = str(duo["Choix"]).strip()
        if tm_id not in tm_ids:
            tm_ids.append(tm_id)
        envies = parse_envies(duo["Envies"], f"duo {duo['Eleves']} and TM {tm_id}")
        choice_envies = duo_records[key]["choices"].setdefault(tm_id, set())
        choice_envies.update(envies)
        for member in members:
            if member not in students:
                students.append(member)

    lines = [
        "digraph TMPreferences {",
        "  graph [rankdir=LR, overlap=false, splines=true];",
        '  node [fontname="Arial"];',
        '  edge [fontname="Arial", fontsize=9, dir=none];',
        "",
        '  subgraph cluster_tms {',
        '    label="Travaux de maturite";',
        '    color="lightgrey";',
    ]

    for tm_id in tm_ids:
        tm = tms.loc[tm_id] if tm_id in tms.index else pd.Series(dtype=object)
        lines.append(
            f"    {dot_quote('tm_' + tm_id)} "
            f"[shape=box, style=filled, fillcolor=lightgoldenrod1, "
            f"label={dot_quote(format_tm_label(tm_id, tm))}];"
        )
    lines.extend(["  }", "", '  subgraph cluster_students {', '    label="Eleves";', '    color="lightgrey";'])
    for student in students:
        lines.append(f"    {dot_quote('student_' + student)} [shape=ellipse, label={dot_quote(student)}];")
    lines.extend(["  }", "", '  subgraph cluster_duos {', '    label="Duos";', '    color="lightgrey";'])
    for duo_number, (key, record) in enumerate(duo_records.items(), start=1):
        record["node_id"] = f"duo_{duo_number}"
        duo_label = " + ".join(record["members"])
        duo_label = f"Duo\n{duo_label}"
        lines.append(
            f"    {dot_quote(record['node_id'])} "
            f"[shape=diamond, style=filled, fillcolor=lightcyan, "
            f"label={dot_quote(duo_label)}];"
        )
    lines.extend(["  }", ""])

    for student in students:
        if student not in grid.index:
            continue
        for tm_id in grid.columns:
            value = grid.at[student, tm_id]
            if pd.isna(value):
                continue
            try:
                envie_value = float(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid envie {value!r} for student {student} and TM {tm_id}") from error
            if not math.isfinite(envie_value) or not envie_value.is_integer():
                raise ValueError(f"Invalid envie {value!r} for student {student} and TM {tm_id}")
            envie = int(envie_value)
            if envie not in ENVIE_COLORS:
                raise ValueError(f"Invalid envie {value!r} for student {student} and TM {tm_id}")
            lines.append(
                f"  {dot_quote('student_' + student)} -> {dot_quote('tm_' + tm_id)} "
                f"[color={dot_quote(ENVIE_COLORS[envie])}, tooltip={dot_quote('Envie ' + str(envie))}];"
            )

    for record in duo_records.values():
        duo_node = record["node_id"]
        for member in record["members"]:
            lines.append(f"  {dot_quote(duo_node)} -> {dot_quote('student_' + member)} [color=grey50];")
        for tm_id, envies in record["choices"].items():
            colors = ":".join(ENVIE_COLORS[envie] for envie in sorted(envies))
            envie_label = " / ".join(str(envie) for envie in sorted(envies))
            lines.append(
                f"  {dot_quote(duo_node)} -> {dot_quote('tm_' + tm_id)} "
                f"[color={dot_quote(colors)}, label={dot_quote('Envie ' + envie_label)}];"
            )

    legend_lines = ["Preferences:", "Envie 1 = green", "Envie 2 = blue", "Envie 3 = red", "", "TM min / max:"]
    for tm_id in tm_ids:
        tm = tms.loc[tm_id] if tm_id in tms.index else pd.Series(dtype=object)
        legend_lines.append(
            f"TM {tm_id}: min {format_limit(tm.get('Nombre minimal travaux', float('nan')))}, "
            f"max {format_limit(tm.get('Nombre maximal travaux', float('nan')))}"
        )
    lines.extend(
        [
            "",
            f"  legend [shape=note, label={dot_quote(chr(10).join(legend_lines))}];",
            "}",
            "",
        ]
    )

    output_path = Path(settings_data["GRID_FILE"]).with_suffix(".dot")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    print(f"DOT graph written to {create_dot()}")
