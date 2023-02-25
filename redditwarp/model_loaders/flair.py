
from __future__ import annotations
from typing import Any, Mapping, Optional

from ..models.flair import (
    FlairTemplate,
    FlairTemplateChoices,
    FlairTemplateChoice,
    UserFlairAssociation,
)

def load_variant1_flair_template(d: Mapping[str, Any]) -> FlairTemplate:
    return FlairTemplate(
        d=d,
        uuid=d['id'],
        text_mode=d['type'],
        text=d['text'],
        css_class=d['css_class'],
        bg_color=d['background_color'],
        fg_color_scheme=d['text_color'],
        mod_only=d['mod_only'],
        text_editable=d['text_editable'],
        allowable_content=d['allowable_content'],
        max_emojis=d['max_emojis'],
    )

def load_variant2_flair_template(d: Mapping[str, Any]) -> FlairTemplate:
    return FlairTemplate(
        d=d,
        uuid=d['id'],
        text_mode=d['type'],
        text=d['text'],
        css_class=d['cssClass'],
        bg_color=d['backgroundColor'],
        fg_color_scheme=d['textColor'],
        mod_only=d['modOnly'],
        text_editable=d['textEditable'],
        allowable_content=d['allowableContent'],
        max_emojis=d['maxEmojis'],
    )

def load_flair_template_choice(d: Mapping[str, Any]) -> FlairTemplateChoice:
    return FlairTemplateChoice(
        uuid=d['flair_template_id'],
        text=d['flair_text'],
        css_class=d['flair_css_class'],
        text_editable=d['flair_text_editable'],
    )

def load_flair_template_choices(d: Mapping[str, Any]) -> FlairTemplateChoices:
    choices_data = d['choices']
    choices = [load_flair_template_choice(m) for m in choices_data]
    return FlairTemplateChoices(
        choices=choices,
        subreddit_flair_user_position=d['current']['flair_position'],
    )

def load_user_flair_association(d: Mapping[str, Any]) -> UserFlairAssociation:
    flair_css_class: Optional[str] = d['flair_css_class']
    return UserFlairAssociation(
        user=d['user'],
        text=d['flair_text'],
        css_class=flair_css_class or '',
        has_had_flair_css_class_assigned_before_in_subreddit_when_no_flair_template_assigned=flair_css_class is not None,
    )
