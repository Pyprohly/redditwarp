
from __future__ import annotations
from typing import Any, Mapping

from ..flair import (
    Variant2FlairTemplate,
    Variant1FlairTemplate,
    FlairChoices,
    CurrentFlairChoice,
    FlairTemplateChoice,
    UserFlairAssociation,
)

def load_variant2_flair_template(d: Mapping[str, Any]) -> Variant2FlairTemplate:
    return Variant2FlairTemplate(d)

def load_variant1_flair_template(d: Mapping[str, Any]) -> Variant1FlairTemplate:
    return Variant1FlairTemplate(d)

def load_flair_choices(d: Mapping[str, Any]) -> FlairChoices:
    current_data = d['current']
    current = None
    if 'flair_template_id' in current_data or 'flair_text' in current_data:
        current = CurrentFlairChoice(current_data)

    choices_data = d['choices']
    choices = [FlairTemplateChoice(i) for i in choices_data]

    return FlairChoices(current, choices)

def load_user_flair_association(d: Mapping[str, Any]) -> UserFlairAssociation:
    return UserFlairAssociation(d)
