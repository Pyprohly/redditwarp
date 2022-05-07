
from __future__ import annotations
from typing import Any, Mapping, Optional

from ..models.flair import (
    FlairTemplate,
    FlairChoices,
    CurrentFlairChoice,
    FlairTemplateChoice,
    UserFlairAssociation,
)

def load_variant1_flair_template(d: Mapping[str, Any]) -> FlairTemplate:
    return FlairTemplate(
        d=d,
        uuid=d['id'],
        type=d['type'],
        mod_only=d['mod_only'],
        text=d['text'],
        bg_color=d['background_color'],
        fg_light_or_dark=d['text_color'],
        allowable_content=d['allowable_content'],
        css_class=d['css_class'],
        max_emojis=d['max_emojis'],
        text_editable=d['text_editable'],
    )

def load_variant2_flair_template(d: Mapping[str, Any]) -> FlairTemplate:
    return FlairTemplate(
        d=d,
        uuid=d['id'],
        type=d['type'],
        mod_only=d['modOnly'],
        text=d['text'],
        bg_color=d['backgroundColor'],
        fg_light_or_dark=d['textColor'],
        allowable_content=d['allowableContent'],
        css_class=d['cssClass'],
        max_emojis=d['maxEmojis'],
        text_editable=d['textEditable'],
    )

def load_flair_template_choice(d: Mapping[str, Any]) -> FlairTemplateChoice:
    return FlairTemplateChoice(
        uuid=d['flair_template_id'],
        text=d['flair_text'],
        css_class=d['flair_css_class'],
        position=d['flair_position'],
        text_editable=d['flair_text_editable'],
    )

def load_current_flair_choice(d: Mapping[str, Any]) -> CurrentFlairChoice:
    return CurrentFlairChoice(
        uuid=d['flair_template_id'],
        text=d['flair_text'],
        css_class=d['flair_css_class'],
        position=d['flair_position'],
    )

def load_flair_choices(d: Mapping[str, Any]) -> FlairChoices:
    current_data = d['current']
    current = None
    if 'flair_template_id' in current_data or 'flair_text' in current_data:
        current = load_current_flair_choice(current_data)

    choices_data = d['choices']
    choices = [load_flair_template_choice(m) for m in choices_data]

    return FlairChoices(current, choices)

def load_user_flair_association(d: Mapping[str, Any]) -> UserFlairAssociation:
    flair_css_class_temp: Optional[str] = d['flair_css_class']
    return UserFlairAssociation(
        username=d['user'],
        text=d['flair_text'],
        has_had_css_class_when_no_flair_template=flair_css_class_temp is not None,
        css_class=flair_css_class_temp or '',
    )
