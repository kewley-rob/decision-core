#  Decision Analysis Core Copyright (C) 2026 Robert Kewley
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go

from decision_core import DecisionAnalysisResult


@dataclass(frozen=True)
class DecisionAnalysisStackedBarPlotter:
    y_axis_title: str = "Weighted Value"
    infeasible_label_prefix: str = "Infeasible"

    def build_figure(self, result: DecisionAnalysisResult) -> go.Figure:
        alternative_names_by_id = {
            alternative.id: alternative.name for alternative in result.decision_problem.alternatives
        }
        rows_by_alternative_id = {row.alternative_id: row for row in result.rows}
        alternative_ids = [alternative.id for alternative in result.decision_problem.alternatives]

        missing_rows = [
            alternative_id
            for alternative_id in alternative_ids
            if alternative_id not in rows_by_alternative_id
        ]
        if missing_rows:
            missing = ", ".join(missing_rows)
            raise ValueError(
                f"DecisionAnalysisResult rows are missing alternatives from the paired DecisionProblem: {missing}."
            )

        normalized_weights = result.total_value_model.normalized_weights()
        rule_by_id = {
            feasibility_rule.id: feasibility_rule
            for feasibility_rule in result.total_value_model.feasibility_rules
        }
        criterion_name_by_id = {
            criterion.id: criterion.name for criterion in result.decision_problem.criteria
        }
        infeasible_criteria_labels_by_alternative_id: dict[str, str] = {}

        for alternative_id in alternative_ids:
            row = rows_by_alternative_id[alternative_id]
            failed_criterion_names = sorted(
                {
                    criterion_name_by_id[rule_by_id[rule_id].criterion_id]
                    for rule_id, passed in row.feasibility_rule_results.items()
                    if not passed
                }
            )
            if failed_criterion_names:
                infeasible_criteria_labels_by_alternative_id[alternative_id] = ", ".join(
                    failed_criterion_names
                )

        figure = go.Figure()
        for criterion in result.decision_problem.criteria:
            criterion_id = criterion.id
            y_values = [
                0.0
                if alternative_id in infeasible_criteria_labels_by_alternative_id
                else max(
                    0.0,
                    min(
                        100.0,
                        rows_by_alternative_id[alternative_id].criterion_value_scores[criterion_id]
                        * normalized_weights[criterion_id],
                    ),
                )
                for alternative_id in alternative_ids
            ]
            figure.add_trace(
                go.Bar(
                    name=criterion.name,
                    x=[alternative_names_by_id[alternative_id] for alternative_id in alternative_ids],
                    y=y_values,
                )
            )

        infeasible_alternative_ids = [
            alternative_id
            for alternative_id in alternative_ids
            if alternative_id in infeasible_criteria_labels_by_alternative_id
        ]
        if infeasible_alternative_ids:
            figure.add_trace(
                go.Scatter(
                    name=self.infeasible_label_prefix,
                    x=[
                        alternative_names_by_id[alternative_id]
                        for alternative_id in infeasible_alternative_ids
                    ],
                    y=[0.0] * len(infeasible_alternative_ids),
                    mode="markers+text",
                    marker={"symbol": "x", "size": 12, "color": "crimson"},
                    text=[
                        f"{self.infeasible_label_prefix}: "
                        f"{infeasible_criteria_labels_by_alternative_id[alternative_id]}"
                        for alternative_id in infeasible_alternative_ids
                    ],
                    textposition="top center",
                    hovertemplate="%{text}<extra></extra>",
                )
            )

        figure.update_layout(barmode="stack")
        figure.update_yaxes(range=[0, 100], title_text=self.y_axis_title)
        return figure
