
from typing import Any, Mapping, Optional, NamedTuple, Sequence

from .artifact import Artifact

class FlairTemplate(Artifact):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self._from_dict(d)

    def _from_dict(self, d: Mapping[str, Any]) -> None:
        raise NotImplementedError
        self.uuid: str = ''
        self.type: str = ''
        self.mod_only: bool = False
        self.text: str = ''
        self.bg_color: str = ''
        self.text_color: str = ''
        self.allowable_content: str = ''
        self.css_class: str = ''
        self.max_emojis: int = 0
        self.text_editable: bool = False
        self.override_css: bool = False

class Variant1FlairTemplate(FlairTemplate):
    def _from_dict(self, d: Mapping[str, Any]) -> None:
        self.uuid: str = d['id']
        self.type: str = d['type']
        self.mod_only: bool = d['mod_only']
        self.text: str = d['text']
        self.bg_color: str = d['background_color']
        self.text_color: str = d['text_color']
        self.allowable_content: str = d['allowable_content']
        self.css_class: str = d['css_class']
        self.max_emojis: int = d['max_emojis']
        self.text_editable: bool = d['text_editable']
        self.override_css: bool = d['override_css']

class Variant2FlairTemplate(FlairTemplate):
    def _from_dict(self, d: Mapping[str, Any]) -> None:
        self.uuid: str = d['id']
        self.type: str = d['type']
        self.mod_only: bool = d['modOnly']
        self.text: str = d['text']
        self.bg_color: str = d['backgroundColor']
        self.text_color: str = d['textColor']
        self.allowable_content: str = d['allowableContent']
        self.css_class: str = d['cssClass']
        self.max_emojis: int = d['maxEmojis']
        self.text_editable: bool = d['textEditable']
        self.override_css: bool = d['overrideCss']


class CurrentFlairChoice:
    def __init__(self, d: Mapping[str, Any]):
        self.uuid: Optional[str] = d['flair_template_id']
        self.text: str = d['flair_text']
        self.css_class: str = d['flair_css_class']
        self.position: str = d['flair_position']

class FlairTemplateChoice:
    def __init__(self, d: Mapping[str, Any]):
        self.uuid: str = d['flair_template_id']
        self.text: str = d['flair_text']
        self.css_class: str = d['flair_css_class']
        self.position: str = d['flair_position']
        self.text_editable: bool = d['flair_text_editable']

class FlairChoices(NamedTuple):
    current: Optional[CurrentFlairChoice]
    choices: Sequence[FlairTemplateChoice]


class UserFlairAssociation:
    def __init__(self, d: Mapping[str, Any]):
        self.username: str = d['user']
        self.text: str = d['flair_text']
        flair_css_class_temp: Optional[str] = d['flair_css_class']
        self.has_had_css_class_when_no_flair_template: bool = flair_css_class_temp is not None
        self.css_class: str = flair_css_class_temp or ''
